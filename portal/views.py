import os, re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Request, Category
from .forms import RequestForm, AdminStatusForm, RegisterForm, CategoryForm
from django.utils import timezone


def index(request):
    completed_requests = (Request.objects.filter(status='done').order_by('-edit_date')[:4])
    in_progress_count = Request.objects.filter(status='in_progress').count()

    return render(request, 'home.html', {
        'completed_requests': completed_requests,
        'in_progress_count': in_progress_count,
    })


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Неверный логин или пароль.')
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        form_data = {
            'full_name': request.POST.get('full_name', '').strip(),
            'username': request.POST.get('username', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'password': request.POST.get('password'),
            'confirm_password': request.POST.get('confirm_password'),
            'agree': 'agree' in request.POST,
        }

        errors = []

        if not form_data['full_name']:
            errors.append("ФИО обязательно.")
        elif not re.fullmatch(r'[а-яА-ЯёЁ\s\-]+', form_data['full_name']):
            errors.append("ФИО должно содержать только кириллицу, пробелы и дефис.")


        if not form_data['username']:
            errors.append("Логин обязателен.")
        elif not re.fullmatch(r'^[a-zA-Z\-]+$', form_data['username']):
            errors.append("Логин может содержать только латинские буквы и дефис.")
        elif User.objects.filter(username=form_data['username']).exists():
            errors.append("Этот логин уже занят.")


        if not form_data['email']:
            errors.append("Email обязателен.")
        elif '@' not in form_data['email'] or '.' not in form_data['email']:
            errors.append("Некорректный email.")


        if not form_data['password']:
            errors.append("Пароль обязателен.")
        elif len(form_data['password']) < 6:
            errors.append("Пароль должен быть не менее 6 символов.")
        elif form_data['password'] != form_data['confirm_password']:
            errors.append("Пароли не совпадают.")


        if not form_data['agree']:
            errors.append("Требуется согласие на обработку данных.")


        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'register.html')


        try:
            user = User.objects.create_user(
                username=form_data['username'],
                email=form_data['email'],
                password=form_data['password']
            )
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')
            login(request, user)
            return redirect('index')
        except Exception as e:
            messages.error(request, 'Произошла ошибка при регистрации. Попробуйте снова.')
            return render(request, 'register.html')

    return render(request, 'register.html')


def user_logout(request):
    logout(request)
    return redirect('index')


@login_required
def user_requests(request):
    status_filter = request.GET.get('status', '')
    if status_filter:
        requests = Request.objects.filter(user=request.user, status=status_filter).order_by('-created_at')
    else:
        requests = Request.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'user_requests.html', {
        'requests': requests,
        'current_status': status_filter,
    })


@login_required
def create_request(request):
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save(commit=False)
            req.user = request.user
            req.edit_date = timezone.now()
            req.save()
            formats = ['.png', '.jpg', '.jpeg']
            format_to_check = os.path.splitext(req.photo.name)[1].lower()
            if format_to_check not in formats:
                messages.error(request, 'Файл не подходит по формату.')
                return render(request, 'create_request.html', {'form': form})

            if req.photo.size > 2 * 1024 * 1024:
                messages.error(request, 'Файл слишком большой (более 2 Мб).')
            else:
                req.save()
                messages.success(request, 'Заявка успешно создана!')
                return redirect('user_requests')
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RequestForm()

    return render(request, 'create_request.html', {'form': form})


@login_required
def delete_request(request, req_id):
    req = get_object_or_404(Request, id=req_id, user=request.user)

    if req.status != 'new':
        messages.error(request, 'Удалить можно только заявку со статусом "Новая".')
        return redirect('user_requests')

    if request.method == 'POST':
        req.delete()
        messages.success(request, 'Заявка удалена.')
        return redirect('user_requests')

    return render(request, 'confirm_delete.html', {'req': req})


def is_admin(user):
    return user.is_authenticated and user.username == 'admin'


@user_passes_test(is_admin)
def admin_dashboard(request):
    requests = Request.objects.all().order_by('-created_at')
    categories = Category.objects.all()

    return render(request, 'admin_dashboard.html', {
        'requests': requests,
        'categories': categories,
    })



@user_passes_test(is_admin)
def change_status(request, req_id):
    req = get_object_or_404(Request, id=req_id)

    if req.status == 'done':
        messages.error(request, 'Нельзя изменить статус у уже выполненной заявки.')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = AdminStatusForm(request.POST, request.FILES)
        if form.is_valid():
            new_status = form.cleaned_data['status']

            allowed_transitions = {
                'new': ['in_progress', 'done'],
                'in_progress': ['done'],
            }

            if new_status not in allowed_transitions.get(req.status, []):
                messages.error(request, f'Невозможно изменить статус с "{req.get_status_display()}" на выбранный.')
                return render(request, 'change_status.html', {'form': form, 'request': req})

            req.status = new_status
            req.comment = form.cleaned_data['comment']

            if new_status == 'done':
                req.design_image = form.cleaned_data['design_image']


            req.edit_date = timezone.now()
            req.save()

            messages.success(request, 'Статус успешно обновлён.')
            return redirect('admin_dashboard')
    else:
        form = AdminStatusForm()

    return render(request, 'change_status.html', {
        'form': form,
        'request': req,
    })


@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория добавлена.')
        else:
            for field in form.errors:
                for error in form.errors[field]:
                    messages.error(request, f"Категория: {error}")
    return redirect('admin_dashboard')


@user_passes_test(is_admin)
def delete_category(request, cat_id):
    cat = get_object_or_404(Category, id=cat_id)
    cat.delete()
    messages.success(request, 'Категория и все заявки удалены.')
    return redirect('admin_dashboard')
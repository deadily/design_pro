import os

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Request
from .forms import RequestForm
import re


def index(request):
    return render(request, 'home.html')


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
    requests = Request.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'user_requests.html', {'requests': requests})

@login_required
def create_request(request):
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save(commit=False)
            req.user = request.user
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
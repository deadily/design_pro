from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


def index(request):
    """Главная страница"""
    return render(request, 'home.html')


def user_login(request):
    """Вход по логину и паролю"""
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
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form_data = {
            'full_name': request.POST.get('full_name', '').strip(),
            'username': request.POST.get('username', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'password': request.POST.get('password'),
            'confirm_password': request.POST.get('confirm_password'),
            'agree': 'agree' in request.POST,
        }

        # Валидация
        errors = []

        if not form_data['full_name']:
            errors.append("ФИО обязательно.")
        elif not all(c.isalpha() or c in ' -' for c in form_data['full_name']):
            errors.append("ФИО: только кириллица, пробелы и дефис.")

        if not form_data['username']:
            errors.append("Логин обязателен.")
        elif not all(c.isalpha() or c == '-' for c in form_data['username']):
            errors.append("Логин: только латиница и дефис.")
        elif User.objects.filter(username=form_data['username']).exists():
            errors.append("Этот логин уже занят.")

        if not form_data['email']:
            errors.append("Email обязателен.")
        elif '@' not in form_data['email']:
            errors.append("Некорректный email.")

        if not form_data['password']:
            errors.append("Пароль обязателен.")
        elif form_data['password'] != form_data['confirm_password']:
            errors.append("Пароли не совпадают.")

        if not form_data['agree']:
            errors.append("Требуется согласие на обработку данных.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'register.html')

        # Создание пользователя
        user = User.objects.create_user(
            username=form_data['username'],
            email=form_data['email'],
            password=form_data['password']
        )
        messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')
        login(request, user)
        return redirect('index')

    return render(request, 'register.html')


def user_logout(request):
    logout(request)
    return redirect('index')
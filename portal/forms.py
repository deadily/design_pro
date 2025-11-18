import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class RegisterForm(forms.Form):
    full_name = forms.CharField(max_length=150, label="ФИО")
    username = forms.CharField(max_length=150, label="Логин")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Повтор пароля")
    agree = forms.BooleanField(label="Согласие на обработку персональных данных")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        if not all(c.isalpha() or c == '-' for c in username):
            raise forms.ValidationError("Только латиница и дефис.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Логин уже занят.")
        return username

    def clean_full_name(self):
        full_name = self.cleaned_data['full_name']
        if not all(c.isalpha() or c in ' -' for c in full_name):
            raise forms.ValidationError("ФИО — только кириллица, пробелы и дефис.")
        return full_name

from .models import Request

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'description', 'photo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'photo': 'Фото или план помещения (JPG, PNG, до 2 Мб)',
        }
import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Request, Category


class RegisterForm(forms.Form):
    full_name = forms.CharField(max_length=150, label="ФИО")
    username = forms.CharField(max_length=150, label="Логин")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Повтор пароля")
    agree = forms.BooleanField(label="Согласие на обработку персональных данных", required=True)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают.")

        if len(password) < 6:
            raise forms.ValidationError("Пароль должен быть не менее 6 символов.")

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username'].strip()

        if not username:
            raise forms.ValidationError("Логин обязателен.")

        if not re.fullmatch(r'^[a-zA-Z\-]+$', username):
            raise forms.ValidationError("Логин может содержать только латинские буквы и дефис.")

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Этот логин уже занят.")

        return username

    def clean_full_name(self):
        full_name = self.cleaned_data['full_name'].strip()

        if not full_name:
            raise forms.ValidationError("ФИО обязательно для заполнения.")

        if not re.fullmatch(r'^[а-яА-ЯёЁ\s\-]+$', full_name):
            raise forms.ValidationError("ФИО должно содержать только буквы кириллицы, пробелы и дефис.")

        return full_name


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'description', 'category', 'photo']  # Добавлено 'category'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'category': 'Категория',
            'photo': 'Фото или план помещения (JPG, JPEG, PNG, до 2 Мб)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        self.fields['category'].empty_label = "Выберите категорию"
        self.fields['category'].required = True



class AdminStatusForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('in_progress', 'Принято в работу'), ('done', 'Выполнено')],
        label="Новый статус"
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label="Комментарий",
        required=False
    )
    design_image = forms.ImageField(
        required=False,
        label="Дизайн (для статуса 'Выполнено')"
    )

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        comment = cleaned_data.get('comment')
        design_image = cleaned_data.get('design_image')

        if status == 'in_progress':
            if not comment or not comment.strip():
                self.add_error('comment', 'Комментарий обязателен при переводе в статус "Принято в работу".')

        if status == 'done':
            if not design_image:
                self.add_error('design_image', 'Для статуса "Выполнено" обязательно прикрепить изображение дизайна.')

        return cleaned_data

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {'name': 'Название категории'}
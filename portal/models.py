from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")

    def __str__(self):
        return self.name


class Request(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'Принято в работу'),
        ('done', 'Выполнено'),
    ]

    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Категория")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    photo = models.ImageField(upload_to='request_photos/', verbose_name="Фото помещения")
    design_image = models.ImageField(upload_to='designs/', null=True, blank=True, verbose_name="Дизайн")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    edit_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата изменения статуса")

    def __str__(self):
        return self.title
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    '''модель пользователя'''
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField('Email',
                              max_length=200,
                              unique=True,)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)

    class Meta:
        ordering = ['id', ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

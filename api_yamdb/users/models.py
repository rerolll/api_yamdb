import random

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models


class UserRoles(models.TextChoices):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Никнейм', max_length=150,
        unique=True, validators=[
            RegexValidator(
                r'^[\w.@+-]+\Z',
                'В никнейме допустимы только цифры, буквы и символы @/./+/-/_'
            )
        ]
    )
    email = models.EmailField(
        verbose_name='Электронная почта', max_length=254, unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя', max_length=150, blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия', max_length=150, blank=True
    )
    role = models.CharField(
        verbose_name='Роль', choices=UserRoles.choices,
        default=UserRoles.USER, max_length=20
    )
    bio = models.CharField(verbose_name='Био', blank=True, max_length=200)
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения', max_length=15, blank=True, null=True
    )

    def generate_confirmation_code(self):
        code = ''.join(random.choices('0123456789', k=15))
        self.confirmation_code = code
        self.send_confirmation_email(code)

    def send_confirmation_email(self, code):
        subject = 'Your confirmation code'
        message = f'Ваш код подтверждения: {code}'
        from_email = 'confirmation@api_yamdb.com'
        recipient_list = [self.email]
        send_mail(
            subject, message, from_email, recipient_list, fail_silently=True
        )

    def save(self, *args, **kwargs):
        if self.username == 'me':
            raise ValidationError("Никнейм 'me' не допустим.")

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

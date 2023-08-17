import random

from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models

from .validators import validate_username


class UserRoles(models.TextChoices):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class User(AbstractUser):
    username = models.CharField(
        verbose_name="Никнейм",
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                r"^[\w.@+-]+\Z",
                "В никнейме допустимы только цифры, буквы и символы @/./+/-/_",
            ),
            validate_username,
        ],
    )
    email = models.EmailField(
        verbose_name="Электронная почта", max_length=254, unique=True
    )
    first_name = models.CharField(
        verbose_name="Имя", max_length=150, blank=True
    )
    last_name = models.CharField(
        verbose_name="Фамилия", max_length=150, blank=True
    )
    role = models.CharField(
        verbose_name="Роль",
        choices=UserRoles.choices,
        default=UserRoles.USER,
        max_length=20,
    )
    bio = models.TextField(verbose_name="Био", blank=True)
    confirmation_code = models.CharField(
        verbose_name="Код подтверждения", max_length=15, blank=True, null=True
    )

    def generate_confirmation_code(self):
        code = "".join(random.choices("0123456789", k=15))
        self.confirmation_code = code
        self.send_confirmation_email(code)

    def generate_confirmation_code_no_email(self):
        code = "".join(random.choices("0123456789", k=15))
        self.confirmation_code = code

    def send_confirmation_email(self, code):
        subject = "Your confirmation code"
        message = f"Ваш код подтверждения: {code}"
        from_email = "confirmation@api_yamdb.com"
        recipient_list = [self.email]
        send_mail(
            subject, message, from_email, recipient_list, fail_silently=True
        )

    def check_confirmation_code(self, confirmation_code):
        if self.confrimation_code == confirmation_code:
            return True


    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "Пользователи"

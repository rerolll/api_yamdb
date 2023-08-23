from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
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

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "Пользователи"

    def generate_confirmation_code(self):
        code = default_token_generator.make_token(self)
        self.confirmation_code = code[:15]
        self.send_confirmation_email(self.confirmation_code)

    def generate_confirmation_code_no_email(self):
        code = default_token_generator.make_token(self)
        self.confirmation_code = code[:15]

    def send_confirmation_email(self, code):
        subject = "Your confirmation code"
        message = f"Ваш код подтверждения: {code}"
        from_email = "confirmation@api_yamdb.com"
        recipient_list = [self.email]
        send_mail(
            subject, message, from_email, recipient_list, fail_silently=True
        )

    def check_confirmation_code(self, code):
        return self.confirmation_code == code

    @property
    def is_admin(self):
        return self.role == UserRoles.ADMIN

    @property
    def is_admin_or_staff(self):
        if self.is_staff or self.role == UserRoles.ADMIN:
            return True

    @property
    def is_admin_or_staff_or_mod(self):
        if (
            self.is_staff or self.role == UserRoles.ADMIN
            or self.role == UserRoles.MODERATOR
        ):
            return True

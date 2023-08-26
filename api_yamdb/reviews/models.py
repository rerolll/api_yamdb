from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

User = get_user_model()


class CategoryGenreBase(models.Model):
    name = models.CharField(verbose_name="Название", max_length=256)
    slug = models.SlugField(
        verbose_name="Уникальный слаг", max_length=50, unique=True
    )

    class Meta:
        abstract = True
        ordering = ("name",)

    def __str__(self):
        return self.name


class Category(CategoryGenreBase):
    class Meta(CategoryGenreBase.Meta):
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Genre(CategoryGenreBase):
    class Meta(CategoryGenreBase.Meta):
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Title(models.Model):
    name = models.CharField(verbose_name="Название", max_length=256)
    year = models.PositiveSmallIntegerField(verbose_name="Дата выхода")
    rating = models.PositiveSmallIntegerField(
        verbose_name="Рейтинг", null=True, default=None
    )
    description = models.TextField(
        verbose_name="Описание", null=True, blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name="Жанр",
        related_name="titles",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.SET_NULL,
        related_name="titles",
        null=True,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name

    def clean(self):
        if self.year > timezone.now().year:
            raise ValidationError("Year can't be in the future.")


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str(self.id)


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name="reviews"
    )
    text = models.TextField(verbose_name="text field")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    score = models.PositiveSmallIntegerField(
        verbose_name="Score",
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    pub_date = models.DateTimeField("Pub-date", auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_author_review"
            )
        ]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField(verbose_name="text_field")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"
    )
    pub_date = models.DateTimeField("Pub-date_", auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

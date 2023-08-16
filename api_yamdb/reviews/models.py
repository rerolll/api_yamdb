from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import forms
from django.utils import timezone


class CategoryGenreBase(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.slug


class Category(CategoryGenreBase):
    class Meta(CategoryGenreBase.Meta):
        verbose_name = "Категория"


class Genre(CategoryGenreBase):
    class Meta(CategoryGenreBase.Meta):
        verbose_name = "Жанр"


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(
        Genre,
        related_name="titles",
    )
    category = models.ForeignKey(
        Category,
        models.SET_NULL,
        related_name="titles",
        null=True,
    )

    def __str__(self):
        return self.name

    def clean(self):
        if self.year > timezone.now().year:
            raise ValidationError("Year can't be in the future.")


User = get_user_model()


class Review(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField(verbose_name='text field')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    score = models.PositiveSmallIntegerField(verbose_name='Score', null=True,
                                             validators=[MinValueValidator(1), MaxValueValidator(10)],)
    pub_date = models.DateTimeField('Pub-date', auto_now_add=True)
    
    
class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(verbose_name='text_field')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    pub_date = models.DateTimeField('Pub-date_', auto_now_add=True)

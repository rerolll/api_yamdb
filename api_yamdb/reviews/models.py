from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class CategoryGenreBase(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.slug


class Categories(CategoryGenreBase):
    class Meta(CategoryGenreBase.Meta):
        verbose_name = "Категория"


class Genres(CategoryGenreBase):
    class Meta(CategoryGenreBase.Meta):
        verbose_name = "Жанр"


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(
        Genres,
        related_name="title",
    )
    category = models.ForeignKey(
        Categories,
        models.SET_NULL,
        related_name="categories",
        null=True
    )

    def __str__(self):
        return self.name

    def clean(self):
        if self.year > timezone.now().year:
            raise ValidationError("Year can't be in the future.")

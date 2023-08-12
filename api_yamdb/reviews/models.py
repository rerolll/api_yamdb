from django.db import models


class CategoryGenreBase(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.slug


class Category(CategoryGenreBase):

    class Meta(CategoryGenreBase.Meta):
        verbose_name = 'Категория'


class Genre(CategoryGenreBase):

    class Meta(CategoryGenreBase.Meta):
        verbose_name = 'Жанр'


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()  #validator
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='title',
    )
    category = models.ForeignKey(
        Category,
        models.SET_NULL,
        null=True,
        blank=True,
        related_name='category',
    )

    def __str__(self):
        return self.name

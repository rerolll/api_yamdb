from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination

from reviews.models import Categories, Genres, Title

from .filters import TitlesFilter
from .permissions import IsAdmin, IsAuthorOrModeratorOrReadOnly, ReadOnly
from .serializers import CategorySerializer, GenreSerializer, TitleSerializer
from .viewsets import CreateListDestroyViewSet


class CategoriesGenresViewSet(CreateListDestroyViewSet):
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter,)
    search_fields = ("name",)
    permission_classes = (IsAdmin | ReadOnly,)
    lookup_field = "slug"


class CategoryViewSet(CategoriesGenresViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoriesGenresViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdmin | IsAuthorOrModeratorOrReadOnly,)
    ordering_fields = ("name",)
    filterset_class = TitlesFilter

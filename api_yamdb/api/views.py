from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotFound,
    PermissionDenied
)
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from reviews.models import Category, Genre, Review, Title
from users.models import User

from .filters import TitlesFilter
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorOrAdminOrModeratorOrReadOnly
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewsSerializer,
    TitleSerializer,
    TitleSerializerGet,
    UserBasicSerializer,
    UserCreateSerializer,
    UserRetrieveUpdateDestroySerializer,
    UserRetrieveUpdateSerializer
)
from .viewsets import CreateListDestroyViewSet

User = get_user_model()


class BasicUserCreateView(generics.CreateAPIView):
    def perform_create(self, serializer):
        user = serializer.save()
        user.generate_confirmation_code()
        user.save()


class BasicUserUpdateView(generics.RetrieveUpdateDestroyAPIView):
    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class UserCreateView(BasicUserCreateView):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get("username")
        email = request.data.get("email")
        try:
            existing_user = User.objects.get(username=username, email=email)
            existing_user.generate_confirmation_code()
            existing_user.save()
            response_data = {
                "detail": """User already exists.
                             New confirmation code has been sent."""
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            pass

        response = super().create(request, *args, **kwargs)
        response.status_code = 200
        return response


class UserListCreateView(generics.CreateAPIView, ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserRetrieveUpdateDestroySerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    pagination_class = PageNumberPagination
    search_fields = ("username",)

    def perform_create(self, serializer):
        user = serializer.save()
        user.generate_confirmation_code_no_email()
        user.save()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserBasicSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except PermissionDenied:
            raise PermissionDenied("Нет прав доступа")
        except AuthenticationFailed:
            raise AuthenticationFailed("Необходим JWT-токен")

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except PermissionDenied:
            raise PermissionDenied("Нет прав доступа")
        except AuthenticationFailed:
            raise AuthenticationFailed("Необходим JWT-токен")


class UserRetrieveUpdateDestroyView(
    generics.RetrieveDestroyAPIView, BasicUserUpdateView
):
    serializer_class = UserRetrieveUpdateDestroySerializer
    permission_classes = (IsAdmin,)
    queryset = User.objects.all()

    def get_object(self):
        username = self.kwargs.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound("Пользователь не найден")
        except PermissionDenied:
            raise PermissionDenied("Нет прав доступа")
        except AuthenticationFailed:
            raise AuthenticationFailed("Необходим JWT-токен")
        return user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response(
            {"message": "Удачное выполнение запроса"},
            status=status.HTTP_204_NO_CONTENT,
        )

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Метод не разрешён"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRetrieveUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        confirmation_code = request.data.get("confirmation_code")
        username = request.data.get("username")
        if confirmation_code is None or username is None:
            return Response(
                {
                    "error": (
                        "Отсутствует обязательное поле или оно некорректно."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound("Пользователь не найден")
        serializer = self.get_serializer(data=request.data)
        if not user.check_confirmation_code(confirmation_code):
            return Response(
                {"error": "Некорректный код подтверждения"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if serializer.is_valid():
            token = serializer.validated_data.get("access")
            refresh_token = serializer.validated_data.get("refresh")
            response_data = {
                "ID пользователя": user.id,
                "token": str(token),
                "Обновление токена": str(refresh_token),
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryGenreViewSet(CreateListDestroyViewSet):
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter,)
    search_fields = ("name",)
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = "slug"


class CategoryViewSet(CategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(CategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects.all().annotate(Avg("reviews__score")).order_by("name")
    )
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TitleSerializerGet
        return TitleSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    permission_classes = (IsAuthorOrAdminOrModeratorOrReadOnly,)

    def get_queryset(self):
        title = self.get_title()
        queryset = Review.objects.filter(title=title)
        return queryset

    def get_title(self):
        title_id = self.kwargs.get("title_id")
        return get_object_or_404(Title, pk=title_id)

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrAdminOrModeratorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            title_id=self.kwargs.get("title_id"),
            pk=self.kwargs.get("review_id"),
        )
        return review.comments.all().order_by("id")

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            title_id=self.kwargs.get("title_id"),
            pk=self.kwargs.get("review_id"),
        )
        serializer.save(author=self.request.user, review=review)

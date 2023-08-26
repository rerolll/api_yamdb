from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotFound,
    PermissionDenied,
)
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView

from reviews.models import Category, Genre, Review, Title
from users.models import User

from .filters import TitlesFilter
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorOrAdminOrModeratorOrReadOnly,
)
from .serializers import (
    UserBasicSerializer,
    CategorySerializer,
    CommentSerializer,
    CustomTokenObtainPairSerializer,
    GenreSerializer,
    ReviewsSerializer,
    TitleSerializer,
    TitleSerializerGet,
    UserCreateSerializer,
    UserRetrieveUpdateSerializer,
)
from .viewsets import CreateListDestroyViewSet

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserBasicSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    pagination_class = PageNumberPagination
    search_fields = ("username",)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'delete', 'patch']

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

    def perform_create(self, serializer):
        user = serializer.save()
        user.generate_confirmation_code_no_email()
        user.save()

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

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response(
            {"message": "Удачное выполнение запроса"},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=False, methods=[
        'get', 'post', 'patch', 'delete', 'put'
    ], permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method == 'DELETE':
            return Response(
                {"detail": "Метод не разрешён"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        if request.method == 'PUT':
            return Response(
                {"detail": "Метод не разрешён"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        user = request.user
        serializer = UserRetrieveUpdateSerializer(
            user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreateView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.generate_confirmation_code()
        user.save()

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


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        access_token = AccessToken.for_user(user)
        response_data = {
            "token": str(access_token),
        }
        return Response(response_data, status=status.HTTP_200_OK)


class CategoryGenreViewSet(CreateListDestroyViewSet):
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
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TitleSerializerGet
        return TitleSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    permission_classes = (IsAuthorOrAdminOrModeratorOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        title = self.get_title()
        queryset = title.reviews.all()
        return queryset

    def get_title(self):
        title_id = self.kwargs.get("title_id")
        return get_object_or_404(Title, pk=title_id)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs["title_id"])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrAdminOrModeratorOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

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

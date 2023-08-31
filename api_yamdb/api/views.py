from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
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
    IsAuthorOrAdminOrModeratorOrReadOnly
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
    # def get_object(self):
    #     username = self.kwargs.get("username")
    #     return get_object_or_404(User, username=username)
    # def perform_create(self, serializer):
    #     user = serializer.save()
    #     user.generate_confirmation_code_no_email()
    #     user.save()
    # def delete(self, request, *args, **kwargs):
    #     user = self.get_object()
    #     user.delete()
    #     return Response(
    #         {"message": "Удачное выполнение запроса"},
    #         status=status.HTTP_204_NO_CONTENT,
    #     )

    @action(methods=['GET', 'PATCH'], detail=False,
            permission_classes=(IsAuthenticated,), url_path='me')
    def me(self, request):
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
                "email": email,
                "username": username
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            pass

        response = super().create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
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
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TitleSerializerGet
        return TitleSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    permission_classes = (IsAuthorOrAdminOrModeratorOrReadOnly,)
    http_method_names = ["get", "post", "patch", "delete"]

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrAdminOrModeratorOrReadOnly,)
    http_method_names = ["get", "post", "patch", "delete"]

    def get_review(self):
        title_id = self.kwargs.get("title_id")
        review_id = self.kwargs.get("review_id")

        review = get_object_or_404(Review, id=review_id, title__id=title_id)
        return review

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

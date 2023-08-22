from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        ]

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except ValidationError:
            return Response(
                {
                    "error": (
                        "Отсутствует обязательное поле или оно не корректно"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserCreateSerializer(UserBasicSerializer):
    class Meta:
        model = User
        fields = ["email", "username"]


class UserRetrieveUpdateSerializer(UserBasicSerializer):
    role = serializers.ReadOnlyField()


class UserRetrieveUpdateDestroySerializer(UserBasicSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "role",
            "first_name",
            "last_name",
            "bio",
        ]


class CustomTokenObtainPairSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)

    def validate(self, attrs):
        confirmation_code = attrs.get("confirmation_code")
        username = attrs.get("username")
        if confirmation_code and username:
            try:
                User.objects.get(
                    confirmation_code=confirmation_code, username=username
                )
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "Неверные данные для выдачи токена."
                )
        return attrs


class CategorySerializer(serializers.ModelSerializer):
    lookup_field = "slug"

    class Meta:
        fields = ("name", "slug")
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    lookup_field = "slug"

    class Meta:
        fields = ("name", "slug")
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True, slug_field="slug", queryset=Genre.objects.all()
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = [
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        ]
        model = Title


class TitleSerializerGet(TitleSerializer):
    rating = serializers.IntegerField(
        source="reviews__score__avg", read_only=True
    )
    category = CategorySerializer()
    genre = GenreSerializer(many=True, read_only=True)


class ReviewsSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        fields = "__all__"
        model = Review

    def validate(self, data):
        if self.context["request"].method == "PATCH":
            return data
        title = self.context["view"].kwargs["title_id"]
        author = self.context["request"].user
        if Review.objects.filter(author=author, title__id=title).exists():
            raise serializers.ValidationError(
                "Нельзя оставлять более одного ревью!"
            )
        return data


"""
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title')
            )
        ]
"""


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(slug_field="text", read_only=True)
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        # validators=[UniqueValidator(queryset=Comment.objects.all())]
    )

    class Meta:
        fields = "__all__"
        model = Comment

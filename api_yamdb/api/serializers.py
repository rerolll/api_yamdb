from rest_framework import serializers
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username']

    def create(self, validated_data):
        user = User(**validated_data)
        user.generate_confirmation_code()
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'bio']

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CustomTokenObtainPairSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)

    def validate(self, attrs):
        confirmation_code = attrs.get('confirmation_code')
        username = attrs.get('username')
        if confirmation_code and username:
            try:
                user = User.objects.get(
                    confirmation_code=confirmation_code, username=username
                )
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    'Неверные данные для выдачи токена.'
                )
        if user:
            refresh = RefreshToken.for_user(user)
            attrs['user'] = user
            attrs['access'] = str(refresh.access_token)
            attrs['refresh'] = str(refresh)
        return attrs

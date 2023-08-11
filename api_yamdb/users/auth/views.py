from django.core.mail import send_mail

from rest_framework import generics, status, mixins, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from .serializers import UserSerializer


class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate confirmation code and send email
        refresh = RefreshToken.for_user(user)
        user.confirmation_code = str(refresh.access_token)
        user.save()
        send_mail(
            fail_silently=True,
            subject='Confirmation Code',
            message=(
                'Thank you for registering with our service. '
                'Please use the following confirmation code '
                f'to activate your account: {user.confirmation_code}'
            ),
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def token_view():
    ...


class TokenViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    ...

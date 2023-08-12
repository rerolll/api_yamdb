from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import (
    UserCreateView, CustomTokenObtainPairView,
    UserUpdateView, UserListView
)

urlpatterns = [
    path(
        'auth/token/',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'auth/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path('auth/signup/', UserCreateView.as_view(), name='user-create'),
    path('users/me/', UserUpdateView.as_view(), name='user-update'),
    path('users/', UserListView.as_view(), name='user-list')
]

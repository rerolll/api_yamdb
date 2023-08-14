from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (CustomTokenObtainPairView, UserCreateView,
                    UserListCreateView, UserRetrieveUpdateDestroyView,
                    UserRetrieveUpdateView)
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, GenreViewSet, TitleViewSet


v1_router = DefaultRouter()
v1_router.register("categories", CategoryViewSet, basename="category")
v1_router.register("genres", GenreViewSet, basename="genre")
v1_router.register("titles", TitleViewSet, basename="title")


urlpatterns = [
    path("v1/", include(v1_router.urls)),
]
urlpatterns += [
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
    path('users/me/', UserRetrieveUpdateView.as_view(), name='user-update'),
    path('users/', UserListCreateView.as_view(), name='user-list'),
    path(
        'users/<username>/', UserRetrieveUpdateDestroyView.as_view(),
        name='user-retrieve-delete'
    )
]
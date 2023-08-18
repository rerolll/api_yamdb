from django.urls import include, path

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CategoryViewSet,
    CustomTokenObtainPairView,
    GenreViewSet,
    TitleViewSet,
    UserCreateView,
    UserListCreateView,
    UserRetrieveUpdateDestroyView,
    UserRetrieveUpdateView,
    ReviewsViewSet,
    CommentViewSet
)

v1_router = DefaultRouter()
v1_router.register('categories', CategoryViewSet, basename="category")
v1_router.register('genres', GenreViewSet, basename="genre")
v1_router.register('titles', TitleViewSet, basename="title")
v1_router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewsViewSet, basename='title-reviews')
v1_router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
                CommentViewSet, basename='review-comments')

urlpatterns = [
    path("", include(v1_router.urls)),
    path(
        "auth/token/",
        CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("auth/signup/", UserCreateView.as_view(), name="user-create"),
    path("users/me/", UserRetrieveUpdateView.as_view(), name="user-update"),
    path("users/", UserListCreateView.as_view(), name="user-list"),
    path(
        "users/<username>/",
        UserRetrieveUpdateDestroyView.as_view(),
        name="user-retrieve-delete",
    ),
]

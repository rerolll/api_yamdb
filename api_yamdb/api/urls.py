from django.urls import include, path

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CategoryViewSet,
    CommentViewSet,
    CustomTokenObtainPairView,
    GenreViewSet,
    ReviewsViewSet,
    TitleViewSet,
    UserCreateView,
    UserListCreateView,
    UserRetrieveUpdateDestroyView,
    UserRetrieveUpdateView
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("genres", GenreViewSet, basename="genre")
router.register("titles", TitleViewSet, basename="title")
router.register(
    r"titles/(?P<title_id>\d+)/reviews",
    ReviewsViewSet,
    basename="title-reviews",
)
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="review-comments",
)

urlpatterns = [
    path("", include(router.urls)),
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

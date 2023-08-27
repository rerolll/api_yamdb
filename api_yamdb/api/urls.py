from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewsViewSet,
    TitleViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
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
    path("auth/", include("users.auth.urls")),
]

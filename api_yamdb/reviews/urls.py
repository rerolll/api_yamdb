from django.urls import include, path

from rest_framework.routers import DefaultRouter

from reviews.views import ReviewsViewSet, CommentViewSet

router = DefaultRouter()

router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewsViewSet, basename='title-reviews')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments/',
                CommentViewSet, basename='review-comments')

urlpatterns = [

    path('v1/', include(router.urls)),
]
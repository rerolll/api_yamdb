from django.urls import path

from api.views import CustomTokenObtainPairView, UserCreateView

urlpatterns = [
    path(
        "token/",
        CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path("signup/", UserCreateView.as_view(), name="user-create"),
]

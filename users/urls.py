from django.urls import path, include
from .views import Login, SignUp, VerifyEmail, UserProfile

urlpatterns = [
    path('login/', Login.as_view(), name="login"),
    path('signup/', SignUp.as_view(), name='signup'),
    path('verify-email/', VerifyEmail.as_view(), name='verify-email'),
    path('profile/', UserProfile.as_view(), name='verify-email'),
]

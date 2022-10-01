from django.urls import path, include

urlpatterns = [
    # path('auth/', include('dj_rest_auth.urls')),
    # path('auth/signup', include('dj_rest_auth.registration.urls')),
    path('', include('users.urls')),
    path('', include('social_auth.urls'), name="social-auth")
]

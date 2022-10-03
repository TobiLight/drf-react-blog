from dotenv import dotenv_values
from rest_framework.generics import views
from rest_framework.response import Response
from users.models import User
from .serializers import GoogleSocialAuthSerializer, TokenSerializer
from rest_framework import status, serializers
from urllib.parse import urlencode
from .services import get_google_token, google_get_user_info
from rest_framework_simplejwt.tokens import RefreshToken
import json

class GoogleLoginView(views.APIView):
    serializer_class = GoogleSocialAuthSerializer
    
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)
    
    def get(self, request):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get('code')
        error = validated_data.get('error')


        if error or not code:
            params = urlencode({'error': error})
            return Response('An error has occured!', status=status.HTTP_400_BAD_REQUEST)

        # domain = settings.BASE_BACKEND_URL
        # api_uri = reverse('api:login:google')
        redirect_uri = 'http://localhost:8000/api/login/google/'
        
        token = get_google_token(code=code, redirect_url=redirect_uri)

        user_data = google_get_user_info(access_token=token["access_token"])
        
        name = user_data['name'].split(" ")
        username = f'{name[0][:4]}{name[1][:4]}'
        profile_data = {
            'email': user_data['email'],
            'username': username,
            "password": dotenv_values('.env')['SOCIAL_SECRET'],
            "auth_provider": 'google',
            "is_verified": True,
            "is_active": True
        }
        #  check if user exists
        user = User.objects.filter(email=profile_data['email'])
        # create token for the user 
        if token['access_token'] and user.exists() and user[0].is_active and not user[0].is_suspended:
            token_for_user = RefreshToken.for_user(user[0])
            token_for_user['username'] = user[0].username
            token_for_user['google_token_info'] = token
            
            return Response({
            "token": {
              "access": str(token_for_user.access_token),
              "refresh": str(token_for_user),
              "user_id": str(token_for_user["user_id"]),
              "username": str(token_for_user['username']),
              "jti": str(token_for_user["jti"]),
              "iat": str(token_for_user['iat']),
              "exp": str(token_for_user['exp']),
              "google_info": {
                  "token_type": str(token_for_user["google_token_info"]['token_type']),
                  "access_token": str(token_for_user["google_token_info"]['access_token']),
                  "refresh_token": str(token_for_user["google_token_info"]['refresh_token']),
                  "scope": str(token_for_user["google_token_info"]['scope']),
                  "id_token": str(token_for_user["google_token_info"]['id_token']),
                  "expires_in": str(token_for_user["google_token_info"]['expires_in']),
              }
            },
            "user": {
                "id": user[0].id ,
                "username": user[0].username,
                "email": user[0].email,
                "joined": user[0].created_at
            }
        })
                        
        user = User.objects.create_user(**profile_data)
        token_for_user = RefreshToken.for_user(user)
        token_for_user['username'] = user.username
        token_for_user['google_token_info'] = token
        
        return Response({
            "token": {
              "access": str(token_for_user.access_token),
              "refresh": str(token_for_user),
              "user_id": str(token_for_user["user_id"]),
              "username": str(token_for_user['username']),
              "jti": str(token_for_user["jti"]),
              "iat": str(token_for_user['iat']),
              "exp": str(token_for_user['exp']),
              "google_info": {
                  "token_type": str(token_for_user["google_token_info"]['token_type']),
                  "access_token": str(token_for_user["google_token_info"]['access_token']),
                  "refresh_token": str(token_for_user["google_token_info"]['refresh_token']),
                  "scope": str(token_for_user["google_token_info"]['scope']),
                  "id_token": str(token_for_user["google_token_info"]['id_token']),
                  "expires_in": str(token_for_user["google_token_info"]['expires_in']),
              }
            },
            "user": {
                "id": user.id ,
                "username": user.username,
                "email": user.email,
                "joined": user.created_at
            }
        })

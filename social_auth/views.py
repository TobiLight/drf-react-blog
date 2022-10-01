from dotenv import dotenv_values
from rest_framework.generics import views
from rest_framework.response import Response
from users.models import User
from .serializers import GoogleSocialAuthSerializer
from rest_framework import status, serializers
from urllib.parse import urlencode
from .services import get_google_token, google_get_user_info


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
        # token = Refre
        if user.exists():
            info = {
                **user,
                "custom_iss": "google",
            }
            return Response({
            "token": token,
            "user": {
                "id": user[0].id ,
                "username": user[0].username,
                "email": user[0].email,
                "joined": user[0].created_at
            }
        })
                        
        user = User.objects.create_user(**profile_data)
        
        return Response({
            "token": access_token,
            "user": {
                "id": user.id ,
                "username": user.username,
                "email": user.email,
                "joined": user.created_at
            }
        })

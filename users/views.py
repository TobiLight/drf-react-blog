import datetime
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.generics import GenericAPIView
from django.contrib.sites.shortcuts import get_current_site
from users.utils import Util
from .serializers import  LoginSerializer, SignupSerializer, UserProfileSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from django.urls import reverse
from dotenv import dotenv_values
import jwt
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth import authenticate

class SignUp(GenericAPIView):
    """
    User Registration page
    """
    serializer_class = SignupSerializer

    def post(self, request):
        user_input = request.data
        serialier = self.serializer_class(data=user_input)
        serialier.is_valid(raise_exception=True)
        serialier.save()
        user = User.objects.get(email=serialier.data['email'])
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relative_link = reverse('verify-email')
        absurl = 'http://' + current_site + relative_link + '?token=' + str(token)
        if user.email and user.username is None:
            email_body = f'Hi {user.email}, \n \nUse the link below to verify your account. \n\n{absurl}'
        else:
            email_body = f'Hi {user.username}, \n \nUse the link below to verify your account. \n\n{absurl}'
        data = {
            "domain": absurl,
            "email_body": email_body,
            "email_subject": "Verify your email",
            "from_email": dotenv_values('.env')['EMAIL_HOST_USERNAME'],
            "to_email": user.email
        }
        
        print(dotenv_values('.env')['EMAIL_HOST_PASSWORD'], data['to_email'])
        Util.send_email(data)
        return Response({"message": "Account created successfully!", "user": serialier.data}, status=status.HTTP_201_CREATED)

class VerifyEmail(GenericAPIView):
    """
    Email Verification page
    """
    def get(self, request):
        token = request.GET.get('token')
        User = get_user_model()
        if not token:
            return Response({"error": "Token is invalid!"})
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY,algorithms=['HS256'],verify=True)
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({"message": "Email verification successful!"})
        except jwt.ExpiredSignatureError:
            return Response({"error": f'Token has expired. Go to http://localhost:8000/resend-email-verification to resend email verification.'})
        except jwt.DecodeError:
            return Response({"error": f'An error occured while trying to verify your email! Go to http://localhost:8000/resend-email-verification to resend email verification'})
        return Response({'message': "Your email has already been verified! Please login."})
    
    
    
class Login(GenericAPIView):
    """
    User Registration page
    
    """
    serializer_class = LoginSerializer
   
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        
        if email is None or password is None:
            return Response({"error": "Please provide an email or password!"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(email=email, password=password)
        
        if not user:
            return Response({"error": "Invalid credentials!"}, status=status.HTTP_404_NOT_FOUND)
        
        token = RefreshToken.for_user(user).access_token
        token.set_exp(lifetime=datetime.timedelta(hours=3))
        print(token)
        return Response({"message": "Login successful!", "token": str(token)}, status=status.HTTP_200_OK)
        

class ResendVerificationEmail(GenericAPIView):
    """
    Resend Email Verification if token has expired
    """
    
    def get(self, request):
        return Response({"message": "Send post request"})
    
    # def post(self, request):
        


class UserProfile(GenericAPIView):
    """
    User Profile Page
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        User = get_user_model()
        token = request.headers['Authorization'].split()[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY,algorithms=['HS256'],verify=True)
            user = User.objects.get(id=payload['user_id'])
            
            if user is None:
                return Response({"error": "There was an error retrieving account info!"}, status=status.HTTP_404_NOT_FOUND)
            
            if not user.is_verified:
                return Response({"message": "Your account is not verified yet!"}, status=status.HTTP_401_UNAUTHORIZED)
            
            if not user.is_active:
                return Response({"message": "Your account is not active!"}, status=status.HTTP_403_FORBIDDEN)
            
        except jwt.ExpiredSignatureError:
            return Response({"error": f'Token has expired. Go to http://localhost:8000/resend-email-verification to resend email verification.'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return Response({"error": f'An error occured! Go to http://localhost:8000/resend-email-verification to resend email verification'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_verified": user.is_verified,
                "is_active": user.is_active,
                "joined_at": user.created_at,
            }
        })

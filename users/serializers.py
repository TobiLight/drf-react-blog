from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode



class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, min_length=6, max_length=68)
    
    default_error_messages = {
        'username': 'The username should only contain alphanumeric characters'}

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def validate(self, attrs):
        # email = attrs.get('email', '')
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError(
                'Username should only contain alphanumeric characters!')
        # return super().validate(attrs)
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(
        max_length=255, min_length=3, read_only=True)

    tokens = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email',  'password', 'tokens']
        
    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])
        return {
            "refresh": user.tokens()['refresh'],
            "access": user.tokens()['access']
        }
        
    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        user_by_email = User.objects.filter(email=email)
        
        if user_by_email.exists() and user_by_email.auth_provider != 'email':
            raise AuthenticationFailed('Please continue your login using {user_by_email[0].auth_provider}')
        
        user = authenticate(email=email, password=password)
        
        if not user:
            raise AuthenticationFailed('Invalid login crredentials, try again.')
        
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin.')
        
        if user.is_banned:
            raise AuthenticationFailed('Your account has been banned from using this app!')
        
        if user.is_suspended:
            raise AuthenticationFailed('Your account has been suspended, contact admin.')
        
        if not user.is_verified:
            raise AuthenticationFailed('Email not verified!')
        
        super().validate(attrs)
        
        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens
        }

        return super().validate(attrs)


class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['username', 'email', 'is_verified', 'is_active', 'created_at']
        
class ReverificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']
        

class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)
    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()
            super().validate(attrs)
            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        
        return super().validate(attrs)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')
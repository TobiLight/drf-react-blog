from rest_framework import serializers
import os
from rest_framework.exceptions import AuthenticationFailed
from .register import register_social_user
from .google import Google
from dotenv import dotenv_values

class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = Google.validate(auth_token)
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please login again.'
            )

        if user_data['aud'] != dotenv_values('.env')['GOOGLE_CLIENT_ID']:
            raise AuthenticationFailed('WHO ARE YOU?!')

        user_id = user_data['sub']
        email = user_data['email']
        provider = 'google'
        name = email.split("@")[0]
        return register_social_user(
            provider=provider, user_id=user_id, email=email, name=name
        )
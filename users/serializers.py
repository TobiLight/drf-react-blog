from rest_framework import serializers

from .models import User


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, min_length=6, max_length=68)

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
    

class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, min_length=6, max_length=68)

    class Meta:
        model = User
        fields = ['email',  'password']


class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['username', 'email', 'is_verified', 'is_active', 'created_at']
        
class ReverificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']
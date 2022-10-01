import os
from typing import Any, Dict
import requests
from django.core.exceptions import ValidationError
from dotenv import dotenv_values


GOOGLE_ID_TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

def get_google_token(code, redirect_url):
    data = {
        'code': code,
        'client_id': dotenv_values('.env')['GOOGLE_CLIENT_ID'],
        'client_secret': dotenv_values('.env')['GOOGLE_CLIENT_SECRET'],
        'redirect_uri': redirect_url,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

    if not response.ok:
        raise ValidationError('Failed to obtain access token from Google.')

    token = response.json()

    return token


def google_get_user_info(*, access_token: str) -> Dict[str, Any]:
    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={'access_token': access_token}
    )
    
    if not response.ok:
        raise ValidationError('Failed to obtain user info from Google.')

    return response.json()
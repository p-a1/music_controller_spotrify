from .models import Spotify_Token
from django.utils import timezone
from datetime import timedelta
from requests import post,put,get
from .credentials import *
from rest_framework.response import Response
from rest_framework import status

BASE_URL='https://api.spotify.com/v1/me/'

def get_user_tokens(session_id):
    return Spotify_Token.objects.filter(user=session_id).first()

def update_or_create_user_tokens(session_id,access_token,token_type,expires_in,refresh_token):
    tokens=get_user_tokens(session_id)
    expires_in=timezone.now() + timedelta(seconds=expires_in)
    if tokens:
        tokens.access_token=access_token
        tokens.refresh_token=refresh_token
        tokens.expires_in=expires_in
        tokens.token_type=token_type
        tokens.save(update_fields=['access_token','expires_in','token_type','refresh_token'])
    else:
        tokens=Spotify_Token(user=session_id,access_token=access_token,token_type=token_type,expires_in=expires_in,refresh_token=refresh_token)
        tokens.save()
def is_spotify_authenticated(session_id):
    tokens= get_user_tokens(session_id)
    if tokens:
        expiry=tokens.expires_in
        if expiry<=timezone.now():
            refresh_spotify_token(session_id)
        return True
    return False
def refresh_spotify_token(session_id):
    refresh_token=get_user_tokens(session_id).refresh_token # type: ignore
    response=post('https://accounts.spotify.com/api/token',data={
        'grant_type':'refresh_token',
        'refresh_token':refresh_token,
        'client_id':CLIENT_ID,
        'client_secret':CLIENT_SECRET,
    }).json()
    
    access_token=response.get('access_token')
    token_type=response.get('token_type')
    expires_in=response.get('expires_in')
    refresh_token=response.get('refresh_token')or refresh_token
    update_or_create_user_tokens(session_id,access_token,token_type,expires_in,refresh_token)
    
def execute_spotify_api_request(session_id,endpoint,post_=False,put_=False):
    tokens=get_user_tokens(session_id)
    headers = {
            'Authorization': f'Bearer {tokens.access_token}',
            'Content-Type': 'application/json',
        }
    if post_ :
        post(BASE_URL+endpoint,headers=headers)
    if put_:
        put(BASE_URL+endpoint,headers=headers) 
    response=get(BASE_URL+endpoint,{},headers=headers)
    try:
        return response.json()
    except:
        return {'error':'Issue with request'}
def play(session_id):
    return execute_spotify_api_request(session_id,'player/play',put_=True) 
def pause(session_id):
    return execute_spotify_api_request(session_id,'player/pause',put_=True)
def skip(session_id):
    return execute_spotify_api_request(session_id,'player/next',post_=True)

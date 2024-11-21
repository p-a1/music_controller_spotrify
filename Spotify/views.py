from django.shortcuts import redirect
from .credentials import *
from rest_framework.views import APIView
from requests import Request,post
from rest_framework.response import Response
from rest_framework import status
from .util import update_or_create_user_tokens,is_spotify_authenticated,execute_spotify_api_request,pause,play,skip
from api.models import Room
from requests import get,put
from .models import Vote

# Create your views here.

class auth_url(APIView):
    def get(self,request,format=None):
        scopes = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'
        url= Request('GET','https://accounts.spotify.com/authorize',params={
            'scope':scopes,
            'response_type':'code',
            'redirect_uri':REDIRECT_URL,
            'client_id':CLIENT_ID,
        }).prepare().url
        return Response({'url':url},status=status.HTTP_200_OK)

def spotify_callback(request,format=None):
    code=request.GET.get('code')
    error= request.GET.get('error')

    response=post('https://accounts.spotify.com/api/token',data={
        'grant_type':'authorization_code',
        'code':code,
        'redirect_uri':REDIRECT_URL,
        'client_id':CLIENT_ID,
        'client_secret':CLIENT_SECRET,
    }).json()
    access_token=response.get('access_token')
    token_type=response.get('token_type')
    refresh_token=response.get('refresh_token')
    expires_in=response.get('expires_in')
    error=response.get('error')
    if not request.session.exists(request.session.session_key):
        request.session.create()
    session_key=request.session.session_key
    update_or_create_user_tokens(session_key,access_token,token_type,expires_in,refresh_token)
    return redirect('frontend:')
class is_authenticated(APIView):
    def get(self,reqeust,format=None):
        is_authenticated=is_spotify_authenticated(self.request.session.session_key)
        return Response({'status':is_authenticated},status=status.HTTP_200_OK)

class current_song(APIView):
    def get(self,request,format=None):
        room_code =self.request.session.get('room_code')
        room=Room.objects.filter(code=room_code).first()
        if not room:
            return Response({'error':'the room not found'},status=status.HTTP_404_NOT_FOUND)
        host=room.host # type: ignore
        endpoint='player/currently-playing'
        response=execute_spotify_api_request(host,endpoint)
        
        if 'error' in response or 'item' not in response:
            return Response({'error':'no content'},status=status.HTTP_204_NO_CONTENT)
        
        item=response.get('item')
        duration=item.get('duration_ms')# type: ignore
        progress=response.get('progress_ms')
        album_cover=item.get('album').get('images')[0].get('url')# type: ignore
        is_playing=response.get('is_playing')
        song_id=item.get('id')# type: ignore
        artists=''
        for i,artist in enumerate(item.get('artists')):# type: ignore
            if i>0:
                artists+=', '
            
            artists+=artist.get('name')
        votes=len(Vote.objects.filter(room=room,song_id=room.current_song))
        song={
            'title':item.get('name'), # type: ignore
            'artist':artists,
            'duration':duration,
            'time':progress,
            'image_url':album_cover,
            'is_playing':is_playing,
            'id':song_id,
            'votes':votes,
            'votes_required':room.votes_to_skip,    
        }
        
        self.upate_room_song(room,song_id)
        return Response(song,status=status.HTTP_200_OK)
    
    
    
    def upate_room_song(self,room,song_id):
        current_song=room.current_song
        if current_song != song_id:
            room.current_song=song_id
            room.save(update_fields=['current_song'])
            Votes=Vote.objects.filter(room=room).delete()




class pause_song(APIView):
    def put(self,response,format=None):
        room=Room.objects.filter(code=self.request.session.get('room_code')).first()
        if room.host==self.request.session.session_key or room.guest_can_pause:
            pause(room.host) 
            return Response({},status=status.HTTP_200_OK)
        return Response({},status=status.HTTP_403_FORBIDDEN)
class play_song(APIView):
    def put(self,response,format=None):
        room=Room.objects.filter(code=self.request.session.get('room_code')).first()
        if room.host==self.request.session.session_key or room.guest_can_pause:
            play(room.host) 
            return Response({},status=status.HTTP_200_OK)
        return Response({},status=status.HTTP_403_FORBIDDEN)

# class get_error(APIView):
#     def get(self,request,format=None):
#         session_id=self.request.session.session_key
#         tokens=get_user_tokens(session_id)
#         header={'content-Type':'application/json','Authorization':'Bearer '+tokens.access_token} # type: ignore
#         response=get('https://api.spotify.com/v1/me/player/devices',headers=header)
#         try:
#             return Response(response.json(),status=status.HTTP_200_OK)
#         except:
#             return Response({'error':response.text},status=status.HTTP_200_OK)
# class start_playback(APIView):
#     def get (self,request,format=None):
#         tokens = get_user_tokens(self.request.session.session_key)
#         headers = {
#             'Authorization': f'Bearer {tokens.access_token}',
#             'Content-Type': 'application/json',
#         }
#         response = put('https://api.spotify.com/v1/me/player/play', headers=headers)
#         return Response({'c':response.text})
class skip_song(APIView):
    def post(self,request,format=None):
        room_code=self.request.session.get('room_code')
        room=Room.objects.filter(code=room_code).first()
        votes=Vote.objects.filter(room=room,song_id=room.current_song)
        votes_needed=room.votes_to_skip
        if self.request.session.session_key==room.host or len(votes)+1>=votes_needed:
            skip(room.host)
        else:
            vote=Vote(user=self.request.session.session_key,room=room,song_id=room.current_song)
            vote.save()
        return Response({},status=status.HTTP_204_NO_CONTENT)
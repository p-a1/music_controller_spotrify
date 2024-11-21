from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Room
from .serializers import Room_serial, Create_Room_serial,Update_Room_serial
from rest_framework.views import APIView
from django.http import JsonResponse


class Create_Room(APIView):
    serializer_class = Create_Room_serial

    def post(self, request, format=None):
        # Ensure session key exists
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            name = serializer.data.get('name')# type: ignore
            guest_can_pause = serializer.data.get('guest_can_pause')# type: ignore
            votes_to_skip = serializer.data.get('votes_to_skip')# type: ignore
            host = session_key  # Get session key to use as host
            
            room = Room.objects.filter(host=host).first()
            if room:
                # Update existing room
                room.guest_can_pause = guest_can_pause # type: ignore
                room.votes_to_skip = votes_to_skip # type: ignore
                room.name = name # type: ignore
                room.save(update_fields=['guest_can_pause', 'votes_to_skip', 'name'])
                self.request.session['room_code']=str(room.code)
                return Response(Room_serial(room).data, status=status.HTTP_200_OK)
            else:
                # Create a new room
                room = Room(
                    host=host,
                    guest_can_pause=guest_can_pause,
                    votes_to_skip=votes_to_skip,
                    name=name
                )
                room.save()
                self.request.session['room_code']=str(room.code)
                return Response(Room_serial(room).data, status=status.HTTP_201_CREATED)
        
        # If serializer is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#this for room join page
class join_room(APIView):
    def post(self,request,format=None):
        session_key=self.request.session.session_key
        if not session_key:
            self.request.session.create()
        code=self.request.data.get('code') # type: ignore
        if code:
            room=Room.objects.filter(code=code).first()
            if room:
                self.request.session['room_code']=str(room.code)
                return Response({"message":"Room join"},status=status.HTTP_200_OK)
            return Response({"Bad Request":"Invalid Room Code"},status=status.HTTP_404_NOT_FOUND)
        return Response({"Bad Request":"Invalid Room Code"},status=status.HTTP_400_BAD_REQUEST)
#this for room page 
class get_room(APIView):
    serial=Room_serial
    def get(self ,request,format=None):
        code=request.GET.get('code')
        if code !=  None:
            room=Room.objects.filter(code=code).first()
            if room:
                data=self.serial(room).data
                data['is_host']=(self.request.session.session_key==room.host) # type: ignore
                return Response(data,status=status.HTTP_200_OK)
            return Response(self.serial.errors,status=status.HTTP_404_NOT_FOUND)
        return Response(request,status=status.HTTP_400_BAD_REQUEST)
    
    
class user_in_room(APIView):
    def get(self,format=None):
        if not self.request.session.session_key:
            self.request.session.create()
        data={
            'code':self.request.session.get('room_code')
        }
        return JsonResponse(data,status=status.HTTP_200_OK)
    
class leave_room(APIView):
    def post(self,request,format=None):
        if 'room_code'in self.request.session:
            self.request.session.pop('room_code')
            id_host=self.request.session.session_key
            room=Room.objects.filter(host=id_host).first()
            if room:
                room.delete()
            return Response({'message':'Success'},status=status.HTTP_200_OK)

class update_room(APIView):
    serial = Update_Room_serial

    def patch(self, request, format=None):
        # Check if the session exists, and create one if it doesn't
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        session_key = self.request.session.session_key
        serialized = self.serial(data=request.data)

        if serialized.is_valid():
            code = serialized.data.get('code')# type: ignore
            room = Room.objects.filter(code=code).first()

            if room:
                if room.host == session_key:
                    # Update the room fields based on the data from the request
                    room.votes_to_skip = serialized.data.get('votes_to_skip') # type: ignore
                    room.guest_can_pause = serialized.data.get('guest_can_pause')# type: ignore
                    room.name = serialized.data.get('name')# type: ignore
                    room.save(update_fields=['votes_to_skip', 'guest_can_pause', 'name'])
                    
                    return Response({'message': 'Room updated successfully'}, status=status.HTTP_200_OK)
                
                return Response({'message': 'You are not authorized'}, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response({'message': 'Invalid Room Code'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)

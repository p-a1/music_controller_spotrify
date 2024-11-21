from django.urls import path
from .views import Create_Room,get_room,join_room,user_in_room,leave_room,update_room

urlpatterns = [
    path('createRoom',Create_Room.as_view(),name='RoomApi'),
    path('get_room',get_room.as_view()),
    path('join_room',join_room.as_view()),
    path('user_in_room',user_in_room.as_view()),
    path('leave_room',leave_room.as_view()),
    path('update_room',update_room.as_view())
]

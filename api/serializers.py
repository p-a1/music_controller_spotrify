from rest_framework import serializers
from .models import Room

class Room_serial (serializers.ModelSerializer):
    class Meta :
        model= Room
        fields = '__all__'

class Create_Room_serial(serializers.ModelSerializer):
    class Meta:
        model= Room
        fields=('guest_can_pause','votes_to_skip','name')
        
class Update_Room_serial(serializers.ModelSerializer):
    code=serializers.CharField(validators=[])
    class Meta:
        model= Room
        fields=('guest_can_pause','votes_to_skip','name','code')
        
from rest_framework import serializers
from rest_framework.response import Response

from .models import *


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = "__all__"
        
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
            for attr, value in validated_data.items():
                if attr == 'password':
                    instance.set_password(value)
                else:
                    setattr(instance, attr, value)
            instance.save()
            return instance
    

class CarSerializer(serializers.ModelSerializer):
    gpsdevice_phone_number = serializers.SerializerMethodField()
    class Meta:
        model = Car
        fields = "__all__"

    def get_gpsdevice_phone_number(self, obj):
        if obj.gpsdevice:
            return obj.gpsdevice.phone_number
        return None


class GpsDevicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GpsDevices
        fields = "__all__"
        

class TrackerGpsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerData
        fields = "__all__"

class TrackerGpsDataPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerData
        fields = ['data']        


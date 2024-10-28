from django import views
from django.urls import path
from .views import *


app_name = 'app'

urlpatterns = [
    path('registre', RegisterView.as_view()),
    path('cars', CarView.as_view()),
    path('cars/<str:pk>', CarView.as_view()),
    path('gpsdevices', GpsDevicesView.as_view()),
    path('gpsdevices/<str:pk>', GpsDevicesView.as_view()),
    path('users', UserView.as_view()),
    path('users/<uuid:pk>/', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('tracker', TrackerView.as_view()),
    path('tracker/<str:date>', TrackerView.as_view()),
    path('tracker/<str:date>/<str:pk>', TrackerView.as_view()),
    path('tracker/<str:date>/<str:pk>/last', LastTrackView.as_view()),
    path('lastposition/<str:imei>', LastPositiongView.as_view()),
    path('update-device-token/', DeviceTokenUpdateView.as_view(), name='update-device-token'),


]
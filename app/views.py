import json
import os
from datetime import datetime
from pathlib import Path

import firebase_admin
import jwt
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.timezone import get_current_timezone, make_aware
from firebase_admin import messaging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from blackgpsapi.settings import BASE_DIR, SECRET_KEY

from .models import *
from .serializers import *


def implementJsonData(folder, name):
    with open('{}/trackers/{}/{}.json'.format(BASE_DIR, folder, name), 'r') as file:
        data = json.load(file)
        for item in data:
            obj = {
                'lat': item['lat'],
                'lon': item['lon'],
                'ioElements': item['ioElements']
            }

            TrackerData.objects.create(
                imei=name,
                timestamp=parse_datetime(item['timestamp']),
                data=obj
            )

def send_notification(sending, device_token, title, body, image=None):
    if sending:
        message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                    image=image,
                ),
                token=device_token
            )
        response = messaging.send(message)


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return({'message':'{}'.format(serializer.errors)})

class CarView(APIView):
    permission_classes=(IsAuthenticated,)

    def post(self,request):
        token = request.META.get('HTTP_AUTHORIZATION') 
        token = token.replace('Bearer ', '')
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        try:
            user = User.objects.filter(id=payload["user_id"]).first()
            data = request.data
            serializer = CarSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message':'{}'.format(e)},status=status.HTTP_400_BAD_REQUEST) 
            
    def get(self,request,pk=None):
        token = request.META.get('HTTP_AUTHORIZATION') 
        token = token.replace('Bearer ', '')
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        try:
            user = User.objects.filter(id=payload["user_id"]).first()
            if pk == None:
                data = Car.objects.filter(Q( user_id=user) & Q(is_deleted=False))
                serializer = CarSerializer(data, many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                data = get_object_or_404(Car,plate_number=pk,user_id=user)
                serializer = CarSerializer(data)
                return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':'{}'.format(e)},status=status.HTTP_400_BAD_REQUEST) 
    

    def put(self, request, pk):
        token = request.META.get('HTTP_AUTHORIZATION')
        token = token.replace('Bearer ', '')
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        try:
            user = User.objects.get(id=payload["user_id"])
            car = get_object_or_404(Car, plate_number=pk,user_id=user)
            if car.user_id != user:
                return Response({'message': 'you must have authorisation to modify this car'}, status=status.HTTP_403_FORBIDDEN)
            serializer = CarSerializer(car, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        token = request.META.get('HTTP_AUTHORIZATION')
        token = token.replace('Bearer ', '')
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        try:
            user = User.objects.get(id=payload["user_id"])
            car = get_object_or_404(Car, plate_number=pk,user_id=user)
            if car.user_id != user:
                return Response({'message': 'you must have authorisation to delete this car'}, status=status.HTTP_403_FORBIDDEN)
            car.is_deleted = True
            car.save()
            return Response({'message': 'Car successfully deleted '}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)


class GpsDevicesView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = GpsDevicesSerializer(data=request.data)
        if serializer.is_valid():
            gps_device = serializer.save()  # Save the device and get the instance
            # Handle device token separately if it's part of the request
            device_token = request.data.get('token')
            if device_token:
                gps_device.device_token = device_token
                gps_device.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        device = get_object_or_404(GpsDevices, imei=pk)
        serializer = GpsDevicesSerializer(device, data=request.data)
        if serializer.is_valid():
            gps_device = serializer.save()
            device_token = request.data.get('token')
            if device_token:
                gps_device.device_token = device_token
                gps_device.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request,pk=None):
       
        try:
            if pk == None:
                devices = GpsDevices.objects.filter(is_deleted=False)
                serializer = GpsDevicesSerializer(devices, many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                devices =  get_object_or_404(GpsDevices,imei=pk)
                serializer = GpsDevicesSerializer(devices)
                return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)

    
        

    def delete(self, request, pk):
        try:
            device = get_object_or_404(GpsDevices, imei=pk)
            device.is_deleted = True
            device.save()
            return Response({'message': 'Car successfully deleted '},status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)




class DeviceTokenUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        token = request.data.get('device_token')
        if token:
            user.device_token = token
            user.save()
            return Response({'message': 'Device token updated successfully'}, status=200)
        return Response({'error': 'No token provided'}, status=400)





        
class LastTrackView(APIView):
    def get(self, request, date, pk):
        BASE_DIR = Path(__file__).resolve().parent.parent
        directory = os.path.join(BASE_DIR, 'trackers', date)
        file_path = os.path.join(directory, f"{pk}.json")

        if not os.path.exists(directory):
            return JsonResponse({'error': f'Data for GPS with date: {date} not found'}, status=404)
        
        if not os.path.exists(file_path):
            return JsonResponse({'error': f'Data for GPS with IMEI {pk} not found'}, status=404)

        try:
            with open(file_path, 'r') as json_file:
                gps_data = json.load(json_file)
                if not gps_data:
                    return JsonResponse({'error': 'Le fichier JSON est vide'}, status=404)
                return JsonResponse([gps_data[-1]], safe=False)  # Retourne le dernier élément enveloppé dans une liste
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Erreur de format dans le fichier JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class LastPositiongView(APIView):

    def get(self, request, imei):
        try:
            
            dataLastTracker = TrackerData.objects.filter(imei=imei).last()
            dataObject = TrackerGpsDataPointsSerializer(dataLastTracker)
            return JsonResponse([dataObject.data], status=status.HTTP_200_OK, safe=False)

        except Exception as e:
            return JsonResponse({'error': 'Erreur lors de la récupération des données : ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SqlTrackerView(APIView):
        def get(self, request, imei):
            try:
                # Filtrer les données uniquement par IMEI
                data_entries = TrackerData.objects.filter(imei=imei)

                if not data_entries.exists():
                    return JsonResponse({'error': 'Aucune donnée trouvée pour cet IMEI.'}, status=status.HTTP_404_NOT_FOUND)

                # Préparation de la réponse
                data_list = [entry.data for entry in data_entries]     
                    
                return JsonResponse(data_list, safe=False, status=status.HTTP_200_OK)

            except Exception as e:
                return JsonResponse({'error': 'Erreur lors de la récupération des données : ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class TrackerView(APIView):
    def post(self, request):
        try:
            imei = request.data.get('imei')
            if not GpsDevices.objects.filter(imei=imei).exists():
                raise ValueError("Aucun GPS avec l'IMEI fourni n'a été trouvé.")
            
            gps_device = GpsDevices.objects.filter(imei=imei).first()
            if not gps_device:
                return JsonResponse({'message': "Aucun GPS avec l'IMEI fourni n'a été trouvé."}, status=status.HTTP_404_NOT_FOUND)

            car = Car.objects.filter(gpsdevice=gps_device).first()
            if not car:
                return JsonResponse({'message': "No car associated with this GPS device."}, status=status.HTTP_404_NOT_FOUND)

            user = get_object_or_404(User, id=car.user_id.id)

            dataToPost = request.data
            io_elements = dataToPost.get('data', {}).get('ioElements', [])
            ignition_status = io_elements[0]['value']
            speed_value = io_elements[8]['value']
            gpsTracker = get_object_or_404(GpsDevices, imei=imei)
            is_ignited = gpsTracker.is_ignited

            if speed_value >= 130:
                send_notification(user.is_notification, user.device_token, 'Vitesse Alert', 'Excess de vitesse {} Km/h voiture {}'.format(speed_value, car.plate_number))

            if is_ignited == False and ignition_status == 0:
                return Response({'message': 'Car is not moving'}, status=status.HTTP_200_OK)
            elif is_ignited == False and ignition_status == 1:
                GpsDevices.objects.filter(imei=imei).update(is_ignited=True)
                serializer = TrackerGpsDataSerializer(data=dataToPost)
                if serializer.is_valid():
                    serializer.save()
                    send_notification(user.is_notification, user.device_token, 'Voiture Start', 'Voiture {} Start'.format(car.plate_number))
                    return Response({'message': 'Car Is Moving'}, status=status.HTTP_200_OK)
            elif is_ignited == True and ignition_status == 0:
                GpsDevices.objects.filter(imei=imei).update(is_ignited=False)
                serializer = TrackerGpsDataSerializer(data=dataToPost)
                if serializer.is_valid():
                    serializer.save()
                    send_notification(user.is_notification, user.device_token, 'Voiture Stop', 'Voiture {} Stop'.format(car.plate_number))
                    return Response({'message': 'Car Is Stoped'}, status=status.HTTP_200_OK)
            else:
                serializer = TrackerGpsDataSerializer(data=dataToPost)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'message': 'Data Is Saved'}, status=status.HTTP_200_OK) 
                               
            return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
      
    def get(self, request, date, pk):
        try:
            # Parse the date string to a date object
            parsed_date = parse_date(date)
            if not parsed_date:
                raise ValueError("Invalid date format")

            # Get the current timezone
            current_tz = get_current_timezone()
            
            # Make the start and end of the day datetime objects in the current timezone
            start_of_day = make_aware(datetime.combine(parsed_date, datetime.min.time()), timezone=current_tz)
            end_of_day = make_aware(datetime.combine(parsed_date, datetime.max.time()), timezone=current_tz)

            # Debugging output
            print(f"Filtering from {start_of_day} to {end_of_day} for IMEI {pk}")

            # Filter objects within the day
            dataTracker = TrackerData.objects.filter(imei=pk, timestamp__range=(start_of_day, end_of_day)).order_by('timestamp')
            
            # Debugging output
            print(f"Found {dataTracker.count()} records")

            dataObject = TrackerGpsDataPointsSerializer(dataTracker, many=True)
            return Response(dataObject.data, status=status.HTTP_200_OK)
        except Exception as e:
            # Debugging output
            print(f"Error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)



    
    
class UserView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, pk=None):
        token = request.META.get('HTTP_AUTHORIZATION') 
        token = token.replace('Bearer ', '')
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        try:
            data = get_object_or_404(User, id=payload["user_id"], is_deleted=False)
            serializer = UserSerializer(data)
            return Response([serializer.data],status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':'{}'.format(e)},status=status.HTTP_400_BAD_REQUEST) 
    
    def put(self, request, pk=None):
        token = request.META.get('HTTP_AUTHORIZATION') 
        token = token.replace('Bearer ', '')
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        try:
            user = User.objects.filter(id=payload["user_id"]).first()
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message':'utilisateur non autorisé pour la modification'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message':'{}'.format(e)},status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        token = request.META.get('HTTP_AUTHORIZATION') 
        token = token.replace('Bearer ', '')
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        try:
            user = User.objects.filter(id=payload["user_id"]).first()
            if user.user_type == 1 :
              user_ = get_object_or_404(User,id=pk)
              user_.is_deleted=True
              user_.save()
              return Response({'message': 'utilisateur supprimé avec succès'}, status=status.HTTP_204_NO_CONTENT)
              
            else:
                return Response({'message':'utilisateur non autorisé pour la suppression'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message':'{}'.format(e)},status=status.HTTP_400_BAD_REQUEST) 
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    
class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('csrftoken')
        response.data = {
            'message': 'success'
        }
        return response
from django.contrib import admin
from .models import User, Car, GpsDevices, TrackerData

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'user_type', 'is_deleted')
    list_filter = ('user_type', 'is_deleted')
    search_fields = ('email', 'id')

    def save_model(self, request, obj, form, change):
        if obj.password:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'plate_number', 'user_id', 'gpsdevice', 'numero_voiture')
    search_fields = ('name', 'plate_number')
    list_filter = ('is_deleted',)
    

@admin.register(GpsDevices)
class GpsDevicesAdmin(admin.ModelAdmin):
    list_display = ('imei', 'phone_number', 'operator', 'is_deleted')
    search_fields = ('imei', 'phone_number')
    list_filter = ('operator', 'is_deleted')


admin.site.register(TrackerData)
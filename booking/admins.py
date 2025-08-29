from django.contrib import admin
from .models import TravelOption, UserProfile, Booking

@admin.register(TravelOption)
class TravelOptionAdmin(admin.ModelAdmin):
    list_display = ['travel_id', 'type', 'source', 'destination', 'date_time', 'price', 'available_seats']
    list_filter = ['type', 'source', 'destination', 'date_time']
    search_fields = ['travel_id', 'source', 'destination']
    ordering = ['date_time']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'date_of_birth']
    search_fields = ['user__username', 'user__email', 'phone_number']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'user', 'travel_option', 'number_of_seats', 'total_price', 'status', 'booking_date']
    list_filter = ['status', 'booking_date', 'travel_option__type']
    search_fields = ['booking_id', 'user__username']
    readonly_fields = ['booking_id', 'total_price', 'booking_date']
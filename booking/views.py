from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import TravelOption, Booking, UserProfile
from .forms import CustomUserCreationForm, UserProfileForm, TravelSearchForm, BookingForm

def home(request):
    # Get recent travel options for home page
    recent_travels = TravelOption.objects.filter(
        date_time__gte=timezone.now(),
        available_seats__gt=0
    )[:6]
    
    return render(request, 'booking/home.html', {'recent_travels': recent_travels})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'booking/register.html', {'form': form})

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            # Update user fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            
            # Save profile
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'booking/profile.html', {'form': form})

def travel_list(request):
    form = TravelSearchForm(request.GET)
    travels = TravelOption.objects.filter(
        date_time__gte=timezone.now(),
        available_seats__gt=0
    )
    
    if form.is_valid():
        if form.cleaned_data['type']:
            travels = travels.filter(type=form.cleaned_data['type'])
        if form.cleaned_data['source']:
            travels = travels.filter(source__icontains=form.cleaned_data['source'])
        if form.cleaned_data['destination']:
            travels = travels.filter(destination__icontains=form.cleaned_data['destination'])
        if form.cleaned_data['date']:
            travels = travels.filter(date_time__date=form.cleaned_data['date'])
    
    paginator = Paginator(travels, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'booking/travel_list.html', {
        'form': form,
        'page_obj': page_obj,
        'travels': page_obj
    })

@login_required
def booking_create(request, travel_id):
    travel_option = get_object_or_404(TravelOption, id=travel_id)
    
    if travel_option.available_seats <= 0:
        messages.error(request, 'No seats available for this travel option.')
        return redirect('travel_list')
    
    if request.method == 'POST':
        form = BookingForm(request.POST, travel_option=travel_option)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.travel_option = travel_option
            booking.total_price = travel_option.price * booking.number_of_seats
            
            # Check seat availability again
            if booking.number_of_seats <= travel_option.available_seats:
                booking.save()
                
                # Update available seats
                travel_option.available_seats -= booking.number_of_seats
                travel_option.save()
                
                messages.success(request, f'Booking confirmed! Booking ID: {booking.booking_id}')
                return redirect('booking_detail', booking_id=booking.booking_id)
            else:
                messages.error(request, 'Not enough seats available.')
    else:
        form = BookingForm(travel_option=travel_option)
    
    return render(request, 'booking/booking_form.html', {
        'form': form,
        'travel_option': travel_option
    })

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    return render(request, 'booking/booking_detail.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    
    if booking.status == 'confirmed':
        booking.status = 'cancelled'
        booking.save()
        
        # Return seats to available inventory
        travel_option = booking.travel_option
        travel_option.available_seats += booking.number_of_seats
        travel_option.save()
        
        messages.success(request, 'Booking cancelled successfully!')
    else:
        messages.error(request, 'This booking cannot be cancelled.')
    
    return redirect('my_bookings')
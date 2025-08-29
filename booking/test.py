from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import TravelOption, Booking, UserProfile

class TravelOptionModelTest(TestCase):
    def setUp(self):
        self.travel_option = TravelOption.objects.create(
            travel_id='FL001',
            type='flight',
            source='New York',
            destination='Los Angeles',
            date_time=timezone.now() + timedelta(days=1),
            price=Decimal('299.99'),
            available_seats=150
        )

    def test_travel_option_creation(self):
        self.assertEqual(self.travel_option.travel_id, 'FL001')
        self.assertEqual(self.travel_option.type, 'flight')
        self.assertEqual(self.travel_option.source, 'New York')
        self.assertEqual(self.travel_option.destination, 'Los Angeles')
        self.assertEqual(self.travel_option.price, Decimal('299.99'))
        self.assertEqual(self.travel_option.available_seats, 150)

    def test_travel_option_str_method(self):
        expected_str = "FL001 - Flight from New York to Los Angeles"
        self.assertEqual(str(self.travel_option), expected_str)

class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.travel_option = TravelOption.objects.create(
            travel_id='TR001',
            type='train',
            source='Chicago',
            destination='Detroit',
            date_time=timezone.now() + timedelta(days=2),
            price=Decimal('89.50'),
            available_seats=200
        )

    def test_booking_creation(self):
        booking = Booking.objects.create(
            user=self.user,
            travel_option=self.travel_option,
            number_of_seats=2
        )
        
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.travel_option, self.travel_option)
        self.assertEqual(booking.number_of_seats, 2)
        self.assertEqual(booking.total_price, Decimal('179.00'))  # 89.50 * 2
        self.assertEqual(booking.status, 'confirmed')
        self.assertTrue(booking.booking_id.startswith('BK'))

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.travel_option = TravelOption.objects.create(
            travel_id='BUS001',
            type='bus',
            source='Miami',
            destination='Orlando',
            date_time=timezone.now() + timedelta(hours=6),
            price=Decimal('45.00'),
            available_seats=40
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome to TravelBook')

    def test_travel_list_view(self):
        response = self.client.get(reverse('travel_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BUS001')

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'testpass123!',
            'password2': 'testpass123!'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_booking_requires_login(self):
        response = self.client.get(reverse('booking_create', args=[self.travel_option.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_booking_creation(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('booking_create', args=[self.travel_option.id]), {
            'number_of_seats': 2
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful booking
        self.assertTrue(Booking.objects.filter(user=self.user).exists())

    def test_my_bookings_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)

class BookingFunctionalityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.travel_option = TravelOption.objects.create(
            travel_id='TEST001',
            type='flight',
            source='Test City A',
            destination='Test City B',
            date_time=timezone.now() + timedelta(days=1),
            price=Decimal('100.00'),
            available_seats=5
        )

    def test_seat_availability_update(self):
        # Create a booking
        booking = Booking.objects.create(
            user=self.user,
            travel_option=self.travel_option,
            number_of_seats=3
        )
        
        # Update travel option seats manually (simulating the view logic)
        self.travel_option.available_seats -= booking.number_of_seats
        self.travel_option.save()
        
        # Check that available seats decreased
        self.travel_option.refresh_from_db()
        self.assertEqual(self.travel_option.available_seats, 2)

    def test_booking_cancellation(self):
        # Create a booking
        booking = Booking.objects.create(
            user=self.user,
            travel_option=self.travel_option,
            number_of_seats=2
        )
        
        # Simulate seat reduction
        self.travel_option.available_seats -= booking.number_of_seats
        self.travel_option.save()
        
        # Cancel booking
        booking.status = 'cancelled'
        booking.save()
        
        # Simulate seat restoration
        self.travel_option.available_seats += booking.number_of_seats
        self.travel_option.save()
        
        # Check results
        booking.refresh_from_db()
        self.travel_option.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        self.assertEqual(self.travel_option.available_seats, 5)
from django.db.models import Sum, Count, Avg
from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from common.permissions import IsAdmin, IsHotelOwner, IsTourOperator
from hotels.models import Hotel
from tours.models import TourPackage
from bookings.models import Booking
from payments.models import Payment
from reviews.models import Review

User = get_user_model()


class AdminDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        data = {
            'total_users': User.objects.count(),
            'total_hotels': Hotel.objects.count(),
            'total_tour_operators': User.objects.filter(role='tour_operator').count(),
            'total_bookings': Booking.objects.count(),
            'total_revenue': Payment.objects.filter(status='success').aggregate(total=Sum('amount'))['total'] or 0,
            'pending_approvals': (
                Hotel.objects.filter(is_approved=False).count()
                + TourPackage.objects.filter(is_approved=False).count()
                + User.objects.filter(role__in=['hotel_owner', 'tour_operator'], is_approved=False).count()
            ),
            'top_destinations': list(
                TourPackage.objects.values('destination').annotate(count=Count('id')).order_by('-count')[:5]
            ),
        }
        return Response(data)


class HotelOwnerDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsHotelOwner]

    def get(self, request):
        hotels = Hotel.objects.filter(owner=request.user)
        bookings = Booking.objects.filter(room__hotel__owner=request.user)
        data = {
            'total_rooms': sum(h.rooms.count() for h in hotels),
            'total_bookings': bookings.count(),
            'monthly_revenue': Payment.objects.filter(
                booking__room__hotel__owner=request.user, status='success'
            ).aggregate(total=Sum('amount'))['total'] or 0,
            'average_rating': Review.objects.filter(hotel__owner=request.user).aggregate(
                avg=Avg('rating')
            )['avg'] or 0,
        }
        return Response(data)


class TourOperatorDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTourOperator]

    def get(self, request):
        packages = TourPackage.objects.filter(operator=request.user)
        bookings = Booking.objects.filter(tour_package__operator=request.user)
        data = {
            'total_packages': packages.count(),
            'total_bookings': bookings.count(),
            'revenue': Payment.objects.filter(
                booking__tour_package__operator=request.user, status='success'
            ).aggregate(total=Sum('amount'))['total'] or 0,
            'upcoming_tours': bookings.filter(status='confirmed').count(),
        }
        return Response(data)


class CustomerDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(customer=request.user)
        data = {
            'upcoming_trips': bookings.filter(status='confirmed').count(),
            'booking_history': bookings.count(),
            'total_spent': Payment.objects.filter(user=request.user, status='success').aggregate(
                total=Sum('amount'))['total'] or 0,
        }
        return Response(data)

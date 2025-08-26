from django.shortcuts import render
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from booking.models import Booking
from rooms.models import Room
from guest.models import Guest
from rate.models import RatePlan

def dashboard_home(request):
    """Dashboard home view with KPIs"""
    today = date.today()
    
    # Date ranges for calculations
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Room Statistics
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(status='AVAILABLE').count()
    occupied_rooms = Room.objects.filter(status='OCCUPIED').count()
    maintenance_rooms = Room.objects.filter(status='MAINTENANCE').count()
    
    # Occupancy Rate
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    # Booking Statistics
    total_bookings = Booking.objects.count()
    active_bookings = Booking.objects.filter(status='CHECKED_IN').count()
    pending_bookings = Booking.objects.filter(status='PENDING').count()
    
    # Today's Check-ins and Check-outs
    todays_checkins = Booking.objects.filter(
        check_in_date=today,
        status__in=['CONFIRMED', 'PENDING']
    ).count()
    
    todays_checkouts = Booking.objects.filter(
        check_out_date=today,
        status='CHECKED_IN'
    ).count()
    
    # Revenue Statistics
    this_month_revenue = Booking.objects.filter(
        check_in_date__gte=this_month_start,
        check_in_date__lte=today,
        status__in=['CHECKED_IN', 'CHECKED_OUT']
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    last_month_revenue = Booking.objects.filter(
        check_in_date__gte=last_month_start,
        check_in_date__lte=last_month_end,
        status__in=['CHECKED_IN', 'CHECKED_OUT']
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Revenue growth calculation
    revenue_growth = 0
    if last_month_revenue > 0:
        revenue_growth = ((this_month_revenue - last_month_revenue) / last_month_revenue * 100)
    
    # Average Daily Rate (ADR)
    adr = Booking.objects.filter(
        status__in=['CHECKED_IN', 'CHECKED_OUT']
    ).aggregate(avg_rate=Avg('total_amount'))['avg_rate'] or Decimal('0.00')
    
    # Guest Statistics
    total_guests = Guest.objects.count()
    new_guests_this_month = Guest.objects.filter(
        created_at__gte=this_month_start
    ).count()
    
    # Loyalty distribution
    loyalty_stats = Guest.objects.values('loyalty_level').annotate(
        count=Count('loyalty_level')
    ).order_by('loyalty_level')
    
    # Recent bookings for quick overview
    recent_bookings = Booking.objects.select_related('guest', 'room').order_by('-created_at')[:5]
    
    # Upcoming check-ins (next 7 days)
    next_week = today + timedelta(days=7)
    upcoming_checkins = Booking.objects.filter(
        check_in_date__gte=today,
        check_in_date__lte=next_week,
        status__in=['CONFIRMED', 'PENDING']
    ).select_related('guest', 'room').order_by('check_in_date')[:10]
    
    # Room type occupancy
    room_type_stats = Room.objects.values('room_type__name').annotate(
        total=Count('id'),
        occupied=Count('id', filter=Q(status='OCCUPIED')),
        available=Count('id', filter=Q(status='AVAILABLE'))
    ).order_by('room_type__name')
    
    context = {
        # Room KPIs
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
        'occupancy_rate': round(occupancy_rate, 1),
        
        # Booking KPIs
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'pending_bookings': pending_bookings,
        'todays_checkins': todays_checkins,
        'todays_checkouts': todays_checkouts,
        
        # Revenue KPIs
        'this_month_revenue': this_month_revenue,
        'last_month_revenue': last_month_revenue,
        'revenue_growth': round(revenue_growth, 1),
        'adr': adr,
        
        # Guest KPIs
        'total_guests': total_guests,
        'new_guests_this_month': new_guests_this_month,
        'loyalty_stats': loyalty_stats,
        
        # Data for charts and tables
        'recent_bookings': recent_bookings,
        'upcoming_checkins': upcoming_checkins,
        'room_type_stats': room_type_stats,
        
        # Date context
        'today': today,
        'current_month': today.strftime('%B %Y'),
    }
    
    return render(request, 'dashboard/home.html', context)
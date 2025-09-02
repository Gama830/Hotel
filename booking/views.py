from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import date
from .models import Booking
from .forms import BookingForm, BookingSearchForm
from rooms.models import Room

def booking_list(request):
    """Display list of all bookings with search and filter functionality"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    bookings = Booking.objects.select_related('guest', 'room', 'room__room_type').all()
    
    # Apply search filter
    if search_query:
        bookings = bookings.filter(
            Q(guest__first_name__icontains=search_query) |
            Q(guest__last_name__icontains=search_query) |
            Q(guest__email__icontains=search_query) |
            Q(room__room_number__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(bookings, 10)  # Show 10 bookings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get status choices for filter dropdown
    status_choices = Booking.STATUS_CHOICES
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': status_choices,
        'total_bookings': bookings.count()
    }
    return render(request, 'booking/booking_list.html', context)

def booking_detail(request, booking_id):
    """Display detailed view of a specific booking"""
    booking = get_object_or_404(
        Booking.objects.select_related('guest', 'room', 'room__room_type'),
        id=booking_id
    )
    context = {'booking': booking}
    return render(request, 'booking/booking_detail.html', context)

def booking_create(request):
    """Create a new booking"""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            
            # Handle reservation source from search
            reservation_source_id = request.POST.get('reservation_source_id')
            if reservation_source_id:
                try:
                    from .models import ReservationSource
                    booking.reservation_source = ReservationSource.objects.get(id=reservation_source_id, is_active=True)
                except ReservationSource.DoesNotExist:
                    pass
            
            # Calculate total amount
            booking.total_amount = booking.calculate_total_amount()
            booking.save()
            messages.success(request, f'Booking #{booking.id} created successfully!')
            return redirect('booking-detail', booking_id=booking.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm()
    
    context = {
        'form': form,
        'title': 'Create New Booking',
        'submit_text': 'Create Booking'
    }
    return render(request, 'booking/booking_form.html', context)

def booking_update(request, booking_id):
    """Update an existing booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
            
            # Handle reservation source from search
            reservation_source_id = request.POST.get('reservation_source_id')
            if reservation_source_id:
                try:
                    from .models import ReservationSource
                    booking.reservation_source = ReservationSource.objects.get(id=reservation_source_id, is_active=True)
                except ReservationSource.DoesNotExist:
                    booking.reservation_source = None
            else:
                booking.reservation_source = None
            
            # Recalculate total amount if dates or room changed
            booking.total_amount = booking.calculate_total_amount()
            booking.save()
            messages.success(request, f'Booking #{booking.id} updated successfully!')
            return redirect('booking-detail', booking_id=booking.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm(instance=booking)
    
    context = {
        'form': form,
        'booking': booking,
        'title': f'Edit Booking #{booking.id}',
        'submit_text': 'Update Booking'
    }
    return render(request, 'booking/booking_form.html', context)

def booking_delete(request, booking_id):
    """Delete a booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        booking_info = f"#{booking.id} - {booking.guest.full_name}"
        booking.delete()
        messages.success(request, f'Booking {booking_info} deleted successfully!')
        return redirect('booking-list')
    
    context = {'booking': booking}
    return render(request, 'booking/booking_confirm_delete.html', context)

def booking_check_in(request, booking_id):
    """Check in a guest for their booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if booking.can_check_in():
        booking.status = 'CHECKED_IN'
        booking.room.status = 'OCCUPIED'
        booking.save()
        booking.room.save()
        messages.success(request, f'Guest {booking.guest.full_name} checked in successfully!')
    else:
        messages.error(request, 'This booking cannot be checked in.')
    
    return redirect('booking-detail', booking_id=booking.id)

def booking_check_out(request, booking_id):
    """Check out a guest from their booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if booking.can_check_out():
        booking.status = 'CHECKED_OUT'
        booking.room.status = 'AVAILABLE'
        booking.save()
        booking.room.save()
        messages.success(request, f'Guest {booking.guest.full_name} checked out successfully!')
    else:
        messages.error(request, 'This booking cannot be checked out.')
    
    return redirect('booking-detail', booking_id=booking.id)

def booking_cancel(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if booking.can_cancel():
        booking.status = 'CANCELED'
        # Make room available if it was reserved
        if booking.room.status == 'RESERVED':
            booking.room.status = 'AVAILABLE'
            booking.room.save()
        booking.save()
        messages.success(request, f'Booking #{booking.id} canceled successfully!')
    else:
        messages.error(request, 'This booking cannot be canceled.')
    
    return redirect('booking-detail', booking_id=booking.id)

def room_availability_search(request):
    """Search for available rooms based on dates and guest count"""
    form = BookingSearchForm(request.GET or None)
    available_rooms = []
    
    if form.is_valid():
        check_in_date = form.cleaned_data['check_in_date']
        check_out_date = form.cleaned_data['check_out_date']
        number_of_adults = form.cleaned_data['number_of_adults']
        number_of_children = form.cleaned_data['number_of_children']
        total_guests = number_of_adults + number_of_children
        
        # Find rooms that are not booked for the selected dates
        booked_room_ids = Booking.objects.filter(
            status__in=['CONFIRMED', 'CHECKED_IN'],
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date
        ).values_list('room_id', flat=True)
        
        available_rooms = Room.objects.filter(
            status='AVAILABLE'
        ).exclude(
            id__in=booked_room_ids
        ).select_related('room_type')
        
        # Filter by capacity if room type has capacity defined
        if total_guests > 0:
            available_rooms = available_rooms.filter(
                Q(room_type__capacity__gte=total_guests) | Q(room_type__capacity__isnull=True)
            )
    
    context = {
        'form': form,
        'available_rooms': available_rooms,
        'search_performed': form.is_valid()
    }
    return render(request, 'booking/room_availability.html', context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from datetime import datetime
from decimal import Decimal

@require_POST
def calculate_booking_amount(request):
    """AJAX endpoint to calculate booking amount"""
    try:
        check_in_date = request.POST.get('check_in_date')
        check_out_date = request.POST.get('check_out_date')
        room_id = request.POST.get('room')
        rate_plan_id = request.POST.get('rate_plan')
        number_of_adults = int(request.POST.get('number_of_adults', 1))
        number_of_children = int(request.POST.get('number_of_children', 0))
        
        if not all([check_in_date, check_out_date, room_id]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Parse dates
        check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()
        nights = (check_out - check_in).days
        
        if nights <= 0:
            return JsonResponse({'error': 'Invalid date range'}, status=400)
        
        # Get room
        try:
            room = Room.objects.select_related('room_type').get(id=room_id)
        except Room.DoesNotExist:
            return JsonResponse({'error': 'Room not found'}, status=404)
        
        # Calculate amount
        total_guests = number_of_adults + number_of_children
        rate_per_night = Decimal('0.00')
        total_amount = Decimal('0.00')
        
        # Try rate plan first
        if rate_plan_id:
            try:
                from rate.models import RatePlan
                rate_plan = RatePlan.objects.get(id=rate_plan_id)
                total_amount = rate_plan.calculate_total_rate(nights, total_guests)
                rate_per_night = rate_plan.base_rate
            except:
                pass
        
        # Fall back to room rates
        if total_amount == 0:
            if room.room_type and room.room_type.price_per_night:
                rate_per_night = room.room_type.price_per_night
                total_amount = rate_per_night * nights
            elif room.rate_default:
                rate_per_night = room.rate_default
                total_amount = rate_per_night * nights
        
        return JsonResponse({
            'total_amount': str(total_amount),
            'rate_per_night': str(rate_per_night),
            'nights': nights,
            'total_guests': total_guests
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def reservation_sources_api(request):
    """API endpoint to fetch reservation sources for search"""
    from .models import ReservationSource
    
    sources = ReservationSource.objects.filter(is_active=True).order_by('name')
    
    sources_data = []
    for source in sources:
        sources_data.append({
            'id': source.id,
            'source_id': source.source_id,
            'name': source.name,
            'source_type': source.source_type,
            'source_type_display': source.get_source_type_display(),
            'contact_person': source.contact_person,
            'is_active': source.is_active
        })
    
    return JsonResponse(sources_data, safe=False)
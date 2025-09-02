from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import date, timedelta
from .models import CheckIn
from .forms import CheckInForm, CheckInSearchForm, QuickCheckInForm
from booking.models import Booking
from guest.models import Guest
from rooms.models import Room


def checkin_list(request):
    """Display list of all check-ins with search and filter functionality"""
    search_query = request.GET.get('search', '')
    payment_status_filter = request.GET.get('payment_status', '')
    date_range_filter = request.GET.get('date_range', '')
    id_verified_filter = request.GET.get('id_verified', '')
    
    checkins = CheckIn.objects.select_related('guest', 'room_number', 'booking').all()
    
    # Apply search filter
    if search_query:
        checkins = checkins.filter(
            Q(check_in_id__icontains=search_query) |
            Q(guest__first_name__icontains=search_query) |
            Q(guest__last_name__icontains=search_query) |
            Q(room_number__room_number__icontains=search_query) |
            Q(assigned_staff__icontains=search_query)
        )
    
    # Apply payment status filter
    if payment_status_filter:
        checkins = checkins.filter(payment_status=payment_status_filter)
    
    # Apply ID verification filter
    if id_verified_filter:
        if id_verified_filter == 'true':
            checkins = checkins.filter(id_proof_verified=True)
        elif id_verified_filter == 'false':
            checkins = checkins.filter(id_proof_verified=False)
    
    # Apply date range filter
    if date_range_filter:
        today = date.today()
        if date_range_filter == 'today':
            checkins = checkins.filter(actual_check_in_date_time__date=today)
        elif date_range_filter == 'yesterday':
            yesterday = today - timedelta(days=1)
            checkins = checkins.filter(actual_check_in_date_time__date=yesterday)
        elif date_range_filter == 'this_week':
            week_start = today - timedelta(days=today.weekday())
            checkins = checkins.filter(actual_check_in_date_time__date__gte=week_start)
        elif date_range_filter == 'this_month':
            month_start = today.replace(day=1)
            checkins = checkins.filter(actual_check_in_date_time__date__gte=month_start)
    
    # Pagination
    paginator = Paginator(checkins, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'payment_status_filter': payment_status_filter,
        'date_range_filter': date_range_filter,
        'id_verified_filter': id_verified_filter,
        'payment_status_choices': CheckIn.PAYMENT_STATUS_CHOICES,
        'total_checkins': checkins.count()
    }
    return render(request, 'checkin/checkin_list.html', context)


def checkin_detail(request, checkin_id):
    """Display detailed view of a check-in"""
    checkin = get_object_or_404(
        CheckIn.objects.select_related('guest', 'room_number', 'booking'),
        id=checkin_id
    )
    
    context = {
        'checkin': checkin,
    }
    return render(request, 'checkin/checkin_detail.html', context)


def checkin_create(request):
    """Create a new check-in"""
    booking_id = request.GET.get('booking_id')
    booking_instance = None
    
    if booking_id:
        booking_instance = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        form = CheckInForm(request.POST, booking_instance=booking_instance)
        if form.is_valid():
            checkin = form.save()
            
            # Update room status to occupied
            checkin.room_number.status = 'OCCUPIED'
            checkin.room_number.save()
            
            # Update booking status if linked
            if checkin.booking:
                checkin.booking.status = 'CHECKED_IN'
                checkin.booking.save()
            
            messages.success(request, f'Check-in {checkin.check_in_id} created successfully!')
            return redirect('checkin-detail', checkin_id=checkin.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CheckInForm(booking_instance=booking_instance)
    
    context = {
        'form': form,
        'booking_instance': booking_instance,
        'title': 'New Check-In',
        'submit_text': 'Complete Check-In'
    }
    return render(request, 'checkin/checkin_form.html', context)


def checkin_update(request, checkin_id):
    """Update an existing check-in"""
    checkin = get_object_or_404(CheckIn, id=checkin_id)
    
    if request.method == 'POST':
        form = CheckInForm(request.POST, instance=checkin)
        if form.is_valid():
            checkin = form.save()
            messages.success(request, f'Check-in {checkin.check_in_id} updated successfully!')
            return redirect('checkin-detail', checkin_id=checkin.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CheckInForm(instance=checkin)
    
    context = {
        'form': form,
        'checkin': checkin,
        'title': f'Edit Check-In: {checkin.check_in_id}',
        'submit_text': 'Update Check-In'
    }
    return render(request, 'checkin/checkin_form.html', context)


def quick_checkin(request):
    """Quick check-in for walk-in guests"""
    if request.method == 'POST':
        form = QuickCheckInForm(request.POST)
        if form.is_valid():
            checkin = form.save(commit=False)
            checkin.actual_check_in_date_time = timezone.now()
            checkin.payment_status = 'PENDING'
            checkin.save()
            
            # Update room status
            checkin.room_number.status = 'OCCUPIED'
            checkin.room_number.save()
            
            messages.success(request, f'Quick check-in completed! Check-in ID: {checkin.check_in_id}')
            return redirect('checkin-detail', checkin_id=checkin.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = QuickCheckInForm()
    
    context = {
        'form': form,
        'title': 'Quick Check-In (Walk-in)',
        'submit_text': 'Complete Quick Check-In'
    }
    return render(request, 'checkin/quick_checkin_form.html', context)


def checkin_from_booking(request, booking_id):
    """Check-in from an existing booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if already checked in
    existing_checkin = CheckIn.objects.filter(booking=booking).first()
    if existing_checkin:
        messages.info(request, f'This booking is already checked in (ID: {existing_checkin.check_in_id})')
        return redirect('checkin-detail', checkin_id=existing_checkin.id)
    
    return redirect('checkin-create') + f'?booking_id={booking_id}'


def checkin_dashboard(request):
    """Check-in dashboard with statistics and recent activity"""
    today = date.today()
    
    # Statistics
    total_checkins = CheckIn.objects.count()
    todays_checkins = CheckIn.objects.filter(actual_check_in_date_time__date=today).count()
    pending_payments = CheckIn.objects.filter(payment_status='PENDING').count()
    unverified_ids = CheckIn.objects.filter(id_proof_verified=False).count()
    
    # Recent check-ins
    recent_checkins = CheckIn.objects.select_related(
        'guest', 'room_number', 'booking'
    ).order_by('-actual_check_in_date_time')[:10]
    
    # Today's check-ins
    todays_checkin_list = CheckIn.objects.filter(
        actual_check_in_date_time__date=today
    ).select_related('guest', 'room_number').order_by('-actual_check_in_date_time')
    
    # Payment status summary
    payment_summary = CheckIn.objects.values('payment_status').annotate(
        count=Count('id')
    ).order_by('payment_status')
    
    # Available rooms for quick check-in
    available_rooms = Room.objects.filter(
        status='AVAILABLE'
    ).count()
    
    context = {
        'today': today,
        'total_checkins': total_checkins,
        'todays_checkins': todays_checkins,
        'pending_payments': pending_payments,
        'unverified_ids': unverified_ids,
        'recent_checkins': recent_checkins,
        'todays_checkin_list': todays_checkin_list,
        'payment_summary': payment_summary,
        'available_rooms': available_rooms,
    }
    return render(request, 'checkin/dashboard.html', context)


def verify_id_proof(request, checkin_id):
    """Mark ID proof as verified"""
    checkin = get_object_or_404(CheckIn, id=checkin_id)
    
    if request.method == 'POST':
        checkin.id_proof_verified = True
        checkin.save()
        messages.success(request, f'ID proof verified for check-in {checkin.check_in_id}')
    
    return redirect('checkin-detail', checkin_id=checkin.id)


def update_payment_status(request, checkin_id):
    """Update payment status"""
    checkin = get_object_or_404(CheckIn, id=checkin_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('payment_status')
        if new_status in dict(CheckIn.PAYMENT_STATUS_CHOICES):
            checkin.payment_status = new_status
            checkin.save()
            messages.success(request, f'Payment status updated to {checkin.get_payment_status_display()}')
        else:
            messages.error(request, 'Invalid payment status')
    
    return redirect('checkin-detail', checkin_id=checkin.id)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Service, ServiceCharge
from .forms import ServiceForm, ServiceSearchForm, ServiceChargeForm
from guest.models import Guest
from rooms.models import Room
from checkin.models import CheckIn
from booking.models import Booking
from decimal import Decimal


def service_list(request):
    """Display list of all services with search and filter functionality"""
    search_query = request.GET.get('search', '')
    availability_filter = request.GET.get('availability', '')
    tax_filter = request.GET.get('tax_applicable', '')
    active_filter = request.GET.get('is_active', '')
    
    services = Service.objects.all()
    
    # Apply search filter
    if search_query:
        services = services.filter(
            Q(service_name__icontains=search_query) |
            Q(service_id__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Apply availability filter
    if availability_filter:
        services = services.filter(availability=availability_filter)
    
    # Apply tax filter
    if tax_filter:
        if tax_filter == 'true':
            services = services.filter(tax_applicable=True)
        elif tax_filter == 'false':
            services = services.filter(tax_applicable=False)
    
    # Apply active filter
    if active_filter:
        if active_filter == 'true':
            services = services.filter(is_active=True)
        elif active_filter == 'false':
            services = services.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(services, 10)  # Show 10 services per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get choices for filter dropdowns
    availability_choices = Service.AVAILABILITY_CHOICES
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'availability_filter': availability_filter,
        'tax_filter': tax_filter,
        'active_filter': active_filter,
        'availability_choices': availability_choices,
        'total_services': services.count()
    }
    return render(request, 'service/service_list.html', context)


def service_detail(request, service_id):
    """Display detailed view of a specific service"""
    service = get_object_or_404(Service, id=service_id)
    context = {'service': service}
    return render(request, 'service/service_detail.html', context)


def service_create(request):
    """Create a new service"""
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Service "{service.service_name}" created successfully!')
            return redirect('service-detail', service_id=service.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ServiceForm()
    
    context = {
        'form': form,
        'title': 'Create New Service'
    }
    return render(request, 'service/service_form.html', context)


def service_update(request, service_id):
    """Update an existing service"""
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Service "{service.service_name}" updated successfully!')
            return redirect('service-detail', service_id=service.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ServiceForm(instance=service)
    
    context = {
        'form': form,
        'service': service,
        'title': f'Edit {service.service_name}'
    }
    return render(request, 'service/service_form.html', context)


def service_delete(request, service_id):
    """Delete a service"""
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        service_name = service.service_name
        service.delete()
        messages.success(request, f'Service "{service_name}" deleted successfully!')
        return redirect('service-list')
    
    context = {'service': service}
    return render(request, 'service/service_confirm_delete.html', context)


def service_bill(request, service_id=None):
    """Create a bill/charge for a service to a guest (and optionally a booking)."""
    service_instance = None
    if service_id:
        service_instance = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        form = ServiceChargeForm(request.POST, service_instance=service_instance)
        if form.is_valid():
            charge: ServiceCharge = form.save(commit=False)
            # Ensure unit price and tax are reasonable if missing
            if not charge.unit_price:
                charge.unit_price = charge.service.rate_cost
            if charge.tax_rate is None:
                charge.tax_rate = Decimal('18.00') if charge.service.tax_applicable else Decimal('0.00')
            charge.save()
            messages.success(request, f'Service charge created: ₹{charge.total_amount}')
            # Redirect to service list or booking detail if provided
            if charge.booking_id:
                return redirect('booking-detail', booking_id=charge.booking_id)
            return redirect('service-list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ServiceChargeForm(service_instance=service_instance)

    context = {
        'form': form,
        'service_instance': service_instance,
        'title': 'Bill Customer for Service'
    }
    return render(request, 'service/service_bill_form.html', context)


def get_room_guest_info(request, room_id):
    """AJAX endpoint to get guest information for a selected room"""
    try:
        room = get_object_or_404(Room, id=room_id)
        
        # Find the current check-in for this room (most recent one without checkout)
        current_checkin = CheckIn.objects.filter(
            room_number=room
        ).order_by('-actual_check_in_date_time').first()
        
        # Debug: Let's also check if there are any check-ins for this room
        all_checkins = CheckIn.objects.filter(room_number=room).count()
        
        if current_checkin:
            guest = current_checkin.guest
            booking = current_checkin.booking
            
            guest_data = {
                'id': guest.guest_id,
                'full_name': guest.full_name,
                'phone_number': guest.contact_number or 'Not provided',
                'email': guest.email or 'Not provided',
            }
            
            booking_data = None
            if booking:
                booking_data = {
                    'id': booking.id,
                    'check_in_date': booking.check_in_date.strftime('%Y-%m-%d'),
                    'check_out_date': booking.check_out_date.strftime('%Y-%m-%d'),
                }
            
            return JsonResponse({
                'success': True,
                'guest': guest_data,
                'booking': booking_data,
                'room': {
                    'number': room.room_number,
                    'type': room.room_type.name if room.room_type else 'N/A'
                },
                'debug': {
                    'total_checkins': all_checkins,
                    'checkin_id': current_checkin.check_in_id,
                    'checkin_date': current_checkin.actual_check_in_date_time.strftime('%Y-%m-%d %H:%M')
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'No check-ins found for this room (Total check-ins in system: {all_checkins})',
                'debug': {
                    'room_id': room_id,
                    'room_number': room.room_number,
                    'room_status': room.status,
                    'total_checkins_for_room': all_checkins
                }
            })
            
    except Room.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Room not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })
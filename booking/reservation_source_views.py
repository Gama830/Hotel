from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import ReservationSource
from .forms import ReservationSourceForm

def reservation_source_list(request):
    """Display list of all reservation sources"""
    search_query = request.GET.get('search', '')
    source_type_filter = request.GET.get('source_type', '')
    
    sources = ReservationSource.objects.all()
    
    # Apply search filter
    if search_query:
        sources = sources.filter(
            Q(name__icontains=search_query) |
            Q(source_id__icontains=search_query) |
            Q(contact_person__icontains=search_query)
        )
    
    # Apply source type filter
    if source_type_filter:
        sources = sources.filter(source_type=source_type_filter)
    
    # Pagination
    paginator = Paginator(sources, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get source type choices for filter dropdown
    source_type_choices = ReservationSource.SOURCE_TYPE_CHOICES
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'source_type_filter': source_type_filter,
        'source_type_choices': source_type_choices,
        'total_sources': sources.count()
    }
    return render(request, 'booking/reservation_source_list.html', context)

def reservation_source_detail(request, source_id):
    """Display detailed view of a specific reservation source"""
    source = get_object_or_404(ReservationSource, id=source_id)
    
    # Get booking statistics
    bookings = source.bookings.all()
    total_bookings = bookings.count()
    recent_bookings = bookings.order_by('-created_at')[:10]
    
    # Calculate revenue and commission
    total_revenue = sum(booking.total_amount for booking in bookings)
    total_commission = 0
    if source.commission_rate > 0:
        total_commission = (total_revenue * source.commission_rate) / 100
    
    context = {
        'source': source,
        'total_bookings': total_bookings,
        'recent_bookings': recent_bookings,
        'total_revenue': total_revenue,
        'total_commission': total_commission,
    }
    return render(request, 'booking/reservation_source_detail.html', context)

def reservation_source_create(request):
    """Create a new reservation source"""
    if request.method == 'POST':
        form = ReservationSourceForm(request.POST)
        if form.is_valid():
            source = form.save()
            messages.success(request, f'Reservation Source "{source.name}" created successfully!')
            return redirect('reservation-source-detail', source_id=source.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReservationSourceForm()
    
    context = {
        'form': form,
        'title': 'Create New Reservation Source',
        'submit_text': 'Create Source'
    }
    return render(request, 'booking/reservation_source_form.html', context)

def reservation_source_update(request, source_id):
    """Update an existing reservation source"""
    source = get_object_or_404(ReservationSource, id=source_id)
    
    if request.method == 'POST':
        form = ReservationSourceForm(request.POST, instance=source)
        if form.is_valid():
            source = form.save()
            messages.success(request, f'Reservation Source "{source.name}" updated successfully!')
            return redirect('reservation-source-detail', source_id=source.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReservationSourceForm(instance=source)
    
    context = {
        'form': form,
        'source': source,
        'title': f'Edit Reservation Source: {source.name}',
        'submit_text': 'Update Source'
    }
    return render(request, 'booking/reservation_source_form.html', context)

def reservation_source_delete(request, source_id):
    """Delete a reservation source"""
    source = get_object_or_404(ReservationSource, id=source_id)
    
    if request.method == 'POST':
        source_name = source.name
        source.delete()
        messages.success(request, f'Reservation Source "{source_name}" deleted successfully!')
        return redirect('reservation-source-list')
    
    context = {'source': source}
    return render(request, 'booking/reservation_source_confirm_delete.html', context)
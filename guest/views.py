from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Guest
from .forms import GuestForm

def guest_list(request):
    """Display list of all guests with search functionality"""
    search_query = request.GET.get('search', '')
    guests = Guest.objects.all()
    
    if search_query:
        guests = guests.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(contact_number__icontains=search_query) |
            Q(member_id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(guests, 10)  # Show 10 guests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_guests': guests.count()
    }
    return render(request, 'guest/guest_list.html', context)

def guest_detail(request, guest_id):
    """Display detailed view of a specific guest"""
    guest = get_object_or_404(Guest, guest_id=guest_id)
    context = {'guest': guest}
    return render(request, 'guest/guest_detail.html', context)

def guest_create(request):
    """Create a new guest"""
    if request.method == 'POST':
        form = GuestForm(request.POST)
        if form.is_valid():
            guest = form.save()
            messages.success(request, f'Guest {guest.full_name} created successfully!')
            return redirect('guest-detail', guest_id=guest.guest_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = GuestForm()
    
    context = {
        'form': form,
        'title': 'Add New Guest',
        'submit_text': 'Create Guest'
    }
    return render(request, 'guest/guest_form.html', context)

def guest_update(request, guest_id):
    """Update an existing guest"""
    guest = get_object_or_404(Guest, guest_id=guest_id)
    
    if request.method == 'POST':
        form = GuestForm(request.POST, instance=guest)
        if form.is_valid():
            guest = form.save()
            messages.success(request, f'Guest {guest.full_name} updated successfully!')
            return redirect('guest-detail', guest_id=guest.guest_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = GuestForm(instance=guest)
    
    context = {
        'form': form,
        'guest': guest,
        'title': f'Edit Guest - {guest.full_name}',
        'submit_text': 'Update Guest'
    }
    return render(request, 'guest/guest_form.html', context)

def guest_delete(request, guest_id):
    """Delete a guest"""
    guest = get_object_or_404(Guest, guest_id=guest_id)
    
    if request.method == 'POST':
        guest_name = guest.full_name
        guest.delete()
        messages.success(request, f'Guest {guest_name} deleted successfully!')
        return redirect('guest-list')
    
    context = {'guest': guest}
    return render(request, 'guest/guest_confirm_delete.html', context)
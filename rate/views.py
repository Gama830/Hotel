from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import date
from .models import RatePlan
from .forms import RatePlanForm, RatePlanSearchForm, RateCalculatorForm
from rooms.models import RoomType

def rate_plan_list(request):
    """Display list of all rate plans with search and filter functionality"""
    form = RatePlanSearchForm(request.GET or None)
    rate_plans = RatePlan.objects.select_related('room_type').all()
    
    # Apply filters
    if form.is_valid():
        room_type = form.cleaned_data.get('room_type')
        season_type = form.cleaned_data.get('season_type')
        meal_plan = form.cleaned_data.get('meal_plan')
        is_active = form.cleaned_data.get('is_active')
        date_from = form.cleaned_data.get('date_from')
        
        if room_type:
            rate_plans = rate_plans.filter(room_type=room_type)
        
        if season_type:
            rate_plans = rate_plans.filter(season_type=season_type)
        
        if meal_plan:
            rate_plans = rate_plans.filter(meal_plan=meal_plan)
        
        if is_active == 'true':
            rate_plans = rate_plans.filter(is_active=True)
        elif is_active == 'false':
            rate_plans = rate_plans.filter(is_active=False)
        
        if date_from:
            rate_plans = rate_plans.filter(valid_to__gte=date_from)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        rate_plans = rate_plans.filter(
            Q(rate_name__icontains=search_query) |
            Q(room_type__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(rate_plans, 10)  # Show 10 rate plans per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'search_query': search_query,
        'total_rate_plans': rate_plans.count()
    }
    return render(request, 'rate/rate_plan_list.html', context)

def rate_plan_detail(request, rate_plan_id):
    """Display detailed view of a specific rate plan"""
    rate_plan = get_object_or_404(
        RatePlan.objects.select_related('room_type'),
        rate_plan_id=rate_plan_id
    )
    context = {'rate_plan': rate_plan}
    return render(request, 'rate/rate_plan_detail.html', context)

def rate_plan_create(request):
    """Create a new rate plan"""
    if request.method == 'POST':
        form = RatePlanForm(request.POST)
        if form.is_valid():
            rate_plan = form.save()
            messages.success(request, f'Rate plan "{rate_plan.rate_name}" created successfully!')
            return redirect('rate-plan-detail', rate_plan_id=rate_plan.rate_plan_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RatePlanForm()
    
    context = {
        'form': form,
        'title': 'Create New Rate Plan',
        'submit_text': 'Create Rate Plan'
    }
    return render(request, 'rate/rate_plan_form.html', context)

def rate_plan_update(request, rate_plan_id):
    """Update an existing rate plan"""
    rate_plan = get_object_or_404(RatePlan, rate_plan_id=rate_plan_id)
    
    if request.method == 'POST':
        form = RatePlanForm(request.POST, instance=rate_plan)
        if form.is_valid():
            rate_plan = form.save()
            messages.success(request, f'Rate plan "{rate_plan.rate_name}" updated successfully!')
            return redirect('rate-plan-detail', rate_plan_id=rate_plan.rate_plan_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RatePlanForm(instance=rate_plan)
    
    context = {
        'form': form,
        'rate_plan': rate_plan,
        'title': f'Edit Rate Plan - {rate_plan.rate_name}',
        'submit_text': 'Update Rate Plan'
    }
    return render(request, 'rate/rate_plan_form.html', context)

def rate_plan_delete(request, rate_plan_id):
    """Delete a rate plan"""
    rate_plan = get_object_or_404(RatePlan, rate_plan_id=rate_plan_id)
    
    if request.method == 'POST':
        rate_plan_name = rate_plan.rate_name
        rate_plan.delete()
        messages.success(request, f'Rate plan "{rate_plan_name}" deleted successfully!')
        return redirect('rate-plan-list')
    
    context = {'rate_plan': rate_plan}
    return render(request, 'rate/rate_plan_confirm_delete.html', context)

def rate_calculator(request):
    """Calculate rates for given parameters"""
    form = RateCalculatorForm(request.GET or None)
    calculated_rates = []
    
    if form.is_valid():
        room_type = form.cleaned_data['room_type']
        check_in_date = form.cleaned_data['check_in_date']
        check_out_date = form.cleaned_data['check_out_date']
        number_of_guests = form.cleaned_data['number_of_guests']
        include_meals = form.cleaned_data['include_meals']
        
        nights = (check_out_date - check_in_date).days
        
        # Find applicable rate plans
        applicable_rates = RatePlan.objects.filter(
            room_type=room_type,
            is_active=True,
            valid_from__lte=check_in_date,
            valid_to__gte=check_out_date,
            minimum_stay__lte=nights
        )
        
        # Filter by maximum stay if specified
        applicable_rates = applicable_rates.filter(
            Q(maximum_stay__isnull=True) | Q(maximum_stay__gte=nights)
        )
        
        for rate_plan in applicable_rates:
            total_cost = rate_plan.calculate_total_rate(
                nights=nights,
                guests=number_of_guests,
                include_meal=include_meals
            )
            
            calculated_rates.append({
                'rate_plan': rate_plan,
                'total_cost': total_cost,
                'cost_per_night': total_cost / nights if nights > 0 else 0,
                'nights': nights,
                'guests': number_of_guests
            })
        
        # Sort by total cost
        calculated_rates.sort(key=lambda x: x['total_cost'])
    
    context = {
        'form': form,
        'calculated_rates': calculated_rates,
        'calculation_performed': form.is_valid()
    }
    return render(request, 'rate/rate_calculator.html', context)

def rate_plan_toggle_status(request, rate_plan_id):
    """Toggle active status of a rate plan"""
    rate_plan = get_object_or_404(RatePlan, rate_plan_id=rate_plan_id)
    
    rate_plan.is_active = not rate_plan.is_active
    rate_plan.save()
    
    status = "activated" if rate_plan.is_active else "deactivated"
    messages.success(request, f'Rate plan "{rate_plan.rate_name}" {status} successfully!')
    
    return redirect('rate-plan-detail', rate_plan_id=rate_plan.rate_plan_id)

def current_rates(request):
    """Display currently valid rate plans"""
    today = date.today()
    current_rate_plans = RatePlan.objects.filter(
        is_active=True,
        valid_from__lte=today,
        valid_to__gte=today
    ).select_related('room_type').order_by('room_type__name', 'base_rate')
    
    # Group by room type
    rates_by_room_type = {}
    for rate_plan in current_rate_plans:
        room_type_name = rate_plan.room_type.name
        if room_type_name not in rates_by_room_type:
            rates_by_room_type[room_type_name] = []
        rates_by_room_type[room_type_name].append(rate_plan)
    
    context = {
        'rates_by_room_type': rates_by_room_type,
        'today': today
    }
    return render(request, 'rate/current_rates.html', context)
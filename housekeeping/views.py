from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import date, timedelta
from .models import HousekeepingStatus, HousekeepingTask, HousekeepingInspection
from .forms import HousekeepingStatusForm, HousekeepingTaskForm, HousekeepingInspectionForm, TaskUpdateForm
from rooms.models import Room

# Housekeeping Status Views
def housekeeping_status_list(request):
    """Display list of all housekeeping statuses"""
    search_query = request.GET.get('search', '')
    
    statuses = HousekeepingStatus.objects.all()
    
    # Apply search filter
    if search_query:
        statuses = statuses.filter(
            Q(status_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(statuses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_statuses': statuses.count()
    }
    return render(request, 'housekeeping/status_list.html', context)

def housekeeping_status_create(request):
    """Create a new housekeeping status"""
    if request.method == 'POST':
        form = HousekeepingStatusForm(request.POST)
        if form.is_valid():
            status = form.save()
            messages.success(request, f'Housekeeping Status "{status.display_name}" created successfully!')
            return redirect('housekeeping-status-detail', status_id=status.status_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HousekeepingStatusForm()
    
    context = {
        'form': form,
        'title': 'Create New Housekeeping Status',
        'submit_text': 'Create Status'
    }
    return render(request, 'housekeeping/status_form.html', context)

def housekeeping_status_detail(request, status_id):
    """Display detailed view of a housekeeping status"""
    status = get_object_or_404(HousekeepingStatus, status_id=status_id)
    
    # Get related tasks
    recent_tasks = status.tasks.select_related('room').order_by('-created_at')[:10]
    total_tasks = status.tasks.count()
    
    context = {
        'status': status,
        'recent_tasks': recent_tasks,
        'total_tasks': total_tasks,
    }
    return render(request, 'housekeeping/status_detail.html', context)

def housekeeping_status_update(request, status_id):
    """Update an existing housekeeping status"""
    status = get_object_or_404(HousekeepingStatus, status_id=status_id)
    
    if request.method == 'POST':
        form = HousekeepingStatusForm(request.POST, instance=status)
        if form.is_valid():
            status = form.save()
            messages.success(request, f'Housekeeping Status "{status.display_name}" updated successfully!')
            return redirect('housekeeping-status-detail', status_id=status.status_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HousekeepingStatusForm(instance=status)
    
    context = {
        'form': form,
        'status': status,
        'title': f'Edit Housekeeping Status: {status.display_name}',
        'submit_text': 'Update Status'
    }
    return render(request, 'housekeeping/status_form.html', context)

# Housekeeping Task Views
def housekeeping_task_list(request):
    """Display list of all housekeeping tasks"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    date_filter = request.GET.get('date', '')
    
    tasks = HousekeepingTask.objects.select_related('room', 'status').all()
    
    # Apply filters
    if search_query:
        tasks = tasks.filter(
            Q(room__room_number__icontains=search_query) |
            Q(task_type__icontains=search_query) |
            Q(assigned_to__icontains=search_query)
        )
    
    if status_filter:
        tasks = tasks.filter(task_status=status_filter)
    
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    if date_filter:
        if date_filter == 'today':
            tasks = tasks.filter(scheduled_date=date.today())
        elif date_filter == 'tomorrow':
            tasks = tasks.filter(scheduled_date=date.today() + timedelta(days=1))
        elif date_filter == 'overdue':
            tasks = tasks.filter(
                scheduled_date__lt=date.today(),
                task_status__in=['PENDING', 'IN_PROGRESS']
            )
    
    # Pagination
    paginator = Paginator(tasks, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter choices
    status_choices = HousekeepingTask.TASK_STATUS_CHOICES
    priority_choices = HousekeepingTask.PRIORITY_CHOICES
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'date_filter': date_filter,
        'status_choices': status_choices,
        'priority_choices': priority_choices,
        'total_tasks': tasks.count()
    }
    return render(request, 'housekeeping/task_list.html', context)

def housekeeping_task_create(request):
    """Create a new housekeeping task"""
    if request.method == 'POST':
        form = HousekeepingTaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Housekeeping Task for Room {task.room.room_number} created successfully!')
            return redirect('housekeeping-task-detail', task_id=task.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HousekeepingTaskForm()
    
    context = {
        'form': form,
        'title': 'Create New Housekeeping Task',
        'submit_text': 'Create Task'
    }
    return render(request, 'housekeeping/task_form.html', context)

def housekeeping_task_detail(request, task_id):
    """Display detailed view of a housekeeping task"""
    task = get_object_or_404(
        HousekeepingTask.objects.select_related('room', 'status'),
        id=task_id
    )
    
    # Get related inspections
    inspections = task.inspections.order_by('-inspection_date')
    
    context = {
        'task': task,
        'inspections': inspections,
    }
    return render(request, 'housekeeping/task_detail.html', context)

def housekeeping_task_update(request, task_id):
    """Update an existing housekeeping task"""
    task = get_object_or_404(HousekeepingTask, id=task_id)
    
    if request.method == 'POST':
        form = HousekeepingTaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Housekeeping Task for Room {task.room.room_number} updated successfully!')
            return redirect('housekeeping-task-detail', task_id=task.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HousekeepingTaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'title': f'Edit Task: Room {task.room.room_number}',
        'submit_text': 'Update Task'
    }
    return render(request, 'housekeeping/task_form.html', context)

def housekeeping_task_update_status(request, task_id):
    """Quick update task status"""
    task = get_object_or_404(HousekeepingTask, id=task_id)
    
    if request.method == 'POST':
        form = TaskUpdateForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            
            # Set timestamps based on status
            if task.task_status == 'IN_PROGRESS' and not task.started_at:
                task.started_at = timezone.now()
            elif task.task_status == 'COMPLETED' and not task.completed_at:
                task.completed_at = timezone.now()
            
            task.save()
            messages.success(request, f'Task status updated successfully!')
            return redirect('housekeeping-task-detail', task_id=task.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskUpdateForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'title': f'Update Task Status: Room {task.room.room_number}',
        'submit_text': 'Update Status'
    }
    return render(request, 'housekeeping/task_update_form.html', context)

# Housekeeping Inspection Views
def housekeeping_inspection_list(request):
    """Display list of all housekeeping inspections"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    inspections = HousekeepingInspection.objects.select_related('room', 'task').all()
    
    # Apply filters
    if search_query:
        inspections = inspections.filter(
            Q(room__room_number__icontains=search_query) |
            Q(inspector_name__icontains=search_query)
        )
    
    if status_filter:
        inspections = inspections.filter(inspection_status=status_filter)
    
    # Pagination
    paginator = Paginator(inspections, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter choices
    status_choices = HousekeepingInspection.INSPECTION_STATUS_CHOICES
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': status_choices,
        'total_inspections': inspections.count()
    }
    return render(request, 'housekeeping/inspection_list.html', context)

def housekeeping_inspection_create(request):
    """Create a new housekeeping inspection"""
    if request.method == 'POST':
        form = HousekeepingInspectionForm(request.POST)
        if form.is_valid():
            inspection = form.save()
            messages.success(request, f'Inspection for Room {inspection.room.room_number} created successfully!')
            return redirect('housekeeping-inspection-detail', inspection_id=inspection.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HousekeepingInspectionForm()
    
    context = {
        'form': form,
        'title': 'Create New Inspection',
        'submit_text': 'Create Inspection'
    }
    return render(request, 'housekeeping/inspection_form.html', context)

def housekeeping_inspection_detail(request, inspection_id):
    """Display detailed view of a housekeeping inspection"""
    inspection = get_object_or_404(
        HousekeepingInspection.objects.select_related('room', 'task'),
        id=inspection_id
    )
    
    context = {
        'inspection': inspection,
    }
    return render(request, 'housekeeping/inspection_detail.html', context)

# Dashboard View
def housekeeping_dashboard(request):
    """Housekeeping dashboard with overview and statistics"""
    today = date.today()
    
    # Task statistics
    total_tasks = HousekeepingTask.objects.count()
    pending_tasks = HousekeepingTask.objects.filter(task_status='PENDING').count()
    in_progress_tasks = HousekeepingTask.objects.filter(task_status='IN_PROGRESS').count()
    completed_today = HousekeepingTask.objects.filter(
        task_status='COMPLETED',
        completed_at__date=today
    ).count()
    
    # Overdue tasks
    overdue_tasks = HousekeepingTask.objects.filter(
        scheduled_date__lt=today,
        task_status__in=['PENDING', 'IN_PROGRESS']
    ).count()
    
    # Today's tasks
    todays_tasks = HousekeepingTask.objects.filter(
        scheduled_date=today
    ).select_related('room', 'status').order_by('scheduled_time', 'priority')
    
    # Recent inspections
    recent_inspections = HousekeepingInspection.objects.select_related(
        'room', 'task'
    ).order_by('-inspection_date')[:10]
    
    # Room status summary
    room_status_summary = HousekeepingStatus.objects.annotate(
        task_count=Count('tasks')
    ).filter(is_active=True)
    
    context = {
        'today': today,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_today': completed_today,
        'overdue_tasks': overdue_tasks,
        'todays_tasks': todays_tasks,
        'recent_inspections': recent_inspections,
        'room_status_summary': room_status_summary,
    }
    return render(request, 'housekeeping/dashboard.html', context)
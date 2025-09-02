from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CorporateAgent
from .forms import CorporateAgentForm

def corporate_agent_list(request):
    """Display list of all corporate clients and agents"""
    search_query = request.GET.get('search', '')
    agent_type_filter = request.GET.get('agent_type', '')
    
    agents = CorporateAgent.objects.all()
    
    # Apply search filter
    if search_query:
        agents = agents.filter(
            Q(name__icontains=search_query) |
            Q(agent_id__icontains=search_query) |
            Q(contact_person__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(city__icontains=search_query)
        )
    
    # Apply agent type filter
    if agent_type_filter:
        agents = agents.filter(agent_type=agent_type_filter)
    
    # Pagination
    paginator = Paginator(agents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get agent type choices for filter dropdown
    agent_type_choices = CorporateAgent.AGENT_TYPE_CHOICES
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'agent_type_filter': agent_type_filter,
        'agent_type_choices': agent_type_choices,
        'total_agents': agents.count()
    }
    return render(request, 'booking/corporate_agent_list.html', context)

def corporate_agent_detail(request, agent_id):
    """Display detailed view of a specific corporate agent"""
    agent = get_object_or_404(CorporateAgent, id=agent_id)
    context = {'agent': agent}
    return render(request, 'booking/corporate_agent_detail.html', context)

def corporate_agent_create(request):
    """Create a new corporate agent"""
    if request.method == 'POST':
        form = CorporateAgentForm(request.POST)
        if form.is_valid():
            agent = form.save()
            messages.success(request, f'Corporate/Agent "{agent.name}" created successfully!')
            return redirect('corporate-agent-detail', agent_id=agent.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CorporateAgentForm()
    
    context = {
        'form': form,
        'title': 'Create New Corporate/Agent',
        'submit_text': 'Create Corporate/Agent'
    }
    return render(request, 'booking/corporate_agent_form.html', context)

def corporate_agent_update(request, agent_id):
    """Update an existing corporate agent"""
    agent = get_object_or_404(CorporateAgent, id=agent_id)
    
    if request.method == 'POST':
        form = CorporateAgentForm(request.POST, instance=agent)
        if form.is_valid():
            agent = form.save()
            messages.success(request, f'Corporate/Agent "{agent.name}" updated successfully!')
            return redirect('corporate-agent-detail', agent_id=agent.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CorporateAgentForm(instance=agent)
    
    context = {
        'form': form,
        'agent': agent,
        'title': f'Edit Corporate/Agent: {agent.name}',
        'submit_text': 'Update Corporate/Agent'
    }
    return render(request, 'booking/corporate_agent_form.html', context)

def corporate_agent_delete(request, agent_id):
    """Delete a corporate agent"""
    agent = get_object_or_404(CorporateAgent, id=agent_id)
    
    if request.method == 'POST':
        agent_name = agent.name
        agent.delete()
        messages.success(request, f'Corporate/Agent "{agent_name}" deleted successfully!')
        return redirect('corporate-agent-list')
    
    context = {'agent': agent}
    return render(request, 'booking/corporate_agent_confirm_delete.html', context)
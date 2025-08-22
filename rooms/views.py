from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.contrib import messages
from django.http import JsonResponse
from .models import Room, RoomType
from .forms import RoomForm, RoomTypeForm

class RoomCreateView(CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'rooms/room_form.html'
    success_url = reverse_lazy('room-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Room created successfully!')
        return super().form_valid(form)

class RoomUpdateView(UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'rooms/room_form.html'
    success_url = reverse_lazy('room-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Room {self.object.room_number} updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

class RoomDeleteView(DeleteView):
    model = Room
    template_name = 'rooms/room_confirm_delete.html'
    success_url = reverse_lazy('room-list')
    
    def delete(self, request, *args, **kwargs):
        room = self.get_object()
        messages.success(request, f'Room {room.room_number} deleted successfully!')
        return super().delete(request, *args, **kwargs)

class RoomListView(ListView):
    model = Room
    template_name = 'rooms/room_list.html'
    context_object_name = 'rooms'
    paginate_by = 10

# Room Type Views
class RoomTypeListView(ListView):
    model = RoomType
    template_name = 'rooms/roomtype_list.html'
    context_object_name = 'room_types'
    paginate_by = 10

class RoomTypeCreateView(CreateView):
    model = RoomType
    form_class = RoomTypeForm
    template_name = 'rooms/roomtype_form.html'
    success_url = reverse_lazy('roomtype-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Room Type created successfully!')
        return super().form_valid(form)

class RoomTypeUpdateView(UpdateView):
    model = RoomType
    form_class = RoomTypeForm
    template_name = 'rooms/roomtype_form.html'
    success_url = reverse_lazy('roomtype-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Room Type "{self.object.name}" updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

class RoomTypeDeleteView(DeleteView):
    model = RoomType
    template_name = 'rooms/roomtype_confirm_delete.html'
    success_url = reverse_lazy('roomtype-list')
    
    def delete(self, request, *args, **kwargs):
        room_type = self.get_object()
        messages.success(request, f'Room Type "{room_type.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)

# API endpoint for room type details
def get_room_type_details(request, room_type_id):
    """AJAX endpoint to get room type details for auto-filling form fields"""
    try:
        room_type = RoomType.objects.get(id=room_type_id)
        data = {
            'bed_type': room_type.bed_type,
            'max_occupancy': room_type.capacity,
            'rate_default': float(room_type.price_per_night),
            'bed_type_display': room_type.get_bed_type_display()
        }
        return JsonResponse(data)
    except RoomType.DoesNotExist:
        return JsonResponse({'error': 'Room type not found'}, status=404)
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.contrib import messages
from .models import Amenity
from .forms import AmenityForm

class AmenityListView(ListView):
    model = Amenity
    template_name = 'amenities/amenity_list.html'
    context_object_name = 'amenities'
    paginate_by = 10

class AmenityCreateView(CreateView):
    model = Amenity
    form_class = AmenityForm
    template_name = 'amenities/amenity_form.html'
    success_url = reverse_lazy('amenity-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Amenity created successfully!')
        return super().form_valid(form)

class AmenityUpdateView(UpdateView):
    model = Amenity
    form_class = AmenityForm
    template_name = 'amenities/amenity_form.html'
    success_url = reverse_lazy('amenity-list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Amenity "{self.object.name}" updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

class AmenityDeleteView(DeleteView):
    model = Amenity
    template_name = 'amenities/amenity_confirm_delete.html'
    success_url = reverse_lazy('amenity-list')
    
    def delete(self, request, *args, **kwargs):
        amenity = self.get_object()
        messages.success(request, f'Amenity "{amenity.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)

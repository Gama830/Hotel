// Booking Form JavaScript

// Global variables
let reservationSources = [];
let selectedSourceId = null;

// Auto-calculate total amount when dates or room changes
function initializeAmountCalculation() {
    const checkInDate = document.querySelector('#id_check_in_date');
    const checkOutDate = document.querySelector('#id_check_out_date');
    const roomSelect = document.querySelector('#id_room');
    const ratePlanSelect = document.querySelector('#id_rate_plan');
    const totalAmountField = document.querySelector('#id_total_amount');
    const adultsField = document.querySelector('#id_number_of_adults');
    const childrenField = document.querySelector('#id_number_of_children');
    
    function calculateTotal() {
        if (checkInDate.value && checkOutDate.value && roomSelect.value) {
            const checkIn = new Date(checkInDate.value);
            const checkOut = new Date(checkOutDate.value);
            const nights = Math.ceil((checkOut - checkIn) / (1000 * 60 * 60 * 24));
            
            if (nights > 0) {
                // Make AJAX call to get calculated amount
                const formData = new FormData();
                formData.append('check_in_date', checkInDate.value);
                formData.append('check_out_date', checkOutDate.value);
                formData.append('room', roomSelect.value);
                formData.append('rate_plan', ratePlanSelect.value || '');
                formData.append('number_of_adults', adultsField.value || '1');
                formData.append('number_of_children', childrenField.value || '0');
                formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
                
                fetch('/bookings/calculate-amount/', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.total_amount) {
                        totalAmountField.value = data.total_amount;
                        totalAmountField.style.backgroundColor = '#d4edda';
                        
                        // Show calculation details
                        const helpText = totalAmountField.parentNode.querySelector('small');
                        if (helpText) {
                            helpText.textContent = `${nights} nights × ₹${data.rate_per_night} = ₹${data.total_amount}`;
                            helpText.style.color = '#28a745';
                        }
                    }
                })
                .catch(error => {
                    console.error('Error calculating amount:', error);
                    totalAmountField.style.backgroundColor = '#fff3cd';
                    totalAmountField.placeholder = 'Will be calculated on save';
                });
            }
        }
    }
    
    // Add event listeners
    [checkInDate, checkOutDate, roomSelect, ratePlanSelect, adultsField, childrenField].forEach(field => {
        if (field) {
            field.addEventListener('change', calculateTotal);
        }
    });
    
    // Calculate on page load if editing
    if (checkInDate.value && checkOutDate.value && roomSelect.value) {
        calculateTotal();
    }
}

// Reservation Source Search Functionality
function initializeReservationSourceSearch() {
    const bookingSourceSelect = document.querySelector('#id_booking_source');
    const reservationSourceInput = document.querySelector('#id_reservation_source');
    const reservationSourceDropdown = document.querySelector('#reservationSourceDropdown');
    const reservationSourceIdInput = document.querySelector('#id_reservation_source_id');
    
    if (!reservationSourceInput) return;
    
    // Fetch reservation sources from server
    async function fetchReservationSources() {
        try {
            const response = await fetch('/bookings/api/reservation-sources/');
            if (response.ok) {
                reservationSources = await response.json();
            }
        } catch (error) {
            console.error('Error fetching reservation sources:', error);
        }
    }
    
    // Filter and display reservation sources
    function filterReservationSources(searchTerm = '') {
        const selectedBookingSource = bookingSourceSelect.value;
        
        // Hide dropdown if booking source is DIRECT
        const reservationSourceDiv = reservationSourceInput.closest('div');
        if (selectedBookingSource === 'DIRECT') {
            reservationSourceDiv.style.display = 'none';
            reservationSourceDropdown.style.display = 'none';
            return;
        } else {
            reservationSourceDiv.style.display = 'block';
        }
        
        // Filter sources based on search term and booking source
        const filteredSources = reservationSources.filter(source => {
            const matchesSearch = searchTerm === '' || 
                source.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                source.source_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                (source.contact_person && source.contact_person.toLowerCase().includes(searchTerm.toLowerCase()));
            
            return matchesSearch && source.is_active;
        });
        
        // Display filtered results
        if (searchTerm && filteredSources.length > 0) {
            reservationSourceDropdown.innerHTML = filteredSources.map(source => `
                <div class="reservation-source-item" data-id="${source.id}" data-name="${source.name}">
                    <div style="font-weight: bold;">${source.name}</div>
                    <div style="font-size: 12px; color: #666;">
                        ${source.source_id} • ${source.source_type_display}
                        ${source.contact_person ? ' • ' + source.contact_person : ''}
                    </div>
                </div>
            `).join('');
            reservationSourceDropdown.style.display = 'block';
        } else if (searchTerm) {
            reservationSourceDropdown.innerHTML = `
                <div style="padding: 10px; color: #666; text-align: center;">
                    No reservation sources found matching "${searchTerm}"
                </div>
            `;
            reservationSourceDropdown.style.display = 'block';
        } else {
            reservationSourceDropdown.style.display = 'none';
        }
    }
    
    // Handle reservation source input
    reservationSourceInput.addEventListener('input', function() {
        const searchTerm = this.value;
        filterReservationSources(searchTerm);
        
        // Clear selection if input is cleared
        if (!searchTerm) {
            selectedSourceId = null;
            reservationSourceIdInput.value = '';
        }
    });
    
    reservationSourceInput.addEventListener('focus', function() {
        if (this.value) {
            filterReservationSources(this.value);
        }
    });
    
    // Handle clicking outside to close dropdown
    document.addEventListener('click', function(event) {
        if (!reservationSourceInput.contains(event.target) && 
            !reservationSourceDropdown.contains(event.target)) {
            reservationSourceDropdown.style.display = 'none';
        }
    });
    
    // Handle clicking on reservation source items
    reservationSourceDropdown.addEventListener('click', function(event) {
        const item = event.target.closest('.reservation-source-item');
        if (item) {
            const sourceId = item.dataset.id;
            const sourceName = item.dataset.name;
            
            reservationSourceInput.value = sourceName;
            reservationSourceIdInput.value = sourceId;
            selectedSourceId = sourceId;
            reservationSourceDropdown.style.display = 'none';
        }
    });
    
    // Handle booking source changes
    if (bookingSourceSelect) {
        bookingSourceSelect.addEventListener('change', function() {
            // Clear reservation source when booking source changes
            reservationSourceInput.value = '';
            reservationSourceIdInput.value = '';
            selectedSourceId = null;
            filterReservationSources();
        });
    }
    
    // Initialize
    fetchReservationSources().then(() => {
        if (bookingSourceSelect) {
            filterReservationSources();
        }
        
        // Pre-populate reservation source if editing
        const existingSourceId = reservationSourceIdInput.value;
        if (existingSourceId && reservationSources.length > 0) {
            const existingSource = reservationSources.find(s => s.id == existingSourceId);
            if (existingSource) {
                reservationSourceInput.value = existingSource.name;
                selectedSourceId = existingSourceId;
            }
        }
    });
}

// Initialize all booking form functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeAmountCalculation();
    initializeReservationSourceSearch();
});
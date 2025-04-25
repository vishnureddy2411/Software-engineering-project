

# In views.py
from django.shortcuts import render,redirect
from .models import Equipment
from sports.models import Location
from bookings.models import Booking
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from datetime import datetime 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import datetime, timedelta
from sports.models import Sport
from bookings.models import Slot

# View to show equipment based on location
@login_required
def user_equipment(request, location_id):
    print(f"[DEBUG] Incoming request path: {request.path}")
    try:
        location = get_object_or_404(Location, location_id=location_id)
        equipment_list = Equipment.objects.filter(location_id=location_id)
        print(f"[DEBUG] Fetched {equipment_list.count()} items for location {location_id}")
    except Location.DoesNotExist:
        print("[ERROR] Location does not exist.")
        messages.error(request, "Location not found.")
        return redirect('home')
    except Exception as e:
        print(f"[ERROR] Couldn't fetch equipment: {e}")
        messages.error(request, "Failed to load equipment.")
        return redirect('home')

    return render(request, 'user_equipment.html', {
        'equipment_list': equipment_list,
        'location': location,  # Needed for template rendering
        'timestamp': datetime.now().timestamp()
    })



@login_required
def select_equipment(request, location_id, slot_id):
    """
    Handles equipment selection and redirects to the payment page, ensuring slot data is pre-populated.
    """
    try:
        # Fetch the location and associated sports
        location = get_object_or_404(Location, location_id=location_id)
        sports = Sport.objects.filter(location_id=location_id)
        equipment_list = Equipment.objects.filter(location_id=location_id)
        all_slots = Slot.objects.filter(location_id=location_id, is_booked=False)  # Fetch all available slots

        # Retrieve the pre-selected slot
        selected_slot = get_object_or_404(Slot, slot_id=slot_id)

        # Validate that sports exist for this location
        if not sports.exists():
            messages.error(request, "No sports associated with this location.")
            return redirect('home')

        # Select the first sport by default
        sport = selected_slot.sport

    except Location.DoesNotExist:
        messages.error(request, "Invalid location.")
        return redirect('home')

    if request.method == 'POST':
        # Retrieve form data
        selected_equipment_id = request.POST.get('equipment')
        quantity = request.POST.get('quantity')
        slot_id = request.POST.get('slot')  # Use the preselected slot

        # Debugging logs
        print(f"Form data received - Equipment: {selected_equipment_id}, Quantity: {quantity}, Slot: {slot_id}")

        if selected_equipment_id and quantity and slot_id:
            try:
                # Validate equipment data and pre-selected slot
                equipment = get_object_or_404(Equipment, equipment_id=selected_equipment_id)
                slot = get_object_or_404(Slot, slot_id=slot_id)  # The selected slot should exist
                quantity = int(quantity)

                if equipment.quantity >= quantity:
                    # Deduct the equipment quantity
                    equipment.quantity -= quantity
                    equipment.save()

                    # Mark the slot as booked
                    slot.is_booked = True
                    slot.save()

                    # Determine price based on peak hours, handle None values
                    current_time = datetime.now().time()
                    price = sport.price
                    if sport.peak_hours_start and sport.peak_hours_end:
                        if sport.peak_hours_start <= current_time <= sport.peak_hours_end:
                            price = sport.peak_price

                    total_price = price * quantity

                    # Create a Booking object
                    booking = Booking.objects.create(
                        user=request.user,
                        location=location,
                        equipment=equipment,
                        quantity=quantity,
                        sport=sport,
                        slot=slot,
                        time_slot=slot.time,  # Use `time` in Slot properly
                    )

                    # Redirect to the payment page with the booking ID
                    messages.success(request, f"Successfully booked {quantity} {equipment.name}(s)!")
                    return redirect('process_payment', booking_id=booking.booking_id)
                else:
                    messages.error(request, f"Not enough stock. Only {equipment.quantity} {equipment.name}(s) available.")
            except Equipment.DoesNotExist:
                messages.error(request, "Selected equipment not found.")
            except ValueError:
                messages.error(request, "Invalid quantity provided.")
        else:
            messages.error(request, "Please select equipment, quantity, and a valid slot.")

    return render(request, 'select_equipment.html', {
        'location': location,
        'equipment_list': equipment_list,
        'slots': all_slots,  # All slots for location
        'selected_slot': selected_slot,  # Prepopulate selected slot
        'sport': sport,  # Pass sport details to the template if needed
        "location_id": location_id,  # Pass location ID explicitly
        "slot_id": slot_id,
        
    })

@never_cache
def get_equipment(request):
    equipment_list = Equipment.objects.all()  # Get all equipment
    equipment_data = [
        {
            'id': equipment.equipment_id,
            'name': equipment.name,
            'quantity': equipment.quantity,
            'price': equipment.price,
            'location' :equipment.location_id
        }
        for equipment in equipment_list
    ]
    return JsonResponse(equipment_data, safe=False)

# Handle invalid equipment paths
def handle_invalid_equipment_path(request, extra):
    print(f"[WARNING] Invalid equipment path accessed: /equipment/{extra}")
    messages.error(request, "Invalid equipment path.")
    return redirect('home')

def create_equipment(request):
    """Create new equipment and add it to the database."""
    print("[DEBUG] Accessing create_equipment view")

    locations = Location.objects.all()  # Fetch all locations

    if request.method == 'POST':
        name = request.POST.get('name')
        quantity = request.POST.get('quantity')
        condition_of_kit = request.POST.get('condition_of_kit', 'Good')
        availability_status = request.POST.get('availability_status', 'Available')
        price = request.POST.get('price')
        location_name = request.POST.get('location_name')  # Get location by name

        print(f"[DEBUG] Received POST data: name={name}, quantity={quantity}, condition={condition_of_kit}, status={availability_status}, price={price}, location_name={location_name}")

        try:
            location = get_object_or_404(Location, name=location_name)  # Find location by name
            Equipment.objects.create(
                name=name,
                quantity=quantity,
                condition_of_kit=condition_of_kit,
                availability_status=availability_status,
                price=price,
                location=location
            )
            print("[DEBUG] Equipment created successfully!")
            messages.success(request, f"Equipment '{name}' added successfully!")
            return redirect('list_equipment')
        except Exception as e:
            print(f"[ERROR] Failed to add equipment: {e}")
            messages.error(request, f"Error adding equipment: {e}")

    return render(request, 'create_equipment.html', {'locations': locations})

def list_equipment(request):
    """Display all equipment available in the database."""
    print("[DEBUG] Accessing list_equipment view")
    equipment_list = Equipment.objects.all()
    print(f"[DEBUG] Found {equipment_list.count()} equipment items.")
    return render(request, 'list_equipment.html', {'equipment_list': equipment_list})


def update_equipment(request, equipment_id):
    """Update existing equipment details."""
    print(f"[DEBUG] Accessing update_equipment view with equipment_id={equipment_id}")
    equipment = get_object_or_404(Equipment, pk=equipment_id)
    locations = Location.objects.all()

    if request.method == 'POST':
        print("[DEBUG] Processing update request")
        equipment.name = request.POST.get('name', equipment.name)
        equipment.quantity = request.POST.get('quantity', equipment.quantity)
        equipment.condition_of_kit = request.POST.get('condition_of_kit', equipment.condition_of_kit)
        equipment.availability_status = request.POST.get('availability_status', equipment.availability_status)
        equipment.price = request.POST.get('price', equipment.price)

        # Validate location_name instead of location_id
        location_name = request.POST.get('location_name')
        if location_name:
            location = get_object_or_404(Location, name=location_name)
            equipment.location = location
        else:
            messages.error(request, "Invalid location selection. Please choose a valid location.")
            return render(request, 'update_equipment.html', {'equipment': equipment, 'locations': locations})

        equipment.save()
        print(f"[DEBUG] Equipment '{equipment.name}' updated successfully!")
        messages.success(request, f"Equipment '{equipment.name}' updated successfully!")
        return redirect('list_equipment')

    return render(request, 'update_equipment.html', {'equipment': equipment, 'locations': locations})

def delete_equipment(request, equipment_id):
    """Delete equipment from the database."""
    print(f"[DEBUG] Accessing delete_equipment view with equipment_id={equipment_id}")

    try:
        equipment = get_object_or_404(Equipment, pk=equipment_id)
        print(f"[DEBUG] Deleting equipment: {equipment.name}")
        equipment.delete()
        print("[DEBUG] Equipment deleted successfully")
        messages.success(request, f"Equipment '{equipment.name}' deleted successfully!")
    except Exception as e:
        print(f"[ERROR] Error deleting equipment: {e}")
        messages.error(request, f"Error deleting equipment: {e}")
    
    return redirect('list_equipment')







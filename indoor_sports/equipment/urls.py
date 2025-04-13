
from django.urls import path
from equipment import views

urlpatterns = [
    # List Equipment (View all)
    path('equipment/', views.list_equipment, name='list_equipment'),
    
    # Create Equipment (Add)
    path('equipment/create/', views.create_equipment, name='create_equipment'),
    
    # Update Equipment (Edit)
    path('equipment/update/<int:equipment_id>/', views.update_equipment, name='update_equipment'),
    
    # Delete Equipment (Delete)
    path('equipment/delete/<int:equipment_id>/', views.delete_equipment, name='delete_equipment'),
    
    # User equipment selection routes
    path('equipment/confirmation/<int:location_id>/', views.user_equipment, name='user_equipment'),
    path('equipment/select/<int:location_id>/<int:slot_id>/', views.select_equipment, name='select_equipment'),
    
    # Optional: Handle truly invalid paths separately (Prevents conflicts)
    path('equipment/invalid/<path:extra>/', views.handle_invalid_equipment_path),

     path('get_equipment/', views.get_equipment, name='get_equipment'),
]

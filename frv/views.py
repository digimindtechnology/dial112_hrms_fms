from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.helpers.basicUtility import GetFileUrl, UploadFileData
from frv.models import FRV,FRVType,FuelType,VehicleStatus
from django.contrib.auth.decorators import login_required
from accounts.helpers.message_helper import send_sweetalert
from django.shortcuts import render, redirect, get_object_or_404
import json
from masters.models import District
from setup.models import PoliceStation
# Create your views here.

@login_required
def frvList(request):
    search_query = request.GET.get('search', '').strip()
    qs = FRV.objects.filter(tenantProfile_id=request.tenantID).select_related('district','status', 'frvType')

    if search_query:
        qs = qs.filter(
            Q(vehicle_id__icontains=search_query) |
            Q(registration_number__icontains=search_query) |
            Q(chassis_number__icontains=search_query) |
            Q(engine_number__icontains=search_query) |
            Q(make__icontains=search_query) |
            Q(model__icontains=search_query) |
            Q(district__district_name__icontains=search_query)
        )

    qs = qs.order_by('-created_date')
    
    total_frv = qs.count()
    active_frv = qs.filter(is_active=True).count()
    inactive_frv = total_frv - active_frv

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'frv/frv_list.html', {
        'page_obj': page_obj,
        'paginator': paginator,
        'search_query': search_query,
        'total_frv': total_frv,
        'active_frv': active_frv,
        'inactive_frv': inactive_frv,
    })
    

@login_required
def frvCreate(request):
    # Get data for dropdowns (no commas at the end!)
    frv_types = FRVType.objects.filter(is_active=True)
    fuel_types = FuelType.objects.filter(is_active=True)
    vehicle_statuses = VehicleStatus.objects.filter(is_active=True)
    districts = District.objects.filter(is_active=True)
    police_stations = PoliceStation.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            frv_images = {}
            
            # Loop through all uploaded files
            uploaded_files = request.FILES.getlist('frv_images')
            for idx, uploaded_file in enumerate(uploaded_files):
                if uploaded_file:
                    # Use UploadFileData to save file
                    stored_path = UploadFileData(
                        request.tenantID, 
                        f'frv_images/{request.POST.get("vehicle_id")}', 
                        uploaded_file, 
                        f'image_{idx+1}_{uploaded_file.name}'
                    )
                    # Store the path (GetFileUrl will be used in template)
                    frv_images[f'image_{idx+1}'] = stored_path
                    
            frv = FRV.objects.create(
                vehicle_id=request.POST.get('vehicle_id'),
                registration_number=request.POST.get('registration_number'),
                registration_date=request.POST.get('registration_date') or None,
                registration_valid_upto=request.POST.get('registration_valid_upto') or None,
                chassis_number=request.POST.get('chassis_number'),
                engine_number=request.POST.get('engine_number'),
                frvType_id=request.POST.get('frv_type') or None,
                make=request.POST.get('make'),
                model=request.POST.get('model'),
                year_of_manufacture=request.POST.get('year_of_manufacture') or None,
                fuelType_id=request.POST.get('fuel_type') or None,
                engine_cc=request.POST.get('engine_cc'),
                seating_capacity=request.POST.get('seating_capacity') or 4,
                district_id=request.POST.get('district') or None,
                policeStation_id=request.POST.get('police_station') or None,
                status_id=request.POST.get('status') or None,
                insurance_policy_number=request.POST.get('insurance_policy_number'),
                insurance_valid_upto=request.POST.get('insurance_valid_upto') or None,
                pollution_certificate_valid_upto=request.POST.get('pollution_certificate_valid_upto') or None,
                fitness_certificate_valid_upto=request.POST.get('fitness_certificate_valid_upto') or None,
                is_active=request.POST.get('is_active') == 'on',
                created_by=request.user,
                frv_images=frv_images if frv_images else None,
                tenantProfile_id=request.tenantID
            )
            send_sweetalert(request, 'success', f'FRV {frv.vehicle_id} created successfully!')
            return redirect('frv-list')
        except Exception as e:
            send_sweetalert(request, 'error', f'Error: {str(e)}')
    
    context = {
        'frv_types': frv_types,
        'fuel_types': fuel_types,
        'vehicle_statuses': vehicle_statuses,
        'districts': districts,
        'police_stations': police_stations,
    }
    return render(request, 'frv/frv_create.html', context)

@login_required
def frvEdit(request, frv_unique_id):
    frv = get_object_or_404(FRV, frv_unique_id=frv_unique_id, tenantProfile_id=request.tenantID)

    # Resolve image URLs for display
    show_images = {}
    if frv.frv_images:
        for key, path in frv.frv_images.items():
            show_images[key] = GetFileUrl(path)
    
    if request.method == 'POST':
        try:
            frv_images = frv.frv_images if frv.frv_images else {}
            
            # Handle deletions
            delete_images = request.POST.getlist('delete_images')
            for img_key in delete_images:
                frv_images.pop(img_key, None)
            
            # Handle new uploads
            uploaded_files = request.FILES.getlist('frv_images')
            current_count = len(frv_images)
            for idx, uploaded_file in enumerate(uploaded_files):
                if uploaded_file:
                    stored_path = UploadFileData(
                        request.tenantID, 
                        f'frv_images/{frv.vehicle_id}', 
                        uploaded_file, 
                        f'image_{current_count + idx + 1}_{uploaded_file.name}'
                    )
                    frv_images[f'image_{current_count + idx + 1}'] = stored_path

            # Update frv fields
            frv.vehicle_id = request.POST.get('vehicle_id')
            frv.registration_number = request.POST.get('registration_number')
            frv.registration_date = request.POST.get('registration_date') or None
            frv.registration_valid_upto = request.POST.get('registration_valid_upto') or None
            frv.chassis_number = request.POST.get('chassis_number')
            frv.engine_number = request.POST.get('engine_number')
            frv.frvType_id = request.POST.get('frv_type') or None
            frv.make = request.POST.get('make')
            frv.model = request.POST.get('model')
            frv.year_of_manufacture = request.POST.get('year_of_manufacture') or None
            frv.fuelType_id = request.POST.get('fuel_type') or None
            frv.engine_cc = request.POST.get('engine_cc')
            frv.seating_capacity = request.POST.get('seating_capacity') or 4
            frv.district_id = request.POST.get('district') or None
            frv.policeStation_id = request.POST.get('police_station') or None
            frv.status_id = request.POST.get('status') or None
            frv.insurance_policy_number = request.POST.get('insurance_policy_number')
            frv.insurance_valid_upto = request.POST.get('insurance_valid_upto') or None
            frv.pollution_certificate_valid_upto = request.POST.get('pollution_certificate_valid_upto') or None
            frv.fitness_certificate_valid_upto = request.POST.get('fitness_certificate_valid_upto') or None
            frv.is_active = request.POST.get('is_active') == 'on'
            frv.frv_images = frv_images if frv_images else None
            frv.updated_by = request.user
            frv.save()

            # Re-resolve images after update
            show_images = {}
            if frv.frv_images:
                for key, path in frv.frv_images.items():
                    show_images[key] = GetFileUrl(path)
            send_sweetalert(request, 'success', f'FRV {frv.vehicle_id} updated successfully!')
            return redirect('frv-list')
        except Exception as e:
            send_sweetalert(request, 'error', f'Error: {str(e)}')
    
    # Get data for dropdowns
    context = {
        'frv': frv,
        'show_images': show_images,
        'frv_types': FRVType.objects.filter(is_active=True),
        'fuel_types': FuelType.objects.filter(is_active=True),
        'vehicle_statuses': VehicleStatus.objects.filter(is_active=True),
        'districts': District.objects.filter(is_active=True),
        'police_stations': PoliceStation.objects.filter(is_active=True),
    }
    return render(request, 'frv/frv_create.html', context)

@login_required
def frvDelete(request, frv_unique_id):
    frv = get_object_or_404(FRV, frv_unique_id=frv_unique_id, tenantProfile_id=request.tenantID)
    if request.method == 'POST':
        try:
            frv.delete()
            send_sweetalert(request, 'success', f'FRV {frv.vehicle_id} deleted successfully!')
        except Exception as e:
            print(f"Error deleting FRV: {e}")
            send_sweetalert(request, 'error', f'Error: {str(e)}')
    return redirect('frv-list')

@login_required
def frvDetail(request, frv_unique_id):
    frv = get_object_or_404(FRV, frv_unique_id=frv_unique_id, tenantProfile_id=request.tenantID)

    
    show_images = {}
    image_urls_list = []
    first_image = None
    
    if frv.frv_images and isinstance(frv.frv_images, dict):
        for key, path in frv.frv_images.items():
            if path:
                url = GetFileUrl(path)
                show_images[key] = url
                image_urls_list.append(url)
        
        # Set first image if any exist
        if image_urls_list:
            first_image = image_urls_list[0]
    
    context = {
        'frv': frv,
        'show_images': show_images,
        'image_urls_list': json.dumps(image_urls_list),  # Convert to JSON for JavaScript
        'first_image': first_image,
        'image_count': len(image_urls_list),
        'has_images': len(image_urls_list) > 0,
        'has_multiple_images': len(image_urls_list) > 1,
        'frv_unique_id': frv.frv_unique_id,
    }
    return render(request, 'frv/frv_detail.html', context)
import csv
import json
import io
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from accounts.helpers.base import Base
from accounts.helpers.decorators import CheckRole
from accounts.models import Profile
from setup.models import CostCenter, CostCenterStatus, CostCenterBulkUploadHistory
from accounts.helpers.import_export_utils import parse_upload


@login_required
@CheckRole(Base.Group.SetupGroup.value)
def data_setup(request):
    return render(request, "setup/data_setup.html")


@login_required
def cost_center_list(request):
    tenant_id = request.tenantID
    items = CostCenter.objects.filter(tenantProfile_id=tenant_id).order_by('cost_center_name')
    upload_history = CostCenterBulkUploadHistory.objects.filter(tenantProfile_id=tenant_id).select_related('status', 'uploaded_by')
    return render(request, "setup/cost_center_list.html", {'items': items, 'upload_history': upload_history})


@login_required
def cost_center_add(request):
    if request.method == "POST":
        name = request.POST.get("cost_center_name", "").strip()
        description = request.POST.get("description", "").strip()
        is_active = request.POST.get("is_active") == "on"
        if not name:
            return JsonResponse({'success': False, 'error': 'Cost center name is required'})
        profile = Profile.objects.filter(user=request.user).select_related('tenantProfile').first()
        tenant = profile.tenantProfile if profile else None
        if not tenant:
            return JsonResponse({'success': False, 'error': 'No tenant profile found for your account'})
        try:
            CostCenter.objects.create(
                cost_center_name=name,
                description=description or None,
                is_active=is_active,
                tenantProfile=tenant,
                created_by=request.user,
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return render(request, "setup/partials/_costcenter_form.html", {'obj': None})


@login_required
def cost_center_edit(request, pk):
    obj = CostCenter.objects.filter(cost_center_id=pk).first()
    if not obj:
        return JsonResponse({'success': False, 'error': 'Cost center not found'})
    if request.method == "POST":
        name = request.POST.get("cost_center_name", "").strip()
        description = request.POST.get("description", "").strip()
        is_active = request.POST.get("is_active") == "on"
        if not name:
            return JsonResponse({'success': False, 'error': 'Cost center name is required'})
        try:
            obj.cost_center_name = name
            obj.description = description or None
            obj.is_active = is_active
            obj.updated_by = request.user
            obj.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return render(request, "setup/partials/_costcenter_form.html", {'obj': obj})


@login_required
def cost_center_delete(request):
    pk = request.POST.get("pk")
    CostCenter.objects.filter(cost_center_id=pk).delete()
    return JsonResponse({'success': True})


@login_required
def cost_center_download_sample(request, fmt):
    filename = 'cost_center_sample'
    headers = ['Cost Center Name', 'Description']
    sample_rows = [
        ['IT Infrastructure', 'All IT-related costs'],
        ['Marketing', 'Marketing and advertising expenses'],
        ['Operations', 'Day-to-day operational expenses'],
    ]

    if fmt == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        response.write('\ufeff'.encode('utf-8'))
        writer = csv.writer(response)
        writer.writerow(headers)
        writer.writerows(sample_rows)
        return response

    # Excel (XLSX)
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Cost Centers'

    ws.append(headers)
    header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF')
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')

    for row in sample_rows:
        ws.append(row)

    ws.column_dimensions['A'].width = 35
    ws.column_dimensions['B'].width = 45

    output = io.BytesIO()
    wb.save(output)
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    return response


@login_required
def cost_center_upload_detail(request, pk):
    history = get_object_or_404(CostCenterBulkUploadHistory, upload_history_id=pk)
    items = CostCenter.objects.filter(costCenterBulkUpload=history).order_by('cost_center_name')
    return render(request, "setup/partials/_upload_detail.html", {'history': history, 'items': items})


@login_required
def cost_center_download_errors(request, pk):
    history = get_object_or_404(CostCenterBulkUploadHistory, upload_history_id=pk)
    try:
        error_rows = json.loads(history.remarks or '[]')
    except (json.JSONDecodeError, TypeError):
        error_rows = []
    if not error_rows:
        error_rows = [{'Cost Center Name': '', 'Description': '', 'Error': 'No error details available'}]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="cost_center_errors_{pk}.csv"'
    response.write('\ufeff'.encode('utf-8'))
    writer = csv.writer(response)
    writer.writerow(['Cost Center Name', 'Description', 'Error'])
    for row in error_rows:
        writer.writerow([row.get('Cost Center Name', ''), row.get('Description', ''), row.get('Error', '')])
    return response


@login_required
def cost_center_bulk_upload(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    profile = Profile.objects.filter(user=request.user).select_related('tenantProfile').first()
    tenant = profile.tenantProfile if profile else None
    if not tenant:
        return JsonResponse({'success': False, 'error': 'No tenant profile found for your account'})

    file = request.FILES.get('file')
    fmt = request.POST.get('format', 'csv')
    if not file:
        return JsonResponse({'success': False, 'error': 'No file uploaded'})

    try:
        rows = parse_upload(file, fmt)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Could not read file. Make sure the file format matches your selection. Detail: {e}'})

    if not rows:
        return JsonResponse({'success': False, 'error': 'File is empty or has no valid data rows. Check the file has correct headers: "Cost Center Name", "Description".'})

    status_pending, _ = CostCenterStatus.objects.get_or_create(
        cost_center_status_name='Pending', defaults={'cost_center_status_css': 'warning'}
    )
    history = CostCenterBulkUploadHistory.objects.create(
        file_name=file.name,
        uploaded_by=request.user,
        total_records=len(rows),
        processed_records=0,
        failed_records=0,
        pending_records=len(rows),
        status=status_pending,
        tenantProfile=tenant,
    )

    created = 0
    updated = 0
    errors = []
    error_rows = []

    for idx, row in enumerate(rows, start=2):
        name = row.get('Cost Center Name', '').strip()
        description = row.get('Description', '').strip()
        if not name:
            errors.append(f"Row {idx}: Cost Center Name is required")
            error_rows.append({'Cost Center Name': name, 'Description': description, 'Error': 'Cost Center Name is required'})
            continue
        try:
            existing = CostCenter.objects.filter(cost_center_name=name, tenantProfile=tenant).first()
            if existing:
                existing.description = description or None
                existing.updated_by = request.user
                existing.costCenterBulkUpload = history
                existing.save()
                updated += 1
            else:
                CostCenter.objects.create(
                    cost_center_name=name,
                    description=description or None,
                    is_active=True,
                    tenantProfile=tenant,
                    created_by=request.user,
                    costCenterBulkUpload=history,
                )
                created += 1
        except Exception as e:
            errors.append(f"Row {idx}: {e}")
            error_rows.append({'Cost Center Name': name, 'Description': description, 'Error': str(e)})

    processed = created + updated
    failed = len(errors)
    pending = len(rows) - processed - failed
    status_name = 'Completed' if failed == 0 else 'Completed with Errors'
    status_css = 'success' if failed == 0 else 'warning'
    final_status, _ = CostCenterStatus.objects.get_or_create(
        cost_center_status_name=status_name, defaults={'cost_center_status_css': status_css}
    )
    history.total_records = len(rows)
    history.processed_records = processed
    history.failed_records = failed
    history.pending_records = max(0, pending)
    history.status = final_status
    history.remarks = json.dumps(error_rows) if error_rows else ''
    history.save(update_fields=['total_records', 'processed_records', 'failed_records', 'pending_records', 'status', 'remarks'])

    msg = f"Bulk upload complete: {created} created, {updated} updated"
    if errors:
        msg += f", {len(errors)} errors"

    return JsonResponse({'success': True, 'message': msg, 'created': created, 'updated': updated, 'errors': len(errors)})

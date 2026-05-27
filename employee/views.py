from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from accounts.helpers.message_helper import send_sweetalert
from employee.models import EmployeeInfo, EmployeeCaste
from masters.models import Gender, District
from setup.models import EmployeeType
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404


def _parse_date(value):
    try:
        return datetime.strptime(value.strip(), '%Y-%m-%d').date()
    except (ValueError, AttributeError):
        return None


def _form_context(request, obj=None):
    return {
        'obj': obj,
        'blood_groups': EmployeeInfo.BLOOD_GROUPS,
        'marital_choices': EmployeeInfo.MARITAL_STATUS,
        'employment_statuses': EmployeeInfo.EMPLOYMENT_STATUS,
        'genders': Gender.objects.filter(is_active=True),
        'districts': District.objects.filter(is_active=True).order_by('district_name'),
        'emp_types': EmployeeType.objects.filter(tenantProfile_id=request.tenantID, is_active=True).order_by('name'),
        'castes': EmployeeCaste.objects.filter(is_active=True),
    }


def _obj_to_fd(obj):
    """Serialize an EmployeeInfo instance to a form_data dict."""
    return {
        'first_name': obj.first_name or '',
        'last_name': obj.last_name or '',
        'mobile': obj.mobile or '',
        'gender_id': str(obj.gender_id) if obj.gender_id else '',
        'email': obj.email or '',
        'employee_code': obj.employee_code or '',
        'date_of_birth': obj.date_of_birth.strftime('%Y-%m-%d') if obj.date_of_birth else '',
        'father_name': obj.father_name or '',
        'mother_name': obj.mother_name or '',
        'marital_status': obj.marital_status or '',
        'blood_group': obj.blood_group or '',
        'nationality': obj.nationality or 'Indian',
        'religion': obj.religion or '',
        'aadhaar_number': obj.aadhaar_number or '',
        'pan_number': obj.pan_number or '',
        'passport_number': obj.passport_number or '',
        'caste_id': str(obj.caste_id) if obj.caste_id else '',
        'emp_type_id': str(obj.empType_id) if obj.empType_id else '',
        'district_id': str(obj.district_id) if obj.district_id else '',
        'city': obj.city or '',
        'postal_code': obj.postal_code or '',
        'current_address': obj.current_address or '',
        'permanent_address': obj.permanent_address or '',
        'department': obj.department or '',
        'designation': obj.designation or '',
        'joining_date': obj.joining_date.strftime('%Y-%m-%d') if obj.joining_date else '',
        'employment_status': obj.employment_status or 'Active',
        'work_location': obj.work_location or '',
        'basic_salary': str(obj.basic_salary) if obj.basic_salary else '',
        'hra': str(obj.hra) if obj.hra else '',
        'bonus': str(obj.bonus) if obj.bonus else '',
        'bank_name': obj.bank_name or '',
        'bank_address': obj.bank_address or '',
        'bank_account_number': obj.bank_account_number or '',
        'ifsc_code': obj.ifsc_code or '',
        'is_eligible_for_pf': 'on' if obj.is_eligible_for_pf else '',
        'is_gratuity': 'on' if obj.is_gratuity else '',
        'pf_number': obj.pf_number or '',
    }


def _post_to_fields(p):
    """Map POST data to EmployeeInfo field kwargs."""
    return dict(
        first_name=p.get('first_name', '').strip(),
        last_name=p.get('last_name', '').strip(),
        mobile=p.get('mobile', '').strip(),
        gender_id=p.get('gender_id', '').strip() or None,
        designation=p.get('designation', '').strip(),
        joining_date=_parse_date(p.get('joining_date', '')),
        email=p.get('email', '').strip() or None,
        employee_code=p.get('employee_code', '').strip() or None,
        date_of_birth=_parse_date(p.get('date_of_birth', '')),
        father_name=p.get('father_name', '').strip(),
        mother_name=p.get('mother_name', '').strip(),
        marital_status=p.get('marital_status', '').strip(),
        blood_group=p.get('blood_group', '').strip(),
        nationality=p.get('nationality', 'Indian').strip() or 'Indian',
        religion=p.get('religion', '').strip(),
        aadhaar_number=p.get('aadhaar_number', '').strip() or None,
        pan_number=p.get('pan_number', '').strip() or None,
        passport_number=p.get('passport_number', '').strip() or None,
        caste_id=p.get('caste_id', '').strip() or None,
        empType_id=p.get('emp_type_id', '').strip() or None,
        district_id=p.get('district_id', '').strip() or None,
        city=p.get('city', '').strip(),
        postal_code=p.get('postal_code', '').strip() or None,
        current_address=p.get('current_address', '').strip() or None,
        permanent_address=p.get('permanent_address', '').strip() or None,
        department=p.get('department', '').strip() or None,
        employment_status=p.get('employment_status', 'Active'),
        work_location=p.get('work_location', '').strip(),
        basic_salary=p.get('basic_salary', '').strip() or None,
        hra=p.get('hra', '').strip() or None,
        bonus=p.get('bonus', '').strip() or None,
        bank_name=p.get('bank_name', '').strip(),
        bank_address=p.get('bank_address', '').strip(),
        bank_account_number=p.get('bank_account_number', '').strip(),
        ifsc_code=p.get('ifsc_code', '').strip(),
        is_gratuity=p.get('is_gratuity') == 'on',
        is_eligible_for_pf=p.get('is_eligible_for_pf') == 'on',
        pf_number=p.get('pf_number', '').strip(),
    )


@login_required
def employee_list(request):
    search_query = request.GET.get('search', '').strip()
    qs = EmployeeInfo.objects.filter(
        tenantProfile_id=request.tenantID
    ).select_related('gender', 'empType', 'empStatus')

    if search_query:
        qs = qs.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(employee_code__icontains=search_query) |
            Q(mobile__icontains=search_query) |
            Q(designation__icontains=search_query)
        )

    qs = qs.order_by('first_name', 'last_name')
    total_employees = qs.count()
    active_employees = qs.filter(employment_status='Active').count()
    inactive_employees = total_employees - active_employees

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'employee/employee_list.html', {
        'page_obj': page_obj,
        'paginator': paginator,
        'search_query': search_query,
        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': inactive_employees,
    })


@login_required
def employee_add(request):
    fd = {}
    if request.method == 'POST':
        p = request.POST
        fd = p
        try:
            obj = EmployeeInfo.objects.create(
                **_post_to_fields(p),
                empStatus_id=1,
                tenantProfile_id=request.tenantID,
                created_by=request.user,
            )
            send_sweetalert(request, 'success', f'Employee {obj.full_name} created successfully.')
            return redirect('employee-list')
        except Exception as e:
            send_sweetalert(request, 'error', str(e))

    ctx = _form_context(request)
    ctx['form_data'] = fd
    return render(request, 'employee/employee_form.html', ctx)


@login_required
def employee_update(request, emp_unique_id=''):
    obj = get_object_or_404(EmployeeInfo, employee_unique_id=emp_unique_id, tenantProfile_id=request.tenantID)

    if request.method == 'POST':
        p = request.POST
        try:
            for attr, val in _post_to_fields(p).items():
                setattr(obj, attr, val)
            obj.updated_by = request.user
            obj.save()
            send_sweetalert(request, 'success', f'Employee {obj.full_name} updated successfully.')
            return redirect('employee-list')
        except Exception as e:
            send_sweetalert(request, 'error', str(e))
            fd = p
    else:
        fd = _obj_to_fd(obj)

    ctx = _form_context(request, obj)
    ctx['form_data'] = fd
    return render(request, 'employee/employee_form.html', ctx)


@login_required
def employee_delete(request):
    pk = request.POST.get('pk')
    EmployeeInfo.objects.filter(employee_id=pk, tenantProfile_id=request.tenantID).delete()
    return JsonResponse({'success': True})

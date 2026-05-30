from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q, Count
from accounts.helpers.basicUtility import GetFileUrl, UploadFileData
from accounts.helpers.import_export_utils import export_csv, export_xlsx, parse_upload
from accounts.base import Base
from accounts.helpers.decorators import CheckRole
from accounts.models import Profile, UserLoginTrace
from masters.models import Country, Gender, State, Currency, District
from tenant.models import Role, TimeZone, DateFormat, TimeFormat
from user.models import UserDistrictMapping


def _int(val):
    try:
        return int(val) if val else None
    except (ValueError, TypeError):
        return None


@login_required
@CheckRole(Base.Group.UserGroup.value)
def users_view(request):
    tenant_id = request.tenantID
    base_qs = Profile.objects.filter(tenantProfile_id=tenant_id).select_related('user', 'role', 'gender')
    if request.role != 'Administrator':
        base_qs = base_qs.exclude(role__role_name='Administrator').select_related('user', 'role', 'gender')
    stats = base_qs.aggregate(alluser=Count('id'), activeuser=Count('id', filter=Q(is_active=True)),
                              inactiveUser=Count('id', filter=Q(is_active=False)),
                              neverlogin=Count('id', filter=Q(is_active=True, user__last_login__isnull=True)), )
    context = {
        "alluser": stats["alluser"],
        "activeuser": stats["activeuser"],
        "inactiveUser": stats["inactiveUser"],
        "neverlogin": stats["neverlogin"],
    }
    return render(request, "user/user_list.html", context)


@login_required
@CheckRole(Base.Group.UserGroup.value)
def UserListJson(request):
    tenant_id = request.tenantID
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')

    base_qs = Profile.objects.filter(tenantProfile_id=tenant_id).select_related('user', 'role', 'gender')
    if request.role != 'Administrator':
        base_qs = base_qs.exclude(role__role_name='Administrator').select_related('user', 'role', 'gender')
    order_column_index = int(request.GET.get('order[0][column]', 1))
    order_dir = request.GET.get('order[0][dir]', 'asc')

    order_map = {
        1: ['user__first_name', 'user__last_name'],
        2: ['role__role_name'],
        3: ['gender__gender_name'],
        4: ['is_active'],
    }
    order_fields = order_map.get(order_column_index, ['user__first_name'])
    if order_dir == 'desc':
        order_fields = ['-' + f for f in order_fields]

    if search_value:
        base_qs = base_qs.filter(Q(user__first_name__icontains=search_value) |
                                 Q(user__last_name__icontains=search_value) |
                                 Q(user__email__icontains=search_value) |
                                 Q(role__role_name__icontains=search_value) |
                                 Q(gender__gender_name__icontains=search_value))

    records_total = Profile.objects.filter(tenantProfile_id=tenant_id).count()
    records_filtered = base_qs.count()
    profiles = base_qs.order_by(*order_fields)[start:start + length]

    # Batch-fetch district mappings for all users on this page
    user_ids = [p.user_id for p in profiles]
    district_map = {}
    try:
        for m in (UserDistrictMapping.objects
                .filter(user_id__in=user_ids, tenantProfile_id=tenant_id, is_active=True)
                .select_related('district')
                .order_by('district__district_name')):
            district_map.setdefault(m.user_id, []).append(m.district.district_name)
    except Exception:
        pass  # table may not exist if migration hasn't been run yet

    data = []
    for i, profile in enumerate(profiles):
        data.append({
            'sno': start + i + 1,
            'user_pk': profile.user.pk,
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'email': profile.user.email,
            'img_url': GetFileUrl(profile.profile_picture_s3_url),
            'role': profile.role.role_name if profile.role else '',
            'gender': profile.gender.gender_name if profile.gender else '',
            'gender_id': profile.gender_id,
            'is_active': profile.user.is_active,
            'districts': ', '.join(district_map.get(profile.user_id, [])),
        })

    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data,
    })


@login_required
@CheckRole(Base.Group.UserGroup.value)
def user_create(request, user_id=None):
    tenant_id = request.tenantID
    profile = None
    loginhistory = []

    # Fetch existing profile if editing
    if user_id:
        user_instance = get_object_or_404(User, id=user_id)
        profile = Profile.objects.filter(user=user_instance).select_related('role', 'tenantProfile').first()
        loginhistory = UserLoginTrace.objects.filter(is_active=True, user=user_instance).order_by('-created_date')[:100]

    # Existing district mappings for this user
    user_district_ids = []
    if user_id:
        try:
            user_district_ids = list(
                UserDistrictMapping.objects.filter(user_id=user_id, tenantProfile_id=tenant_id, is_active=True)
                .values_list('district_id', flat=True)
            )
        except Exception:
            pass  # table may not exist until migration is applied

    # Base Context
    context = {
        "profile": profile,
        "loginhistory": loginhistory,
        "country": Country.objects.filter(is_active=True),
        "gender": Gender.objects.filter(is_active=True),
        "role": Role.objects.filter(is_active=True, tenantProfile_id=tenant_id),
        "active_tab": "details",
        "currencyList": Currency.objects.filter(is_active=True),
        "timeZoneList": TimeZone.objects.filter(is_active=True),
        "dateFormatList": DateFormat.objects.filter(is_active=True),
        "timeFormatList": TimeFormat.objects.filter(is_active=True),
        "districtList": District.objects.filter(is_active=True).select_related('state').order_by('district_name'),
        "user_district_ids": user_district_ids,
    }

    if request.method == "POST":
        # TAB 1: User Details
        if 'btn_createUserDetails' in request.POST:
            p = request.POST

            first_name = p.get('userFirstName', '').strip()
            last_name = p.get('userLastName', '').strip()
            email = p.get('userEmail', '').strip()
            phone = p.get('userPhone', '').strip()
            city = p.get('city', '').strip()
            address = p.get('userAddress', '').strip()
            is_active = p.get('edituserstatus') == 'on'
            is_login_with_otp = p.get('is_login_with_otp') == 'on'
            profile_photo = request.FILES.get('uploadprofilephoto')

            gender_id = _int(p.get('gender'))
            role_id = _int(p.get('role'))
            country_id = _int(p.get('country_id'))
            state_id = _int(p.get('state_id'))

            currency_id = _int(p.get('currency_id'))
            time_zone_id = _int(p.get('time_zone'))
            date_format_id = _int(p.get('date_formate_view'))
            time_format_id = _int(p.get('time_formate_view'))

            try:
                if not profile:
                    if User.objects.filter(email=email).exists():
                        messages.error(request, "A user with this email already exists.")
                        return redirect('user-create-form')

                    base_un = email.split('@')[0]
                    un, n = base_un, 1
                    while User.objects.filter(username=un).exists():
                        un = f"{base_un}{n}";
                        n += 1

                    user = User.objects.create_user(username=un, email=email, first_name=first_name, last_name=last_name, is_active=is_active, )
                    profile = Profile.objects.get(user=user)
                    profile.tenantProfile_id = tenant_id
                    profile.created_by = request.user
                else:
                    user = profile.user
                    if User.objects.filter(email=email).exclude(id=user.id).exists():
                        messages.error(request, "This email is already registered to another user.")
                        return redirect('user-update-form', user_id=user.id)

                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.is_active = is_active
                user.save()

                profile.mobile = phone
                profile.address = address
                profile.city = city
                profile.is_login_with_otp = is_login_with_otp
                profile.is_active = is_active
                profile.gender_id = gender_id
                profile.role_id = role_id
                profile.country_id = country_id
                profile.state_id = state_id
                profile.currency_id = currency_id
                profile.time_zone_id = time_zone_id
                profile.date_formate_view_id = date_format_id
                profile.time_formate_view_id = time_format_id
                profile.updated_by = request.user
                profile.save()
                if profile_photo:
                    path = UploadFileData(tenant_id, 'profile', profile_photo, '')
                    if path:
                        profile.profile_picture_s3_url = path
                        profile.save()

                try:
                    with transaction.atomic():
                        selected = [int(d) for d in p.getlist('district_ids') if d]
                        UserDistrictMapping.objects.filter(user=user, tenantProfile_id=tenant_id).delete()
                        for did in selected:
                            UserDistrictMapping.objects.create(user=user,district_id=did, tenantProfile_id=tenant_id, created_by=request.user, )
                except Exception:
                    pass  # table not yet created — run: python manage.py migrate user

                messages.success(request, "User details saved successfully.")
                return redirect('user-update-form', user_id=user.id)

            except Exception as error:
                import traceback;
                traceback.print_exc()
                messages.error(request, f"Error saving user: {error}")
                context['active_tab'] = 'details'

        # TAB 2: User Security (Password)
        elif 'btn_createUserSecurity' in request.POST:
            try:
                if not profile:
                    messages.error(request, "Please create user first.")
                    return redirect('user-create-form')

                username = request.POST.get('username', '').strip()
                password = request.POST.get('password', '').strip()
                confirm_password = request.POST.get('confirm_password', '').strip()

                user = profile.user

                # Validate Username
                if User.objects.filter(username=username).exclude(id=user.id).exists():
                    messages.error(request, "Username already exists.")
                    return redirect('user-update-form', user_id=user.id)

                # Validate Password Match
                if password and password != confirm_password:
                    messages.error(request, "Password mismatch.")
                    return redirect('user-update-form', user_id=user.id)

                user.username = username
                if password:
                    user.set_password(password)
                    profile.is_system_assigned_password = False

                user.save()

                profile.updated_by = request.user
                profile.save()

                messages.success(request, "Login credentials updated successfully.")
                context['active_tab'] = 'security'
                return redirect('user-update-form', user_id=user.id)

            except Exception as error:
                print('error=>', error)
                messages.error(request, f"Error updating security: {str(error)}")
                context['active_tab'] = 'security'

    return render(request, "user/user_form.html", context)


@login_required
@CheckRole(Base.Group.UserGroup.value)
def user_detail(request, user_id=None):
    tenant_id = request.tenantID
    user_instance = get_object_or_404(User, id=user_id)
    profile = Profile.objects.filter(user=user_instance).select_related('role', 'gender', 'country', 'state', 'tenantProfile').first()
    loginhistory = UserLoginTrace.objects.filter(is_active=True, user=user_instance).order_by('-created_date')[:100]

    has_username = bool(user_instance.username and user_instance.username.strip())
    has_password = user_instance.has_usable_password()
    is_profile_complete = has_username and has_password

    context = {
        "user_obj": user_instance,
        "profile": profile,
        "loginhistory": loginhistory,
        "date_joined": user_instance.date_joined,
        "is_profile_complete": is_profile_complete,
    }
    return render(request, "user/user_detail.html", context)


# =============================================================
# USER IMPORT / EXPORT
# =============================================================

USER_EXPORT_FIELDS = ['user__username', 'user__first_name', 'user__last_name', 'user__email',
                      'role__role_name', 'gender__gender_name', 'country__country_name',
                      'state__state_name', 'mobile', 'is_active']
USER_EXPORT_HEADERS = {
    'user__username': 'Username', 'user__first_name': 'First Name', 'user__last_name': 'Last Name',
    'user__email': 'Email', 'role__role_name': 'Role', 'gender__gender_name': 'Gender',
    'country__country_name': 'Country', 'state__state_name': 'State', 'mobile': 'Mobile',
    'is_active': 'Active',
}


@login_required
def ExportUsersCSV(request):
    qs = Profile.objects.filter(tenantProfile_id=request.tenantID).select_related(
        'user', 'role', 'gender', 'country', 'state')
    return export_csv(qs, USER_EXPORT_FIELDS, USER_EXPORT_HEADERS, 'Users')


@login_required
def ExportUsersExcel(request):
    qs = Profile.objects.filter(tenantProfile_id=request.tenantID).select_related(
        'user', 'role', 'gender', 'country', 'state')
    return export_xlsx(qs, USER_EXPORT_FIELDS, USER_EXPORT_HEADERS, 'Users')


@transaction.atomic
@login_required
def ImportUsers(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    file = request.FILES.get('file')
    fmt = request.POST.get('format', 'csv')
    if not file:
        return JsonResponse({'success': False, 'error': 'No file uploaded'})

    rows = parse_upload(file, fmt)
    if not rows:
        return JsonResponse({'success': False, 'error': 'File is empty or has no data rows'})

    created = 0
    updated = 0
    errors = []
    tenant_id = request.tenantID

    for idx, row in enumerate(rows, start=2):
        try:
            username = row.get('Username', '').strip()
            if not username:
                errors.append(f"Row {idx}: Username is required")
                continue

            role_name = row.get('Role', '').strip()
            role = Role.objects.filter(role_name=role_name, tenantProfile_id=tenant_id).first()
            gender = Gender.objects.filter(gender_name__iexact=row.get('Gender', '').strip()).first()
            country = Country.objects.filter(country_name=row.get('Country', '').strip()).first()
            state = State.objects.filter(state_name=row.get('State', '').strip()).first()

            existing_user = User.objects.filter(username=username).first()
            if existing_user:
                profile = Profile.objects.filter(user=existing_user, tenantProfile_id=tenant_id).first()
                if not profile:
                    errors.append(f"Row {idx}: User '{username}' exists but not in this tenant")
                    continue
                updated += 1
            else:
                password = row.get('Password', 'User@123').strip()
                user = User.objects.create_user(
                    username=username,
                    email=row.get('Email', '').strip(),
                    password=password,
                    first_name=row.get('First Name', '').strip(),
                    last_name=row.get('Last Name', '').strip(),
                )
                profile, _ = Profile.objects.get_or_create(user=user)
                created += 1

            profile.tenantProfile_id = tenant_id
            if role:
                profile.role = role
            if gender:
                profile.gender = gender
            if country:
                profile.country = country
            if state:
                profile.state = state
            profile.mobile = row.get('Mobile', '')[:20]
            profile.is_active = str(row.get('Active', 'true')).strip().lower() in ('1', 'yes', 'true', 'active', 'on')
            profile.save()

        except Exception as e:
            errors.append(f"Row {idx}: {e}")

    msg = f"Imported: {created} created, {updated} updated"
    if errors:
        msg += f", {len(errors)} errors: {'; '.join(errors[:5])}"

    return JsonResponse(
        {'success': True, 'message': msg, 'created': created, 'updated': updated, 'errors': len(errors)})

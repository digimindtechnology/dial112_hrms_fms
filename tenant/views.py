import traceback
from urllib.parse import quote

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models, transaction

from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from accounts.helpers.basicUtility import DeleteFileFromS3, UploadFileS3Server, UploadFileData
from accounts.helpers.base import Base
from accounts.helpers.decorators import CheckRole
from accounts.helpers.message_helper import send_sweetalert
from masters.models import Country, Currency

from tenant.models import (
    TenantProfile,
    TimeZone,
    DateFormat,
    TimeFormat,
    Role
)

from accounts.models import Profile, UserLoginTrace


@login_required
@CheckRole(Base.Group.TenantGroup.value)
def tenant_list(request):
    tenant_id = request.tenantID

    if request.method == "POST":
        search_query = request.POST.get("search", "").strip()
        if search_query:
            return redirect(f"{request.path}?search={quote(search_query)}")
        return redirect(request.path)

    search_query = request.GET.get("search", "").strip()

    all_tenants = TenantProfile.objects.all()
    if search_query:
        all_tenants = all_tenants.filter(
            models.Q(tenant_name__icontains=search_query) |
            models.Q(contact_person__icontains=search_query) |
            models.Q(email__icontains=search_query) |
            models.Q(mobile__icontains=search_query)
        )

    paginator = Paginator(all_tenants, 10)
    page = request.GET.get("page", 1)
    try:
        tenants_page = paginator.page(page)
    except PageNotAnInteger:
        tenants_page = paginator.page(1)
    except EmptyPage:
        tenants_page = paginator.page(paginator.num_pages)

    all_count = TenantProfile.objects.aggregate(
        total=models.Count('tenant_profile_id'),
        active=models.Count('tenant_profile_id', filter=models.Q(is_active=True)),
        inactive=models.Count('tenant_profile_id', filter=models.Q(is_active=False)),
    )

    context = {
        "all_tenants": tenants_page,
        "total_tenants": all_count['total'],
        "active_tenants": all_count['active'],
        "inactive_tenants": all_count['inactive'],
        "search_query": search_query,
        "page_obj": tenants_page,
        "paginator": paginator,
    }
    return render(request, "tenant/tenant_list.html", context)


@login_required
@CheckRole(Base.Group.TenantGroup.value)
def tenant_detail(request, pk):
    tenant = get_object_or_404(TenantProfile.objects.select_related(
        "country", "state", "currency", "time_zone", "date_formate_view", "time_formate_view", "admin_user"
    ), tenant_profile_id=pk)
    roles = Role.objects.filter(tenantProfile=tenant)
    context = {
        "tenant": tenant,
        "roles": roles,
    }
    return render(request, "tenant/tenant_detail.html", context)


@login_required
@CheckRole(Base.Group.TenantGroup.value)
def tenant_create(request):
    if request.method == "POST":
        try:
            with transaction.atomic():
                data = request.POST
                files = request.FILES

                tenant = TenantProfile.objects.create(
                    tenant_name=data.get("tenant_name", ""),
                    contact_person=f"{data.get('first_name', '')} {data.get('last_name', '')}",
                    address=data.get("address", ""),
                    country_id=data.get("country_id"),
                    state_id=data.get("state_id"),
                    city=data.get("city", ""),
                    postal_code=data.get("postal_code", ""),
                    email=data.get("email", ""),
                    mobile=data.get("mobile", ""),
                    admin_user_id=1,
                    currency_id=data.get("currency_id"),
                    time_zone_id=data.get("time_zone"),
                    date_formate_view_id=data.get("date_formate_view"),
                    time_formate_view_id=data.get("time_formate_view"),
                    gst=data.get("gst", ""),
                    pan=data.get("pan", ""),
                    website_url=data.get("website_url", ""),
                    is_active=True,
                )

                def upload(file, folder, field):
                    if not file:
                        return
                    path = UploadFileData(request.tenantID, folder, file)
                    if path:
                        old = getattr(tenant, field)
                        setattr(tenant, field, path)
                        tenant.save()
                        DeleteFileFromS3(old)

                upload(files.get("uploadTenantLogFile"), "logo", "tenant_logo_s3_url")
                upload(files.get("uploadTenantIconFile"), "logo", "tenant_favicon_s3_url")

                all_groups = Group.objects.filter(RoleGroup__tenantProfile_id=1).distinct()
                created = []

                for role_name in ("Administrator", "Admin"):

                    uname = f"{role_name}_{tenant.tenant_profile_id}"
                    pwd = f"{uname}_pwd"

                    user = User.objects.create_user(
                        username=uname,
                        email=tenant.email,
                        first_name=data.get("first_name", ""),
                        last_name=data.get("last_name", ""),
                        password=pwd,
                    )

                    created.append((uname, pwd))

                    template_role = Role.objects.filter(
                        tenantProfile_id=1, role_name=role_name
                    ).first()

                    role = Role.objects.create(
                        role_name=role_name,
                        role_short_name=getattr(template_role, "role_short_name", role_name),
                        tenantProfile=tenant,
                        system_role_id=getattr(template_role, "system_role_id", None),
                        sequence=getattr(template_role, "sequence", 0),
                        is_active=True,
                    )

                    role_groups = all_groups.filter(RoleGroup__role_name=role_name)
                    if role_name != 'Administrator':
                        role_groups = role_groups.exclude(name='Tenant')
                    role.group.set(role_groups)

                    profile = Profile.objects.get(user=user)
                    profile.tenantProfile = tenant
                    profile.mobile = tenant.mobile
                    profile.country_id = tenant.country_id
                    profile.role = role
                    profile.is_company_setup = True
                    profile.is_system_assigned_password = True
                    profile.created_by_id = 1
                    profile.save()

                uname, pwd = created[0]
                send_sweetalert(
                    request, "success",
                    f"Tenant created successfully. Username: {uname}, Password: {pwd}"
                )
                return redirect("dashboard-home")

        except Exception as e:
            traceback.print_exc()
            send_sweetalert(request, "error", str(e))
            return redirect("tenant-create")

    return render(request, "tenant/tenant_create.html", {
        "countryList": Country.objects.filter(is_active=True),
        "currencyList": Currency.objects.filter(is_active=True),
        "timeZoneList": TimeZone.objects.filter(is_active=True),
        "dateFormatList": DateFormat.objects.filter(is_active=True),
        "timeFormatList": TimeFormat.objects.filter(is_active=True),
    })


# =========================================================
# ACCOUNT SETTINGS
# =========================================================

@login_required
@CheckRole(Base.Group.TenantGroup.value)
def tenant_settings_account(request):
    try:
        tenant = TenantProfile.objects.filter(tenant_profile_id=request.tenantID).first()
        if not tenant:
            send_sweetalert(request, 'error', "Tenant not found")
            return redirect('tenant-settings-account')

        profile = Profile.objects.filter(user_id=tenant.admin_user_id).first()

        countryList = Country.objects.filter(is_active=True)
        currencyList = Currency.objects.filter(is_active=True)
        timeZoneList = TimeZone.objects.filter(is_active=True)
        dateFormatList = DateFormat.objects.filter(is_active=True)
        timeFormatList = TimeFormat.objects.filter(is_active=True)

        if request.method == "POST":

            # UPDATE ACCOUNT
            if 'btn_SubmitAccount' in request.POST:
                try:
                    with transaction.atomic():

                        first_name = request.POST.get("first_name", "")
                        last_name = request.POST.get("last_name", "")

                        tenant_logo = request.FILES.get('uploadTenantLogFile')
                        tenant_favicon = request.FILES.get('uploadTenantIconFile')

                        tenant.tenant_name = request.POST.get("tenant_name")
                        tenant.contact_person = first_name + ' ' + last_name
                        tenant.email = request.POST.get("email")
                        tenant.mobile = request.POST.get("mobile")
                        tenant.country_id = request.POST.get("country_id")
                        tenant.state_id = request.POST.get("state_id")
                        tenant.city = request.POST.get("city")
                        tenant.address = request.POST.get("address")
                        tenant.postal_code = request.POST.get("postal_code")
                        tenant.gst = request.POST.get("gst")
                        tenant.pan = request.POST.get("pan")
                        tenant.website_url = request.POST.get("website_url")
                        tenant.currency_id = request.POST.get("currency_id")
                        tenant.time_zone_id = request.POST.get("time_zone")
                        tenant.date_formate_view_id = request.POST.get("date_formate_view")
                        tenant.time_formate_view_id = request.POST.get("time_formate_view")
                        tenant.save()

                        if tenant_logo:
                            try:
                                old_logo = tenant.tenant_logo_s3_url
                                logo_path = UploadFileData(request.tenantID, 'logo', tenant_logo)
                                if not logo_path:
                                    raise ValueError("Logo upload failed")
                                tenant.tenant_logo_s3_url = logo_path
                                tenant.save()
                                DeleteFileFromS3(old_logo)

                            except Exception as e:
                                print("Logo Upload Error:", str(e))
                                send_sweetalert(request, 'error', "Logo upload failed")

                        if tenant_favicon:
                            try:
                                old_favicon = tenant.tenant_favicon_s3_url
                                favicon_path = UploadFileData(request.tenantID, 'logo', tenant_favicon)
                                if not favicon_path:
                                    raise ValueError("Favicon upload failed")
                                tenant.tenant_favicon_s3_url = favicon_path
                                tenant.save()
                                DeleteFileFromS3(old_favicon)

                            except Exception as e:
                                print("Favicon Upload Error:", str(e))
                                send_sweetalert(request, 'error', "Favicon upload failed")

                        # UPDATE USER
                        user = tenant.admin_user
                        user.first_name = first_name
                        user.last_name = last_name
                        user.save()

                        send_sweetalert(
                            request,
                            'success',
                            "Account updated successfully"
                        )

                        return redirect('tenant-settings-account')

                except Exception as e:
                    print("Account Update Error:", str(e))
                    traceback.print_exc()

                    send_sweetalert(
                        request,
                        'error',
                        "Something went wrong while updating account"
                    )

                    return redirect('tenant-settings-account')

            # DEACTIVATE ACCOUNT
            if 'btn_Deactivated' in request.POST:
                try:
                    tenant.is_active = False
                    tenant.save()

                    if profile:
                        profile.is_active = False
                        profile.save()

                    send_sweetalert(
                        request,
                        'success',
                        "Account deactivated successfully"
                    )

                except Exception as e:
                    print("Deactivate Error:", str(e))

                    send_sweetalert(
                        request,
                        'error',
                        "Unable to deactivate account"
                    )

                return redirect('tenant-settings-account')

            # ACTIVATE ACCOUNT
            if 'btn_Activate' in request.POST:
                try:
                    tenant.is_active = True
                    tenant.save()

                    if profile:
                        profile.is_active = True
                        profile.save()

                    send_sweetalert(
                        request,
                        'success',
                        "Account activated successfully"
                    )

                except Exception as e:
                    print("Activate Error:", str(e))

                    send_sweetalert(
                        request,
                        'error',
                        "Unable to activate account"
                    )

                return redirect('tenant-settings-account')

        context = {
            'tenant': tenant,
            'profile': profile,
            'countryList': countryList,
            'currencyList': currencyList,
            'timeZoneList': timeZoneList,
            'dateFormatList': dateFormatList,
            'timeFormatList': timeFormatList,
        }

        return render(
            request,
            "tenant/tenant_settings_account.html",
            context
        )

    except Exception as e:
        print("Main View Error:", str(e))
        traceback.print_exc()

        send_sweetalert(
            request,
            'error',
            "Unexpected error occurred"
        )

        return redirect('dashboard')


# =========================================================
# SECURITY SETTINGS
# =========================================================

@login_required
@CheckRole(Base.Group.TenantGroup.value)
def tenant_settings_security(request):
    tenant = TenantProfile.objects.filter(tenant_profile_id=request.tenantID).first()
    loginhistory = UserLoginTrace.objects.filter(is_active=True, user=tenant.admin_user).order_by('-created_date')
    if request.method == "POST":
        if 'btn_ChangePassword' in request.POST:
            user = tenant.admin_user
            currentPassword = request.POST.get("currentPassword")
            newPassword = request.POST.get("newPassword")
            confirmPassword = request.POST.get("confirmPassword")

            if newPassword == confirmPassword:
                if user.check_password(currentPassword):
                    user.set_password(newPassword)
                    user.save()

                    update_session_auth_hash(request, user)
                    profile = Profile.objects.filter(user_id=user.id).first()

                    profile.is_system_assigned_password = False
                    profile.save()

                    send_sweetalert(request, 'success', "Password changed successfully")
                else:
                    send_sweetalert(request, 'error', "Invalid current password")
            else:
                send_sweetalert(request, 'error', "Password and confirm password not match")
            return redirect('tenant-settings-security')

    context = {
        'loginhistory': loginhistory,
        'tenant': tenant,
    }

    return render(
        request,
        "tenant/tenant_settings_security.html",
        context
    )


# =========================================================
# ROLES & PERMISSIONS
# =========================================================

@login_required
@CheckRole(Base.Group.TenantGroup.value)
def tenant_roles_permissions(request):
    return render(
        request,
        "tenant/roles_permissions.html"
    )


@login_required
def RoleList(request):
    roleList = Role.objects.filter(
        tenantProfile_id=request.tenantID
    ).order_by('role_id')
    context = {
        'tenantId': request.tenantID,
        'roleList': roleList,
    }

    return render(
        request,
        'tenant/partials/_role_list.html',
        context
    )


@login_required
def AddUpdateRoleFrom(request, id):
    roleData = Role.objects.filter(
        role_id=id
    ).first()

    groupList = Group.objects.all()

    selectedGroupList = None

    if roleData:

        groupIds = []

        for g in roleData.group.all():
            groupIds.append(g.pk)

        selectedGroupList = groupList.filter(
            id__in=groupIds
        )

        groupList = groupList.exclude(
            id__in=groupIds
        )

    context = {
        'tenantId': request.tenantID,
        'roleData': roleData,
        'groupList': groupList,
        'selectedGroupList': selectedGroupList,
    }

    return render(
        request,
        'tenant/partials/_role_from.html',
        context
    )


@login_required
@csrf_exempt
def AddUpdateRoleDataPost(request):
    if request.method == 'POST':

        role_id = request.POST.get("role_id")
        role_name = request.POST.get("role_name")
        role_short_name = request.POST.get("role_short_name")
        sequence = request.POST.get("sequence")
        system_role_id = request.POST.get("system_role_id")

        groups_ids = []

        for r in request.POST:
            if r.startswith('groupCheckbox_'):
                groups_ids.append(r.split('_')[1])

        # UPDATE
        if role_id:

            roleData = Role.objects.filter(
                role_id=role_id
            ).first()

            roleData.role_name = role_name
            roleData.role_short_name = role_short_name
            roleData.sequence = sequence
            roleData.system_role_id = system_role_id

            roleData.save()

            roleData.group.clear()

            selected_groups = Group.objects.filter(
                pk__in=groups_ids
            )

            roleData.group.set(selected_groups)

            return JsonResponse({
                'message': 'Role updated successfully!'
            })

        # ADD
        else:

            roleData = Role.objects.create(
                role_name=role_name,
                role_short_name=role_short_name,
                sequence=sequence,
                system_role_id=system_role_id,
                tenantProfile_id=request.tenantID
            )

            selected_groups = Group.objects.filter(
                pk__in=groups_ids
            )

            roleData.group.set(selected_groups)

            return JsonResponse({
                'message': 'Role added successfully!'
            })

    return JsonResponse({
        'message': 'error'
    })


@login_required
def CopyRole(request):
    if request.method == 'POST':

        copyRoleId = request.POST.get("copyRoleId")

        copyRole = Role.objects.filter(
            role_id=copyRoleId
        ).first()

        groupIds = []

        for g in copyRole.group.all():
            groupIds.append(g.pk)

        copyRoleCount = Role.objects.filter(
            role_name='New Role'
        ).count()

        newRoleName = 'New Role'

        if copyRoleCount > 0:
            newRoleName = f'New Role-{copyRoleCount}'

        roleData = Role.objects.create(
            role_name=newRoleName,
            role_short_name=copyRole.role_short_name,
            sequence=copyRole.sequence,
            system_role_id=copyRole.system_role_id,
            tenantProfile_id=request.tenantID
        )

        selected_groups = Group.objects.filter(
            pk__in=groupIds
        )

        roleData.group.set(selected_groups)

        return JsonResponse({
            'message': 'Role copied successfully!'
        })

    return JsonResponse({
        'message': 'error'
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ApprovalType, ApprovalRule, Approver
from tenant.models import Role
from accounts.models import Profile



def ApprovalTypeList(request):
    try:
        approvalTypeList = ApprovalType.objects.filter(is_active=True).order_by('sequence')
        context = {
            'approvalTypeList': approvalTypeList,
        }

        return render(request, 'approvalrules/approve_type_list.html', context)

    except Exception as e:
        messages.error(request, str(e), extra_tags='alert alert-danger')
        return render(request, 'approvalrules/approve_type_list.html')



def ApprovalTypeCreate(request):
    try:
        if request.method == "POST":
            name = request.POST.get('name')
            sequence = request.POST.get('sequence')

            ApprovalType.objects.create(name=name, sequence=sequence)

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})

            messages.success(request, f'Approve Type "{name}" Created')
            return redirect('approve-type-list')

        if request.headers.get('x-requested-with') != 'XMLHttpRequest':
            return redirect('approve-type-list')

        context = {}
        return render(request, 'approvalrules/partials/_approve_type_form.html', context)

    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, str(e), extra_tags='alert alert-danger')
        return redirect('approve-type-list')



def ApprovalTypeUpdate(request, pk):
    try:
        approval_type = get_object_or_404(ApprovalType, pk=pk)

        if request.method == "POST":
            approval_type.name = request.POST.get('name')
            approval_type.sequence = request.POST.get('sequence')
            approval_type.is_active = request.POST.get('is_active') == 'on'

            approval_type.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})

            messages.success(request, f'Approve Type "{approval_type.name}" Updated')
            return redirect('approve-type-list')

        if request.headers.get('x-requested-with') != 'XMLHttpRequest':
            return redirect('approve-type-list')

        context = {
            'approval_type': approval_type
        }
        return render(request, 'approvalrules/partials/_approve_type_form.html', context)

    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, str(e), extra_tags='alert alert-danger')
        return redirect('approve-type-list')



def approveruleCreateView(request, id):
    approvertype = get_object_or_404(ApprovalType, pk=id)
    roles = Role.objects.filter(is_active=True, tenantProfile_id=request.tenantID).exclude(role_name='Administrator').order_by('role_name')
    approverule_id = request.GET.get('approverule_id') or request.POST.get('approveruleId', 0)
    editapproval_rule = None
    if approverule_id and approverule_id != '0':
        editapproval_rule = get_object_or_404(ApprovalRule, pk=approverule_id)

    if request.method == "POST":
        try:
            sequence = request.POST.get('sequence')
            role_id = request.POST.get('role')
            approver_id = request.POST.get('approver')
            is_active =  request.POST.get('is_active')

            duplicate_filter = dict(approval_type_id=id, role_id=role_id, approver_id=approver_id, tenantProfile_id=request.tenantID)
            duplicate_uesr_check = ApprovalRule.objects.filter(**duplicate_filter)

            if editapproval_rule:
                duplicate_uesr_check = duplicate_uesr_check.exclude(pk=editapproval_rule.pk)

            if duplicate_uesr_check.exists():
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': "This role and approver combination already exists!"})
                messages.warning(request, "This role and approver combination already exists!")
            else:
                if editapproval_rule:
                    approveruleobj = editapproval_rule
                    approveruleobj.updated_by = request.user
                    approveruleobj.is_active  = True  if is_active  else  False
                    message = "Approve rule updated successfully!"
                else:
                    approveruleobj = ApprovalRule()
                    approveruleobj.tenantProfile_id = request.tenantID
                    approveruleobj.created_by = request.user
                    message = "Approve rule added successfully!"
            
                approveruleobj.sequence = sequence
                approveruleobj.approver_id = approver_id
                approveruleobj.role_id = role_id
                approveruleobj.approval_type_id = id
                
                approveruleobj.save()
                
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                
                messages.success(request, message)
                return redirect('approvedetail', id)
            
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f"Error: {str(e)}")

    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return redirect('approvedetail', id)

    context = {
        'roles': roles,
        'approvertypeID': id,
        'approverule_id': approverule_id,
        'editapproval_rule': editapproval_rule,
        'approvers': approvertype.approvers.all() if hasattr(approvertype, 'approvers') else [],
        'approvertype': approvertype
    }
    return render(request, 'approvalrules/partials/_approvel_add_from.html', context)



def GetUser(request,**kwargs):
    
    try:
        role_id = kwargs.get('role_id', 0)

        profile = Profile.objects.filter(role__role_id=role_id, is_active=True).select_related('user')
        user_list = [
            {'id': p.user.id, 'name': p.user.get_full_name() or p.user.username}
            for p in profile
        ]
        return JsonResponse({'users': user_list})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def ApproveTypeDetailView(request, ApprovId):
    approvertype = get_object_or_404(ApprovalType, pk=ApprovId)
    approverule = ApprovalRule.objects.filter(approval_type_id=ApprovId, tenantProfile_id=request.tenantID).select_related('role', 'approver')
    
    context = {
        'approverule': approverule,
        'approvertype': approvertype
    }
    return render(request, 'approvalrules/approver_detail.html', context)



def listforapproval(request):
    status_filter = request.GET.get('status', '')
    approve_type_filter = request.GET.get('approve_type', '')

    approver = Approver.objects.filter(is_active=True,
                                        user=request.user,
                                        tenantProfile_id=request.tenantID
                                        ).order_by('-created_date')
    
    approvers = approver
    
    if status_filter:
        approvers = approvers.filter(status=status_filter)

    if approve_type_filter:
        print("approve_type_filter", approve_type_filter)
        approvers = approvers.filter(approval_type_id=approve_type_filter)
    approve_types = ApprovalType.objects.filter(is_active=True)

    status_counts = {
        'total': approver.filter(is_active=True).count(),
        'pending': approver.filter(is_active=True, status='pending').count(),
        'approved': approver.filter(is_active=True, status='approved').count(),
        'rejected': approver.filter(is_active=True, status='rejected').count(),
    }
    context = {
        'approvers': approvers,
        'status_counts': status_counts,
        'approve_types': approve_types,
        'current_status': status_filter,
        'current_approve_type': approve_type_filter,
    }
    return render(request, 'approvalrules/approver_list.html', context)
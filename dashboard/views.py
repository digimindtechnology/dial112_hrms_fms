from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.base import Base
from accounts.helpers.decorators import CheckRole
from accounts.models import UserDistrictMapping


@login_required(login_url='/login/')
@CheckRole(Base.Group.HomeGroup.value)
def home(request):
    userDistrictMapping = list(UserDistrictMapping.objects.filter(user=request.user, tenantProfile_id=request.tenantID, is_active=True).values_list('district_id', flat=True).distinct())
    context = {
        'userDistrictMapping': userDistrictMapping
    }
    return render(request, 'dashboard/home.html', context)


@login_required(login_url='/login/')
def not_authorized(request):
    return render(request, 'dashboard/not_accessible.html')

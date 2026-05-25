from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.base import Base
from accounts.helpers.decorators import CheckRole


@login_required(login_url='/login/')
@CheckRole(Base.Group.HomeGroup.value)
def home(request):
    context = {}
    return render(request, 'dashboard/home.html', context)


@login_required(login_url='/login/')
def not_authorized(request):
    return render(request, 'dashboard/not_accessible.html')
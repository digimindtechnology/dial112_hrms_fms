from datetime import date, datetime, timedelta, time
from django import template
from django.utils.safestring import mark_safe
from accounts.helpers.basicUtility import GetFileUrl
import re

register = template.Library()

## SS Dyanmice Date Time Fromate
MAP = {'YYYY': '%Y', 'YY': '%y', 'Month': '%B', 'Mon': '%b', 'MM': '%m', 'DD': '%d', 'D': '%d','HH': '%H', 'hh': '%I', 'h': '%I', 'mm': '%M', 'SS': '%S', 'A': '%p', }
REGEX = re.compile('|'.join(sorted(MAP, key=len, reverse=True)))
def convert_format(fmt, default):
    fmt = fmt or default
    return REGEX.sub(lambda m: MAP[m.group()], fmt)
def _format(value, fmt, default):
    if not value:
        return ''
    try:
        return value.strftime(convert_format(fmt, default))
    except Exception:
        return ''

@register.filter
def dyn_date(value, fmt=None):
    return _format(value, fmt, '%d-%m-%Y') \
        if isinstance(value, (date, datetime)) else ''

@register.filter
def dyn_time(value, fmt=None):
    return _format(value, fmt, 'HH:mm') \
        if isinstance(value, (datetime, time)) else ''
## SS Dyanmice Date Time Fromate

def safe_date(value):
    return isinstance(value, date)


@register.filter
def file_url(value):
    return GetFileUrl(value)


@register.filter
def FormatDateYYYYMMDD(value): return value.strftime('%Y-%m-%d') if safe_date(value) else ''


@register.filter
def FormatDateDDMMYYYY(value): return value.strftime('%d-%m-%Y') if safe_date(value) else ''


@register.filter
def FormatDateYYYYMMDDHHMM(value):
    if isinstance(value, datetime):
        value += timedelta(minutes=330)
        return value.strftime('%Y-%m-%d %H:%M')
    return ''


@register.filter
def FormatTimeHHMM(value): return f"{value.hour:02}:{value.minute:02} hrs" if value else ""


@register.filter
def ToInt(value): return int(value or 0)

@register.filter(name='multipleVal')
def multipleVal(val, val1):
    return val * val1


@register.filter(name='addVal')
def addVal(value, arg):
    return value + arg


@register.filter
def ConvertToDateTime(value):
    if not value: return ''
    value = value.replace('T', ' ').replace('+05:30', '').split('.')[0]
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')


@register.filter(name='GetRoleWiseUserList')
def GetRoleWiseUserList(tenantId, roleId):
    try:
        from accounts.models import Profile
        profileCount = Profile.objects.filter(tenantProfile_id=tenantId, role_id=roleId).count()
        if profileCount == 0:
            return mark_safe(
                '<h6 class="fw-normal mb-0 text-body"><span class="text-danger">User not available </span></h6>'
                '<ul class="list-unstyled d-flex align-items-center avatar-group mb-0">'
                '<li class="avatar"><span class="avatar-initial rounded-circle pull-up" '
                'data-bs-toggle="tooltip" data-bs-placement="bottom" title="NA">NA</span></li></ul>'
            )
        profileList = Profile.objects.filter(
            tenantProfile_id=tenantId, role_id=roleId,
            profile_picture_s3_url__isnull=False
        ).select_related('user').only(
            'user__first_name', 'user__last_name', 'profile_picture_s3_url'
        )[:3]
        users_html = ''.join(
            '<li data-bs-toggle="tooltip" data-popup="tooltip-custom" data-bs-placement="top " '
            f'title="{p.user.first_name} {p.user.last_name}" class="avatar pull-up">'
            '<i class="ti tabler-users" style="font-size: 35px;"></i>'
            for p in profileList
        )
        extra = profileCount - 3 if profileCount > 3 else 0
        extra_html = ''
        if extra > 0:
            extra_html = (
                f'<li class="avatar"><span class="avatar-initial rounded-circle pull-up" '
                f'data-bs-toggle="tooltip" data-bs-placement="bottom" title="{extra} more">'
                f'+{extra}</span></li>'
            )
        return mark_safe(
            f'<h6 class="fw-normal mb-0 text-body">Total {profileCount} users</h6>'
            f'<ul class="list-unstyled d-flex align-items-center avatar-group mb-0">'
            f'{users_html}{extra_html}</ul>'
        )
    except Exception:
        return mark_safe('')


@register.simple_tag
def GetTenantName(tenantId):
    from tenant.models import TenantProfile
    tenant = TenantProfile.objects.filter(pk=tenantId).only('tenant_name').first()
    return tenant.tenant_name if tenant else ''


@register.simple_tag
def CurrentTime(format_string):
    return datetime.now().strftime(format_string)

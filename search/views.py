from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from accounts.models import Profile

SEARCH_REGISTRY = []
def register(label, icon, model, fields, url, limit=5, tenant_filter=False, display_fn=None, url_fn=None):
    SEARCH_REGISTRY.append({ 'label': label, 'icon': icon, 'model': model, 'fields': fields,
                             'url': url, 'limit': limit, 'tenant_filter': tenant_filter,
                             'display_fn': display_fn, 'url_fn': url_fn,})

register('Users', 'tabler-user', Profile, ['user__first_name', 'user__last_name', 'user__email'],
         '/user/list/', tenant_filter=True, limit=5,
         display_fn=lambda o: f"{o.user.first_name} {o.user.last_name}".strip() + f" ({o.user.email})",
         url_fn=lambda o: f"/user/list/{o.user.id}/update/")


def _make_display(obj):
    return str(obj)


@login_required
def global_search(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 3:
        return JsonResponse({'results': []})

    words = q.split()
    results = {}
    for entry in SEARCH_REGISTRY:
        qs = entry['model'].objects
        q_filter = Q()
        for word in words:
            word_filter = Q()
            for field in entry['fields']:
                word_filter |= Q(**{f'{field}__icontains': word})
            q_filter &= word_filter

        if entry['tenant_filter']:
            qs = qs.filter(tenantProfile_id=request.tenantID)

        related_map = { 'Users': ['user']}
        related = related_map.get(entry['label'], [])
        if related:
            qs = qs.select_related(*related)

        items = []
        for obj in qs.filter(q_filter)[:entry['limit']]:
            label = (entry['display_fn'] or _make_display)(obj)
            url = (entry['url_fn'](obj) if entry['url_fn'] else entry['url'])
            items.append({'label': label, 'url': url, 'icon': entry['icon']})

        if items:
            key = entry['label'].lower().replace(' ', '_')
            results[key] = {'icon': entry['icon'], 'items': items}

    return JsonResponse({'results': results})

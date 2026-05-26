import json
from django.http import HttpResponse

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from accounts.base import  Base
from accounts.helpers.decorators import CheckRole
from masters.models import Country, State, District, Currency, Division, Zone, City

from tenant.models import TimeZone, DateFormat, TimeFormat
from accounts.helpers.import_export_utils import export_csv, export_xlsx, parse_upload


@login_required
def GetStateListJson(request, **kwargs):
    if request.method == 'GET':
        countryID = request.GET['countryID']
        qs = State.objects.filter(is_active=True).order_by('state_name')
        if int(countryID) > 0:
            qs = qs.filter(country=countryID)
        data = [{"pk": s["state_id"], "fields": {"state_name": s["state_name"]}}
                for s in qs.values("state_id", "state_name")]
        return HttpResponse(json.dumps(data))




def _render_partial(request, template, context):
    return render(request, template, context)


# =========================================================
# COUNTRY
# =========================================================

@login_required
@CheckRole(Base.Group.SetupGroup.value)
def setup_master(request):
    return render(request, "master/setup_master.html")


@login_required
def CountryList(request):
    countries = Country.objects.all().order_by('country_name')
    return _render_partial(request, "master/partials/_country_list.html", {'countries': countries})


@login_required
def AddUpdateCountry(request, pk=0):
    country = Country.objects.filter(country_id=pk).first() if pk else None
    if request.method == "POST":
        name = request.POST.get("country_name", "").strip()
        is_active = request.POST.get("is_active") == "on"
        if name:
            if country:
                country.country_name = name
                country.is_active = is_active
                country.save()
            else:
                Country.objects.create(country_name=name, is_active=is_active)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Country name is required'})
    return _render_partial(request, "master/partials/_country_form.html", {'country': country})


@login_required
def DeleteCountry(request):
    pk = request.POST.get("pk")
    Country.objects.filter(country_id=pk).delete()
    return JsonResponse({'success': True})


# =========================================================
# CURRENCY
# =========================================================

@login_required
def CurrencyList(request):
    currencies = Currency.objects.all().order_by('currency_code')
    return _render_partial(request, "master/partials/_currency_list.html", {'currencies': currencies})


@login_required
def AddUpdateCurrency(request, pk=0):
    currency = Currency.objects.filter(currency_id=pk).first() if pk else None
    if request.method == "POST":
        code = request.POST.get("currency_code", "").strip()
        symbol = request.POST.get("currency_symbol", "").strip()
        is_active = request.POST.get("is_active") == "on"
        if code and symbol:
            if currency:
                currency.currency_code = code
                currency.currency_symbol = symbol
                currency.is_active = is_active
                currency.save()
            else:
                Currency.objects.create(currency_code=code, currency_symbol=symbol, is_active=is_active)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Currency code and symbol are required'})
    return _render_partial(request, "master/partials/_currency_form.html", {'currency': currency})


@login_required
def DeleteCurrency(request):
    pk = request.POST.get("pk")
    Currency.objects.filter(currency_id=pk).delete()
    return JsonResponse({'success': True})


# =========================================================
# STATE
# =========================================================

@login_required
def StateList(request):
    states = State.objects.select_related('country').all().order_by('state_name')
    return _render_partial(request, "master/partials/_state_list.html", {'states': states})


@login_required
def AddUpdateState(request, pk=0):
    state = State.objects.filter(state_id=pk).first() if pk else None
    countries = Country.objects.filter(is_active=True)
    if request.method == "POST":
        name = request.POST.get("state_name", "").strip()
        country_id = request.POST.get("country_id")
        is_active = request.POST.get("is_active") == "on"
        if name and country_id:
            if state:
                state.state_name = name
                state.country_id = country_id
                state.is_active = is_active
                state.save()
            else:
                State.objects.create(state_name=name, country_id=country_id, is_active=is_active)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'State name and country are required'})
    return _render_partial(request, "master/partials/_state_form.html", {'state': state, 'countries': countries})


@login_required
def DeleteState(request):
    pk = request.POST.get("pk")
    State.objects.filter(state_id=pk).delete()
    return JsonResponse({'success': True})


# =========================================================
# DIVISION
# =========================================================

@login_required
def DivisionList(request):
    divisions = Division.objects.select_related('state', 'state__country').all().order_by('division_name')
    return _render_partial(request, "master/partials/_division_list.html", {'divisions': divisions})


@login_required
def AddUpdateDivision(request, pk=0):
    division = Division.objects.filter(division_id=pk).first() if pk else None
    countries = Country.objects.filter(is_active=True)
    states = State.objects.filter(is_active=True)
    if request.method == "POST":
        name = request.POST.get("division_name", "").strip()
        code = request.POST.get("division_code", "").strip()
        state_id = request.POST.get("state_id")
        is_active = request.POST.get("is_active") == "on"
        if name and state_id:
            if division:
                division.division_name = name
                division.division_code = code or None
                division.state_id = state_id
                division.is_active = is_active
                division.save()
            else:
                Division.objects.create(
                    division_name=name,
                    division_code=code or None,
                    state_id=state_id,
                    is_active=is_active,
                )
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Division name and state are required'})
    return _render_partial(request, "master/partials/_division_form.html", {
        'division': division, 'countries': countries, 'states': states
    })


@login_required
def DeleteDivision(request):
    pk = request.POST.get("pk")
    Division.objects.filter(division_id=pk).delete()
    return JsonResponse({'success': True})


# =========================================================
# DISTRICT
# =========================================================

@login_required
def DistrictList(request):
    districts = District.objects.select_related('state', 'division', 'zone').all().order_by('district_name')
    return _render_partial(request, "master/partials/_district_list.html", {'districts': districts})


@login_required
def AddUpdateDistrict(request, pk=0):
    district = District.objects.filter(district_id=pk).first() if pk else None
    countries = Country.objects.filter(is_active=True)
    states = State.objects.filter(is_active=True)
    divisions = Division.objects.filter(is_active=True)
    zones = Zone.objects.filter(is_active=True).select_related('state')
    if request.method == "POST":
        name = request.POST.get("district_name", "").strip()
        state_id = request.POST.get("state_id")
        division_id = request.POST.get("division_id") or None
        zone_id = request.POST.get("zone_id") or None
        is_active = request.POST.get("is_active") == "on"
        if name and state_id:
            if district:
                district.district_name = name
                district.state_id = state_id
                district.division_id = division_id
                district.zone_id = zone_id
                district.is_active = is_active
                district.save()
            else:
                District.objects.create(
                    district_name=name,
                    state_id=state_id,
                    division_id=division_id,
                    zone_id=zone_id,
                    is_active=is_active,
                )
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'District name and state are required'})
    return _render_partial(request, "master/partials/_district_form.html", {
        'district': district, 'countries': countries, 'states': states, 'divisions': divisions, 'zones': zones
    })


@login_required
def DeleteDistrict(request):
    pk = request.POST.get("pk")
    District.objects.filter(district_id=pk).delete()
    return JsonResponse({'success': True})


# =========================================================
# ZONE
# =========================================================

@login_required
def ZoneList(request):
    zones = Zone.objects.select_related('state').all().order_by('zone_name')
    return _render_partial(request, "master/partials/_zone_list.html", {'zones': zones})


@login_required
def AddUpdateZone(request, pk=0):
    zone = Zone.objects.filter(zone_id=pk).first() if pk else None
    states = State.objects.filter(is_active=True)
    if request.method == "POST":
        name = request.POST.get("zone_name", "").strip()
        name_hindi = request.POST.get("zone_name_hindi", "").strip()
        state_id = request.POST.get("state_id") or None
        sequence = request.POST.get("sequence") or 1
        is_active = request.POST.get("is_active") == "on"
        if name and state_id:
            if zone:
                zone.zone_name = name
                zone.zone_name_hindi = name_hindi or None
                zone.state_id = state_id
                zone.sequence = sequence
                zone.is_active = is_active
                zone.save()
            else:
                Zone.objects.create(
                    zone_name=name,
                    zone_name_hindi=name_hindi or None,
                    state_id=state_id,
                    sequence=sequence,
                    is_active=is_active,
                )
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Zone name and state are required'})
    return _render_partial(request, "master/partials/_zone_form.html", {'zone': zone, 'states': states})


@login_required
def DeleteZone(request):
    pk = request.POST.get("pk")
    Zone.objects.filter(zone_id=pk).delete()
    return JsonResponse({'success': True})


# =========================================================
# CITY
# =========================================================

@login_required
def CityList(request):
    cities = City.objects.select_related('district', 'district__state').all().order_by('city_name')
    return _render_partial(request, "master/partials/_city_list.html", {'cities': cities})


@login_required
def AddUpdateCity(request, pk=0):
    city = City.objects.filter(city_id=pk).first() if pk else None
    districts = District.objects.filter(is_active=True).select_related('state')
    if request.method == "POST":
        name = request.POST.get("city_name", "").strip()
        name_hindi = request.POST.get("city_name_hindi", "").strip()
        district_id = request.POST.get("district_id") or None
        sequence = request.POST.get("sequence") or 1
        is_active = request.POST.get("is_active") == "on"
        if name:
            if city:
                city.city_name = name
                city.city_name_hindi = name_hindi or None
                city.district_id = district_id
                city.sequence = sequence
                city.is_active = is_active
                city.save()
            else:
                City.objects.create(
                    city_name=name,
                    city_name_hindi=name_hindi or None,
                    district_id=district_id,
                    sequence=sequence,
                    is_active=is_active,
                )
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'City name is required'})
    return _render_partial(request, "master/partials/_city_form.html", {'city': city, 'districts': districts})


@login_required
def DeleteCity(request):
    pk = request.POST.get("pk")
    City.objects.filter(city_id=pk).delete()
    return JsonResponse({'success': True})


# =========================================================
# TIME ZONE
# =========================================================

@login_required
def TimeZoneList(request):
    timezones = TimeZone.objects.all().order_by('time_zone_name')
    return _render_partial(request, "master/partials/_timezone_list.html", {'timezones': timezones})


@login_required
def AddUpdateTimeZone(request, pk=0):
    tz = TimeZone.objects.filter(time_zone_id=pk).first() if pk else None
    if request.method == "POST":
        name = request.POST.get("time_zone_name", "").strip()
        label = request.POST.get("display_label", "").strip()
        offset = request.POST.get("utc_offset", "").strip()
        is_active = request.POST.get("is_active") == "on"
        if name and label:
            if tz:
                tz.time_zone_name = name
                tz.display_label = label
                tz.utc_offset = offset or None
                tz.is_active = is_active
                tz.save()
            else:
                TimeZone.objects.create(time_zone_name=name, display_label=label, utc_offset=offset or None, is_active=is_active)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Time zone name and display label are required'})
    return _render_partial(request, "master/partials/_timezone_form.html", {'tz': tz})


@login_required
def DeleteTimeZone(request):
    pk = request.POST.get("pk")
    TimeZone.objects.filter(time_zone_id=pk).delete()
    return JsonResponse({'success': True})


# =========================================================
# DATE FORMAT
# =========================================================

@login_required
def DateFormatList(request):
    formats = DateFormat.objects.all().order_by('display_label')
    return _render_partial(request, "master/partials/_dateformat_list.html", {'formats': formats})


@login_required
def AddUpdateDateFormat(request, pk=0):
    fmt = DateFormat.objects.filter(date_format_id=pk).first() if pk else None
    if request.method == "POST":
        value = request.POST.get("format_value", "").strip()
        label = request.POST.get("display_label", "").strip()
        is_active = request.POST.get("is_active") == "on"
        if value and label:
            if fmt:
                fmt.format_value = value
                fmt.display_label = label
                fmt.is_active = is_active
                fmt.save()
            else:
                DateFormat.objects.create(format_value=value, display_label=label, is_active=is_active)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Format value and display label are required'})
    return _render_partial(request, "master/partials/_dateformat_form.html", {'fmt': fmt})


@login_required
def DeleteDateFormat(request):
    pk = request.POST.get("pk")
    DateFormat.objects.filter(date_format_id=pk).delete()
    return JsonResponse({'success': True})


# =========================================================
# TIME FORMAT
# =========================================================

@login_required
def TimeFormatList(request):
    formats = TimeFormat.objects.all().order_by('display_label')
    return _render_partial(request, "master/partials/_timeformat_list.html", {'formats': formats})


@login_required
def AddUpdateTimeFormat(request, pk=0):
    fmt = TimeFormat.objects.filter(time_format_id=pk).first() if pk else None
    if request.method == "POST":
        value = request.POST.get("format_value", "").strip()
        label = request.POST.get("display_label", "").strip()
        is_active = request.POST.get("is_active") == "on"
        if value and label:
            if fmt:
                fmt.format_value = value
                fmt.display_label = label
                fmt.is_active = is_active
                fmt.save()
            else:
                TimeFormat.objects.create(format_value=value, display_label=label, is_active=is_active)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Format value and display label are required'})
    return _render_partial(request, "master/partials/_timeformat_form.html", {'fmt': fmt})


@login_required
def DeleteTimeFormat(request):
    pk = request.POST.get("pk")
    TimeFormat.objects.filter(time_format_id=pk).delete()
    return JsonResponse({'success': True})


# =============================================================
# IMPORT / EXPORT – reused helpers
# =============================================================

ENTITY_CONFIG = {
    'Country': {
        'model': Country,
        'fields': ['country_name', 'is_active'],
        'headers': {'country_name': 'Country Name', 'is_active': 'Active'},
        'unique': ['country_name'],
    },
    'Currency': {
        'model': Currency,
        'fields': ['currency_code', 'currency_symbol', 'is_active'],
        'headers': {'currency_code': 'Code', 'currency_symbol': 'Symbol', 'is_active': 'Active'},
        'unique': ['currency_code'],
    },
    'State': {
        'model': State,
        'fields': ['state_name', 'country__country_name', 'is_active'],
        'headers': {'state_name': 'State Name', 'country__country_name': 'Country Name', 'is_active': 'Active'},
        'unique': ['state_name'],
    },
    'District': {
        'model': District,
        'fields': ['district_name', 'state__state_name', 'division__division_name', 'zone__zone_name', 'is_active'],
        'headers': {'district_name': 'District Name', 'state__state_name': 'State Name', 'division__division_name': 'Division Name', 'zone__zone_name': 'Zone Name', 'is_active': 'Active'},
        'unique': ['district_name'],
    },
    'Division': {
        'model': Division,
        'fields': ['division_name', 'division_code', 'state__state_name', 'is_active'],
        'headers': {'division_name': 'Division Name', 'division_code': 'Division Code', 'state__state_name': 'State Name', 'is_active': 'Active'},
        'unique': ['division_name'],
    },
    'Zone': {
        'model': Zone,
        'fields': ['zone_name', 'zone_name_hindi', 'state__state_name', 'sequence', 'is_active'],
        'headers': {'zone_name': 'Zone Name', 'zone_name_hindi': 'Hindi Name', 'state__state_name': 'State Name', 'sequence': 'Sequence', 'is_active': 'Active'},
        'unique': ['zone_name'],
    },
    'City': {
        'model': City,
        'fields': ['city_name', 'city_name_hindi', 'district__district_name', 'sequence', 'is_active'],
        'headers': {'city_name': 'City Name', 'city_name_hindi': 'Hindi Name', 'district__district_name': 'District Name', 'sequence': 'Sequence', 'is_active': 'Active'},
        'unique': ['city_name'],
    },
    'TimeZone': {
        'model': TimeZone,
        'fields': ['time_zone_name', 'display_label', 'utc_offset', 'is_active'],
        'headers': {'time_zone_name': 'Time Zone Name', 'display_label': 'Display Label', 'utc_offset': 'UTC Offset', 'is_active': 'Active'},
        'unique': ['time_zone_name'],
    },
    'DateFormat': {
        'model': DateFormat,
        'fields': ['format_value', 'display_label', 'is_active'],
        'headers': {'format_value': 'Format Value', 'display_label': 'Display Label', 'is_active': 'Active'},
        'unique': ['format_value'],
    },
    'TimeFormat': {
        'model': TimeFormat,
        'fields': ['format_value', 'display_label', 'is_active'],
        'headers': {'format_value': 'Format Value', 'display_label': 'Display Label', 'is_active': 'Active'},
        'unique': ['format_value'],
    },
}


def _get_export_queryset(entity_name):
    cfg = ENTITY_CONFIG[entity_name]
    return cfg['model'].objects.all()


def _bool(val):
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ('1', 'yes', 'true', 'active', 'on')


def _build_lookup_cache(entity_name):
    fields = ENTITY_CONFIG[entity_name]['fields']
    cache = {}
    if 'country__country_name' in fields:
        cache['country'] = {c.country_name: c for c in Country.objects.all()}
    if 'state__state_name' in fields:
        cache['state'] = {s.state_name: s for s in State.objects.all()}
    if 'division__division_name' in fields:
        cache['division'] = {d.division_name: d for d in Division.objects.all()}
    if 'district__district_name' in fields:
        cache['district'] = {d.district_name: d for d in District.objects.all()}
    if 'zone__zone_name' in fields:
        cache['zone'] = {z.zone_name: z for z in Zone.objects.all()}
    return cache


def _resolve_row(entity_name, row, lookup_cache=None):
    kwargs = {}
    cfg = ENTITY_CONFIG[entity_name]
    rev_headers = {v: k for k, v in cfg['headers'].items()}
    lc = lookup_cache or {}

    for col_name, raw in row.items():
        field = rev_headers.get(col_name)
        if not field:
            continue
        if field == 'is_active':
            kwargs[field] = _bool(raw)
        elif field == 'country__country_name':
            kwargs['country'] = lc.get('country', {}).get(raw) if raw else None
        elif field == 'state__state_name':
            kwargs['state'] = lc.get('state', {}).get(raw) if raw else None
        elif field == 'division__division_name':
            kwargs['division'] = lc.get('division', {}).get(raw) if raw else None
        elif field == 'district__district_name':
            kwargs['district'] = lc.get('district', {}).get(raw) if raw else None
        elif field == 'zone__zone_name':
            kwargs['zone'] = lc.get('zone', {}).get(raw) if raw else None
        elif field == 'sequence':
            kwargs[field] = int(raw) if str(raw).strip() else 1
        else:
            kwargs[field] = raw
    return kwargs


# --- GENERIC EXPORT VIEWS ---

@login_required
def ExportCSV(request, entity_name):
    qs = _get_export_queryset(entity_name)
    cfg = ENTITY_CONFIG[entity_name]
    return export_csv(qs, cfg['fields'], cfg['headers'], entity_name)


@login_required
def ExportExcel(request, entity_name):
    qs = _get_export_queryset(entity_name)
    cfg = ENTITY_CONFIG[entity_name]
    return export_xlsx(qs, cfg['fields'], cfg['headers'], entity_name)


# --- GENERIC IMPORT VIEW ---

@login_required
def ImportData(request, entity_name):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    cfg = ENTITY_CONFIG.get(entity_name)
    if not cfg:
        return JsonResponse({'success': False, 'error': 'Unknown entity'})

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
    lookup_cache = _build_lookup_cache(entity_name)

    for idx, row in enumerate(rows, start=2):
        try:
            kwargs = _resolve_row(entity_name, row, lookup_cache)
            if not kwargs:
                continue

            unique_field = cfg['unique'][0]
            unique_val = kwargs.get(unique_field)
            if unique_val:
                existing = cfg['model'].objects.filter(**{unique_field: unique_val}).first()
                if existing:
                    for k, v in kwargs.items():
                        setattr(existing, k, v)
                    existing.save()
                    updated += 1
                    continue

            cfg['model'].objects.create(**kwargs)
            created += 1
        except Exception as e:
            errors.append(f"Row {idx}: {e}")

    msg = f"Imported: {created} created, {updated} updated"
    if errors:
        msg += f", {len(errors)} errors: {'; '.join(errors[:5])}"

    return JsonResponse({'success': True, 'message': msg, 'created': created, 'updated': updated, 'errors': len(errors)})

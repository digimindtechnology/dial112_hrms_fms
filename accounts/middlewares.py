from django.utils.deprecation import MiddlewareMixin
from rest_framework.authtoken.models import Token
from accounts.helpers.basicUtility import GetFileUrl
from DmtHrmsFmsApp.settings import COPY_RIGHT_INFORMATION, S3_URL,MEDIA_URL,IS_FILE_UPLOAD_S3
from accounts.models import Profile


class RoleMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return None

        filePath = S3_URL if IS_FILE_UPLOAD_S3 else f"{MEDIA_URL}"
        request.COPY_RIGHT_INFORMATION = COPY_RIGHT_INFORMATION
        request.filePath = filePath
        request.image = f'{filePath}default.jpg'
        request.roleID = 1
        request.role = ''
        request.tenantID = 0
        request.tenantName = ''

        request.tenantLogo = f'{filePath}digimind.png'
        request.tenantFavicon = f'{filePath}favicon.ico'
        request.currencySymbol = '\u20b9'
        request.is_company_setup = False
        request.is_system_assigned_password = False

        request.usertoken = ''
        request.time_zone_name = ''
        request.time_zone_utc_offset = ''
        request.time_zone_display_label = ''

        request.date_format_value = ''
        request.date_display_label = ''

        request.time_format_value = ''
        request.time_display_label = ''

        request.module = ''
        request.breadcrumb = ''
        request.title = ''
        request.pagetitle = ''

        # -------------------------------------------------
        # Breadcrumb Logic
        # -------------------------------------------------
        path_segments = request.path.strip('/').split('/')
        segments = [seg.replace('_', ' ').replace('-', ' ').title() for seg in path_segments if
                    seg and not seg.isdigit()]

        if segments:
            request.module = segments[0]
            request.pagetitle = segments[-1]

            if len(segments) > 1:
                request.breadcrumb = ' / '.join(segments[1:])
            request.title = ' : '.join(segments)
        # -------------------------------------------------
        # Profile Query (Single Query)
        # -------------------------------------------------
        profile = (
            Profile.objects
            .select_related(
                'role',
                'currency',
                'time_zone',
                'date_formate_view',
                'time_formate_view',
                'tenantProfile',
                'tenantProfile__currency',
                'tenantProfile__time_zone',
                'tenantProfile__date_formate_view',
                'tenantProfile__time_formate_view',
            ).prefetch_related('role__group').filter(user_id=user.id).first())

        if not profile:
            return None

        # -------------------------------------------------
        # Profile Data
        # -------------------------------------------------
        request.is_company_setup = (profile.is_company_setup)

        request.is_system_assigned_password = (profile.is_system_assigned_password)

        if profile.profile_picture_s3_url:
            request.image = GetFileUrl(profile.profile_picture_s3_url)

        # -------------------------------------------------
        # Role Data
        # -------------------------------------------------
        role = profile.role
        if role:
            request.roleID = role.role_id
            request.role = role.role_name
            role_groups = role.group.all()
            role_group_ids = {group.id for group in role_groups}

            user_group_ids = set(user.groups.values_list('id', flat=True))

            # Sync only if changed
            if role_group_ids != user_group_ids:
                user.groups.set(role_groups)

        # -------------------------------------------------
        # Tenant/Profile Settings
        # Profile > Tenant > Default
        # -------------------------------------------------
        tenant = profile.tenantProfile

        if tenant:
            request.tenantID = (tenant.tenant_profile_id)
            request.tenantName = (tenant.tenant_name)

            # ---------- Currency ----------
            currency = (profile.currency or tenant.currency)
            request.currencySymbol = (currency.currency_symbol if currency else '\u20b9')

            # ---------- Timezone ----------
            timezone = (profile.time_zone or tenant.time_zone)
            if timezone:
                request.time_zone_name = (timezone.time_zone_name or '')
                request.time_zone_utc_offset = (timezone.utc_offset or '')
                request.time_zone_display_label = (timezone.display_label or '')

            # ---------- Date Format ----------
            date_format = (profile.date_formate_view or tenant.date_formate_view)
            if date_format:
                request.date_format_value = (date_format.format_value or '')
                request.date_display_label = (date_format.display_label or '')

            # ---------- Time Format ----------
            time_format = (profile.time_formate_view or tenant.time_formate_view)
            if time_format:
                request.time_format_value = (time_format.format_value or '')
                request.time_display_label = (time_format.display_label or '')

            # ---------- Logo / Favicon ----------
            if request.is_company_setup:
                logo = tenant.tenant_logo_s3_url
                favicon = tenant.tenant_favicon_s3_url
                if logo:
                    request.tenantLogo = f'{filePath}{logo}'
                if favicon:
                    request.tenantFavicon = f'{filePath}{favicon}'

        request.usertoken = (Token.objects.filter(user_id=user.id).values_list('key', flat=True).first() or '')
        return None

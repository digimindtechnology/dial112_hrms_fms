from django.contrib.auth.models import User, Group
from django.db import models
from masters.models import Country, State, Currency


class SocialConnectionType(models.Model):
    social_connection_id = models.AutoField(primary_key=True)
    social_connection_name = models.CharField(max_length=100)
    social_connection_icon = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('social_connection_name',)

    def __str__(self):
        return self.social_connection_name


class TimeZone(models.Model):
    time_zone_id = models.AutoField(primary_key=True)
    time_zone_name = models.CharField(max_length=100, unique=True)
    display_label = models.CharField(max_length=200)
    utc_offset = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('time_zone_name',)

    def __str__(self):
        return self.display_label or self.time_zone_name


class DateFormat(models.Model):
    date_format_id = models.AutoField(primary_key=True)
    format_value = models.CharField(max_length=50, unique=True)
    display_label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('display_label',)

    def __str__(self):
        return self.display_label


class TimeFormat(models.Model):
    time_format_id = models.AutoField(primary_key=True)
    format_value = models.CharField(max_length=50, unique=True)
    display_label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('display_label',)

    def __str__(self):
        return self.display_label


class TenantProfile(models.Model):
    tenant_profile_id = models.AutoField(primary_key=True)
    tenant_name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    address = models.TextField(max_length=1000, null=True, blank=True)

    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.CASCADE)
    state = models.ForeignKey(State, null=True, blank=True, on_delete=models.CASCADE)
    city = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(max_length=100)
    mobile = models.CharField(max_length=10)

    phone_number = models.CharField(max_length=50, null=True, blank=True)
    fax = models.CharField(max_length=50, null=True, blank=True)
    gst = models.CharField(max_length=20, null=True, blank=True)
    pan = models.CharField(max_length=20, null=True, blank=True)
    website_url = models.CharField(max_length=100, null=True, blank=True)
    website_name = models.CharField(max_length=50, null=True, blank=True)

    admin_user = models.ForeignKey(User, related_name='admin_user_TenantProfile', on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    time_zone = models.ForeignKey(TimeZone, null=True, blank=True, on_delete=models.SET_NULL)
    date_formate_view = models.ForeignKey(DateFormat, null=True, blank=True, on_delete=models.SET_NULL)
    time_formate_view = models.ForeignKey(TimeFormat, null=True, blank=True, on_delete=models.SET_NULL)

    tenant_logo_s3_url = models.CharField(max_length=1000, null=True, blank=True)
    tenant_favicon_s3_url = models.CharField(max_length=1000, null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('tenant_name',)
        indexes = [
            models.Index(fields=['tenant_name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.tenant_name


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=100)
    role_short_name = models.CharField(max_length=100)
    tenantProfile = models.ForeignKey(TenantProfile, blank=True, null=True, related_name='tenantProfile_Role',on_delete=models.CASCADE)
    system_role_id = models.IntegerField(blank=True, null=True)
    sequence = models.IntegerField(default=0)
    group = models.ManyToManyField(Group, related_name='RoleGroup', blank=True, null=True, )
    role_desc = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('role_name',)
        indexes = [
            models.Index(fields=['tenantProfile']),
        ]

    def __str__(self):
        return self.role_name

    def get_assigned_group_name(self):
        return ", ".join([g.name for g in self.group.all().order_by('name')])


class SocialConnection(models.Model):
    social_connection_id = models.AutoField(primary_key=True)
    social_connection_url = models.CharField(max_length=500, null=True, blank=True)
    socialConnectionType = models.ForeignKey(SocialConnectionType, related_name='socialConnectionType_SocialConnection',
                                             on_delete=models.CASCADE)
    tenant = models.ForeignKey(TenantProfile, related_name='tenant_SocialConnection', on_delete=models.CASCADE,
                               verbose_name="Company")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('socialConnectionType__social_connection_name',)

    def __str__(self):
        return self.socialConnectionType__social_connection_name

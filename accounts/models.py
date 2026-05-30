from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from masters.models import (Country, State, Division, District, Gender, Currency, BaseModel)
from tenant.models import Role, TenantProfile, TimeZone, DateFormat, TimeFormat


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.CASCADE)
    profile_picture_s3_url = models.CharField(max_length=1000, null=True, blank=True)

    mobile = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)

    country = models.ForeignKey(Country, related_name='country_profile', null=True, blank=True, on_delete=models.CASCADE)
    state = models.ForeignKey(State, related_name='state_profile', null=True, blank=True, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, related_name='division_profile', null=True, blank=True, on_delete=models.CASCADE)
    district = models.ForeignKey(District, related_name='district_profile', null=True, blank=True, on_delete=models.CASCADE)

    currency = models.ForeignKey(Currency, null=True, blank=True, on_delete=models.SET_NULL)
    time_zone = models.ForeignKey(TimeZone, null=True, blank=True, on_delete=models.SET_NULL)
    date_formate_view = models.ForeignKey(DateFormat, null=True, blank=True, on_delete=models.SET_NULL)
    time_formate_view = models.ForeignKey(TimeFormat, null=True, blank=True, on_delete=models.SET_NULL)

    city = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    gender = models.ForeignKey(Gender, null=True, blank=True, on_delete=models.CASCADE)

    designation = models.CharField(max_length=100)
    is_company_setup = models.BooleanField(default=False)

    is_system_assigned_password = models.BooleanField(default=True)

    user_otp = models.CharField(max_length=20, null=True, blank=True)
    user_otp_expire_date = models.DateTimeField(null=True, blank=True)
    is_login_with_otp = models.BooleanField(default=False)
    total_resend_otp = models.IntegerField(default=0)
    total_wrong_otp = models.IntegerField(default=0)

    tenantProfile = models.ForeignKey(TenantProfile, blank=True, null=True, related_name='tenantProfile_Profile', on_delete=models.CASCADE, verbose_name="Company")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="created_by_profile")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="updated_by_profile")

    class Meta:
        ordering = ('user__username',)
        indexes = [
            models.Index(fields=['tenantProfile']),
            models.Index(fields=['user']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return "{0} - {1} {2} ({3})".format(self.user.username, self.user.first_name, self.user.last_name, self.role.role_name if self.role else 'N/A')


class UserLoginTrace(models.Model):
    user_login_trace_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, blank=True, related_name='user_profile_web_login', on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    ip_or_mac = models.CharField(max_length=50)
    browser_os_info = models.CharField(max_length=1000, null=True, blank=True)
    message = models.CharField(max_length=1000)
    created_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_date']),
        ]

class UserDistrictMapping(models.Model):
    user_district_mapping_id = models.AutoField(primary_key=True)
    district = models.ForeignKey(District, related_name='district_UserDistrictMapping', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_UserDistrictMapping', on_delete=models.CASCADE)
    tenantProfile = models.ForeignKey(TenantProfile, blank=True, null=True, related_name='tenantProfile_UserDistrictMapping', on_delete=models.CASCADE, verbose_name="Company")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="created_by_UserDistrictMapping")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="updated_by_UserDistrictMapping")
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('district',)
        constraints = [
            models.UniqueConstraint(fields=['district', 'user', 'tenantProfile'], name='district_user_tenantProfile_UserDistrictMapping')
        ]

    def __str__(self):
        return self.district.district_name

@receiver(post_save, sender=User)
def user_is_created(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

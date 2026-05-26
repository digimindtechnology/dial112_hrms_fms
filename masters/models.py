from django.db import models
from django.contrib.auth.models import User, Group


class BaseModel(models.Model):
    remark = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
class MenuType(models.Model):
    menu_type_id = models.AutoField(primary_key=True)
    menu_type_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('menu_type_name',)

    def __str__(self):
        return self.menu_type_name
class Menu(models.Model):
    menu_id = models.AutoField(primary_key=True)
    menu_name = models.CharField(max_length=100)
    menu_icon = models.CharField(max_length=100)
    menu_slug = models.CharField(max_length=70, db_index=True, null=True, blank=True, default="#")
    menu_args = models.IntegerField(null=True, blank=True)
    sequence_order = models.IntegerField(default=0)
    menuType = models.ForeignKey(MenuType, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', verbose_name="Parent", on_delete=models.CASCADE,
                               limit_choices_to={'parent__isnull': True, 'menuType__menu_type_id': 2}, blank=True,
                               null=True, related_name='children')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('sequence_order',)

    def __str__(self):
        return self.menu_name
class Menu_Group(models.Model):
    menu_group_id = models.AutoField(primary_key=True)
    menu_group_name = models.CharField(max_length=400)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    menu = models.ManyToManyField(Menu)
    is_active = models.BooleanField(default=True)
    is_permission_required = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    is_write = models.BooleanField(default=False)
    is_create = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_import = models.BooleanField(default=False)
    is_export = models.BooleanField(default=False)

    class Meta:
        ordering = ('menu_group_name',)

    def __str__(self):
        return self.menu_group_name

    def get_assigned_menu_name(self):
        return ", ".join([p.menu_name for p in self.menu.all()])
class Gender(models.Model):
    gender_id = models.AutoField(primary_key=True)
    gender_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['gender_name']

    def __str__(self):
        return self.gender_name

class Currency(models.Model):
    currency_id = models.AutoField(primary_key=True)
    currency_code = models.CharField(max_length=10)
    currency_symbol = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('currency_code',)

    def __str__(self):
        return self.currency_code + ' - ' + self.currency_symbol

class Country(models.Model):
    country_id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('country_name',)

    def __str__(self):
        return self.country_name
class State(models.Model):
    state_id = models.AutoField(primary_key=True)
    state_name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('state_name',)
        indexes = [
            models.Index(fields=['country']),
            models.Index(fields=['state_name']),
        ]

    def __str__(self):
        return self.state_name

class Division(models.Model):
    division_id = models.AutoField(primary_key=True)
    division_code = models.CharField(max_length=30, null=True, blank=True)
    division_name = models.CharField(max_length=30)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='state_Division')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('division_name',)
        indexes = [
            models.Index(fields=['state']),
        ]

    def __str__(self):
        return self.division_name

class Zone(models.Model):
    zone_id = models.AutoField(primary_key=True)
    zone_name = models.CharField(max_length=100)
    zone_name_hindi = models.CharField(max_length=100,null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE,related_name='state_Zone')
    sequence= models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ('zone_name',)

    def __str__(self):
        return self.zone_name + ' - ' + self.state.state_name

class District(models.Model):
    district_id = models.AutoField(primary_key=True)
    district_name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE,related_name='state_District')
    division = models.ForeignKey(Division, on_delete=models.CASCADE, null=True, blank=True,related_name='division_District')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, null=True, blank=True,related_name='zone_District')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('district_name',)
        indexes = [
            models.Index(fields=['state']),
            models.Index(fields=['division']),
            models.Index(fields=['zone']),
        ]

    def __str__(self):
        return self.district_name + ' - ' + self.state.state_name


class City(models.Model):
    city_id = models.AutoField(primary_key=True)
    city_name = models.CharField(max_length=100)
    city_name_hindi = models.CharField(max_length=100,null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE,null=True,blank=True)
    sequence= models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering = ('city_name',)

    def __str__(self):
        district_name = self.district.district_name if self.district else 'N/A'
        return self.city_name + ' - ' + district_name


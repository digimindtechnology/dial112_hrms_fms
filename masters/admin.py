from django.contrib import admin
from masters.models import Gender, Currency, Country, State, Division, District, MenuType, Menu, Menu_Group


admin.site.register(Gender)
admin.site.register(Currency)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(Division)
admin.site.register(District)

class MenuTypeAdmin(admin.ModelAdmin):
    model = MenuType
    list_display = ('__str__','is_active',)
    list_filter = (
        ('is_active', admin.BooleanFieldListFilter),
    )
admin.site.register(MenuType,MenuTypeAdmin)

class MenuAdmin(admin.ModelAdmin):
    model = Menu
    list_display = ('__str__','parent','menu_slug','menu_icon','menuType','sequence_order','is_active')
    list_filter = (
        ('is_active', admin.BooleanFieldListFilter),
    )
admin.site.register(Menu,MenuAdmin)

class Menu_GroupAdmin(admin.ModelAdmin):
    model = Menu
    list_display = ('__str__','group','get_assigned_menu_name','is_active')
    list_filter = (
        ('is_active', admin.BooleanFieldListFilter),
    )
admin.site.register(Menu_Group,Menu_GroupAdmin)


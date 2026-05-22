from django.urls import path
from tenant import views

urlpatterns = [
    path("", views.tenant_list, name="tenant-list"),
    path("detail/<int:pk>/", views.tenant_detail, name="tenant-detail"),
    path("create/", views.tenant_create, name="tenant-create"),
    path("account/", views.tenant_settings_account, name="tenant-settings-account"),
    path("account/security/", views.tenant_settings_security, name="tenant-settings-security"),

    path("roles_permissions/", views.tenant_roles_permissions, name="tenant-roles-and-permissions"),
    path('RoleList/', views.RoleList, name='RoleList'),
    path('AddUpdateRoleFrom/<int:id>/', views.AddUpdateRoleFrom, name='AddUpdateRoleFrom'),
    path('AddUpdateRoleDataPost/', views.AddUpdateRoleDataPost, name='AddUpdateRoleDataPost'),
    path('CopyRole/', views.CopyRole, name='CopyRole'),

]

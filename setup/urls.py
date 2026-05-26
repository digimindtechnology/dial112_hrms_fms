from django.urls import path
from setup import views

urlpatterns = [
    path('data-setup', views.data_setup, name='setup-data-setup'),
    path('cost-centers/', views.cost_center_list, name='setup-cost-center-list'),
    path('cost-centers/add/', views.cost_center_add, name='setup-cost-center-add'),
    path('cost-centers/edit/<int:pk>/', views.cost_center_edit, name='setup-cost-center-edit'),
    path('cost-centers/delete/', views.cost_center_delete, name='setup-cost-center-delete'),
    path('cost-centers/bulk-upload/', views.cost_center_bulk_upload, name='setup-cost-center-bulk-upload'),
    path('cost-centers/download-sample/<str:fmt>/', views.cost_center_download_sample, name='setup-cost-center-download-sample'),
    path('cost-centers/upload-detail/<int:pk>/', views.cost_center_upload_detail, name='setup-cost-center-upload-detail'),
    path('cost-centers/download-errors/<int:pk>/', views.cost_center_download_errors, name='setup-cost-center-download-errors'),
    path('lookups/<str:slug>/', views.setup_lookup_list, name='setup-lookup-list'),
    path('lookups/<str:slug>/add/', views.setup_lookup_form, name='setup-lookup-add'),
    path('lookups/<str:slug>/edit/<int:pk>/', views.setup_lookup_form, name='setup-lookup-edit'),
    path('lookups/<str:slug>/delete/', views.setup_lookup_delete, name='setup-lookup-delete'),
    # Police Stations
    path('police-stations/', views.police_station_list, name='setup-police-station-list'),
    path('police-stations/add/', views.police_station_form, name='setup-police-station-add'),
    path('police-stations/edit/<int:pk>/', views.police_station_form, name='setup-police-station-edit'),
    path('police-stations/delete/', views.police_station_delete, name='setup-police-station-delete'),
    # Holidays
    path('holidays/', views.holiday_list, name='setup-holiday-list'),
    path('holidays/add/', views.holiday_form, name='setup-holiday-add'),
    path('holidays/edit/<int:pk>/', views.holiday_form, name='setup-holiday-edit'),
    path('holidays/delete/', views.holiday_delete, name='setup-holiday-delete'),
    path('holidays/<int:pk>/districts/', views.holiday_district_list, name='setup-holiday-district-list'),
    path('holidays/<int:pk>/districts/save/', views.holiday_district_save, name='setup-holiday-district-save'),
]

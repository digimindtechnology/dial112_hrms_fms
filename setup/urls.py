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

]

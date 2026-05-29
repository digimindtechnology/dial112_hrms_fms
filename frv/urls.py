from django.urls import path
from frv import views

urlpatterns = [
    path('', views.frvList, name='frv-list'),
    path('create/', views.frvCreate, name='frv-create'),
    path('detail/<uuid:frv_unique_id>/', views.frvDetail, name='frv-detail'), 
    path('edit/<uuid:frv_unique_id>/', views.frvEdit, name='frv-edit'),  # Add this
    path('delete/<uuid:frv_unique_id>/', views.frvDelete, name='frv-delete'),  # Add this
]

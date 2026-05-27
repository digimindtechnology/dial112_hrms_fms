from django.urls import path
from employee import views

urlpatterns = [
    path('', views.employee_list, name='employee-list'),
    path('add/', views.employee_add, name='employee-add'),
    path('edit/<str:emp_unique_id>/', views.employee_update, name='employee-edit'),
    path('delete/', views.employee_delete, name='employee-delete'),
]

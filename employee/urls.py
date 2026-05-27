from django.urls import path
from employee import views

urlpatterns = [
    path('', views.employee_list, name='employee-list'),
    path('add/', views.employee_add, name='employee-add'),
    path('<str:emp_unique_id>/detail/', views.employee_detail, name='employee-detail'),
    path('<str:emp_unique_id>/edit/', views.employee_update, name='employee-edit'),
    path('delete/', views.employee_delete, name='employee-delete'),

    # Education
    path('<str:emp_unique_id>/education/list/', views.education_list, name='education-list'),
    path('<str:emp_unique_id>/education/form/<int:pk>/', views.education_form, name='education-form'),
    path('<str:emp_unique_id>/education/save/', views.education_save, name='education-save'),
    path('education/delete/', views.education_delete, name='education-delete'),

    # Experience
    path('<str:emp_unique_id>/experience/list/', views.experience_list, name='experience-list'),
    path('<str:emp_unique_id>/experience/form/<int:pk>/', views.experience_form, name='experience-form'),
    path('<str:emp_unique_id>/experience/save/', views.experience_save, name='experience-save'),
    path('experience/delete/', views.experience_delete, name='experience-delete'),
]

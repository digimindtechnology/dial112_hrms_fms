from django.urls import path
from employee import views

urlpatterns = [
    path('', views.employee_list, name='employee-list'),
    path('list/partial/', views.employee_list_partial, name='employee-list-partial'),
    path('add/', views.employee_add, name='employee-add'),
    path('<str:emp_unique_id>/detail/', views.employee_detail, name='employee-detail'),
    path('<str:emp_unique_id>/view/', views.employee_view_profile, name='employee-view'),
    path('<str:emp_unique_id>/edit/', views.employee_update, name='employee-edit'),
    path('delete/', views.employee_delete, name='employee-delete'),

    # Education
    path('<str:emp_unique_id>/education/list/', views.education_list, name='education-list'),
    path('<str:emp_unique_id>/education/form/<int:pk>/', views.education_form, name='education-form'),
    path('<str:emp_unique_id>/education/save/', views.education_save, name='education-save'),
    path('education/delete/', views.education_delete, name='education-delete'),

    # Duplicate check
    path('check-duplicate/', views.employee_check_duplicate, name='employee-check-duplicate'),

    # Experience
    path('<str:emp_unique_id>/experience/list/', views.experience_list, name='experience-list'),
    path('<str:emp_unique_id>/experience/form/<int:pk>/', views.experience_form, name='experience-form'),
    path('<str:emp_unique_id>/experience/save/', views.experience_save, name='experience-save'),
    path('experience/delete/', views.experience_delete, name='experience-delete'),

    # Certification
    path('<str:emp_unique_id>/certification/list/', views.certification_list, name='certification-list'),
    path('<str:emp_unique_id>/certification/form/<int:pk>/', views.certification_form, name='certification-form'),
    path('<str:emp_unique_id>/certification/save/', views.certification_save, name='certification-save'),
    path('certification/delete/', views.certification_delete, name='certification-delete'),

    # Language
    path('<str:emp_unique_id>/language/list/', views.language_list, name='language-list'),
    path('<str:emp_unique_id>/language/form/<int:pk>/', views.language_form, name='language-form'),
    path('<str:emp_unique_id>/language/save/', views.language_save, name='language-save'),
    path('language/delete/', views.language_delete, name='language-delete'),

    # Family Detail
    path('<str:emp_unique_id>/family/list/', views.family_list, name='family-list'),
    path('<str:emp_unique_id>/family/form/<int:pk>/', views.family_form, name='family-form'),
    path('<str:emp_unique_id>/family/save/', views.family_save, name='family-save'),
    path('family/delete/', views.family_delete, name='family-delete'),

    # Job History
    path('<str:emp_unique_id>/job-history/list/', views.job_history_list, name='job-history-list'),
    path('<str:emp_unique_id>/job-history/form/<int:pk>/', views.job_history_form, name='job-history-form'),
    path('<str:emp_unique_id>/job-history/save/', views.job_history_save, name='job-history-save'),
    path('job-history/delete/', views.job_history_delete, name='job-history-delete'),

    # Document
    path('<str:emp_unique_id>/document/list/', views.document_list, name='document-list'),
    path('<str:emp_unique_id>/document/form/<int:pk>/', views.document_form, name='document-form'),
    path('<str:emp_unique_id>/document/save/', views.document_save, name='document-save'),
    path('document/delete/', views.document_delete, name='document-delete'),

    # Reporting Manager
    path('<str:emp_unique_id>/reporting-manager/list/', views.reporting_manager_list, name='reporting-manager-list'),
    path('<str:emp_unique_id>/reporting-manager/form/<int:pk>/', views.reporting_manager_form, name='reporting-manager-form'),
    path('<str:emp_unique_id>/reporting-manager/save/', views.reporting_manager_save, name='reporting-manager-save'),
    path('reporting-manager/delete/', views.reporting_manager_delete, name='reporting-manager-delete'),

    # Approval Action
    path('approval-action/', views.employee_approval_action, name='employee-approval-action'),

    # Profile Update Request
    path('profile-update-request/', views.profile_update_request_list, name='profile-update-request-list'),
    path('profile-update-request/list/partial/', views.profile_update_request_list_partial, name='profile-update-request-list-partial'),
    path('profile-update-request/form/<int:pk>/', views.profile_update_request_form, name='profile-update-request-form'),
    path('profile-update-request/save/', views.profile_update_request_save, name='profile-update-request-save'),
    path('profile-update-request/delete/', views.profile_update_request_delete, name='profile-update-request-delete'),
    path('profile-update-request/<int:pk>/detail/', views.profile_update_request_detail, name='profile-update-request-detail'),
    path('profile-update-request/<int:pk>/process/', views.profile_update_request_process, name='profile-update-request-process'),
    path('profile-update-request/<int:pk>/process/save/', views.profile_update_request_process_save, name='profile-update-request-process-save'),
    path('profile-update-request/<int:pk>/reject/', views.profile_update_request_reject, name='profile-update-request-reject'),
]

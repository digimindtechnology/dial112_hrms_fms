from django.urls import path
from approvalrules import views

urlpatterns = [

    path('list', views.ApprovalTypeList, name='approve-type-list'),
    path('create/', views.ApprovalTypeCreate, name='approve-type-create'),
    path('update/<int:pk>/', views.ApprovalTypeUpdate, name='approve-type-update'),

    path('create/<int:id>/',views.approveruleCreateView,name='approveruleCreate'),
    path('getUser/<int:role_id>/', views.GetUser, name='getUser'),
    path('detail/<int:ApprovId>/', views.ApproveTypeDetailView, name='approvedetail'),
    path('list-of-approval', views.listforapproval, name='listforapproval'),

]

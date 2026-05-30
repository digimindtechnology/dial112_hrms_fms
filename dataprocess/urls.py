from django.urls import path
from dataprocess import views

urlpatterns = [
    path('home/', views.home, name='data-process-home'),
   
]

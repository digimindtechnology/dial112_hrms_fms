from django.urls import path
from dashboard import views

urlpatterns = [
    path('home/', views.home, name='dashboard-home'),
    path('unauthorized/', views.not_authorized, name='unauthorized'),
]
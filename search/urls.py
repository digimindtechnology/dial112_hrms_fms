from django.urls import path
from search import views

urlpatterns = [
    path('global/', views.global_search, name='global-search'),
]

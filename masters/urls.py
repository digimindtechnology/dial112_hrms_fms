from django.urls import path
from masters import views

urlpatterns = [
    path('GetStateListJson/', views.GetStateListJson, name='GetStateListJson'),

    path('master-data', views.setup_master, name='master-data'),

    # Country
    path('CountryList/', views.CountryList, name='CountryList'),
    path('AddUpdateCountry/', views.AddUpdateCountry, name='AddUpdateCountry'),
    path('AddUpdateCountry/<int:pk>/', views.AddUpdateCountry, name='AddUpdateCountry'),
    path('DeleteCountry/', views.DeleteCountry, name='DeleteCountry'),

    # Currency
    path('CurrencyList/', views.CurrencyList, name='CurrencyList'),
    path('AddUpdateCurrency/', views.AddUpdateCurrency, name='AddUpdateCurrency'),
    path('AddUpdateCurrency/<int:pk>/', views.AddUpdateCurrency, name='AddUpdateCurrency'),
    path('DeleteCurrency/', views.DeleteCurrency, name='DeleteCurrency'),

    # State
    path('StateList/', views.StateList, name='StateList'),
    path('AddUpdateState/', views.AddUpdateState, name='AddUpdateState'),
    path('AddUpdateState/<int:pk>/', views.AddUpdateState, name='AddUpdateState'),
    path('DeleteState/', views.DeleteState, name='DeleteState'),

    # Division
    path('DivisionList/', views.DivisionList, name='DivisionList'),
    path('AddUpdateDivision/', views.AddUpdateDivision, name='AddUpdateDivision'),
    path('AddUpdateDivision/<int:pk>/', views.AddUpdateDivision, name='AddUpdateDivision'),
    path('DeleteDivision/', views.DeleteDivision, name='DeleteDivision'),

    # District
    path('DistrictList/', views.DistrictList, name='DistrictList'),
    path('AddUpdateDistrict/', views.AddUpdateDistrict, name='AddUpdateDistrict'),
    path('AddUpdateDistrict/<int:pk>/', views.AddUpdateDistrict, name='AddUpdateDistrict'),
    path('DeleteDistrict/', views.DeleteDistrict, name='DeleteDistrict'),

    # Zone
    path('ZoneList/', views.ZoneList, name='ZoneList'),
    path('AddUpdateZone/', views.AddUpdateZone, name='AddUpdateZone'),
    path('AddUpdateZone/<int:pk>/', views.AddUpdateZone, name='AddUpdateZone'),
    path('DeleteZone/', views.DeleteZone, name='DeleteZone'),

    # City
    path('CityList/', views.CityList, name='CityList'),
    path('AddUpdateCity/', views.AddUpdateCity, name='AddUpdateCity'),
    path('AddUpdateCity/<int:pk>/', views.AddUpdateCity, name='AddUpdateCity'),
    path('DeleteCity/', views.DeleteCity, name='DeleteCity'),

    # Time Zone
    path('TimeZoneList/', views.TimeZoneList, name='TimeZoneList'),
    path('AddUpdateTimeZone/', views.AddUpdateTimeZone, name='AddUpdateTimeZone'),
    path('AddUpdateTimeZone/<int:pk>/', views.AddUpdateTimeZone, name='AddUpdateTimeZone'),
    path('DeleteTimeZone/', views.DeleteTimeZone, name='DeleteTimeZone'),

    # Date Format
    path('DateFormatList/', views.DateFormatList, name='DateFormatList'),
    path('AddUpdateDateFormat/', views.AddUpdateDateFormat, name='AddUpdateDateFormat'),
    path('AddUpdateDateFormat/<int:pk>/', views.AddUpdateDateFormat, name='AddUpdateDateFormat'),
    path('DeleteDateFormat/', views.DeleteDateFormat, name='DeleteDateFormat'),

    # Time Format
    path('TimeFormatList/', views.TimeFormatList, name='TimeFormatList'),
    path('AddUpdateTimeFormat/', views.AddUpdateTimeFormat, name='AddUpdateTimeFormat'),
    path('AddUpdateTimeFormat/<int:pk>/', views.AddUpdateTimeFormat, name='AddUpdateTimeFormat'),
    path('DeleteTimeFormat/', views.DeleteTimeFormat, name='DeleteTimeFormat'),



    # Import / Export
    path('ExportCSV/<str:entity_name>/', views.ExportCSV, name='ExportCSV'),
    path('ExportExcel/<str:entity_name>/', views.ExportExcel, name='ExportExcel'),
    path('ImportData/<str:entity_name>/', views.ImportData, name='ImportData'),
]

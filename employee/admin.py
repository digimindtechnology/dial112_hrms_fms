from django.contrib import admin
from employee.models import EmployeeStatus, EmployeeRequestType, EmployeeCaste, EmployeeRecruitmentCategory, EmployeeInfo

admin.site.register(EmployeeCaste)
admin.site.register(EmployeeStatus)
admin.site.register(EmployeeRequestType)
admin.site.register(EmployeeRecruitmentCategory)
admin.site.register(EmployeeInfo)

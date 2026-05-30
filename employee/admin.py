from django.contrib import admin
from employee.models import EmployeeStatus, EmployeeRequestType, EmployeeCaste, EmployeeRecruitmentCategory, EmployeeInfo, EmployeeRequestStatus

admin.site.register(EmployeeCaste)
admin.site.register(EmployeeStatus)
admin.site.register(EmployeeRequestType)
admin.site.register(EmployeeRequestStatus)
admin.site.register(EmployeeRecruitmentCategory)
admin.site.register(EmployeeInfo)

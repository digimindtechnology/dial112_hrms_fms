from django.contrib import admin
from approvalrules.models import ApprovalType, ApproverStatus

admin.site.register(ApprovalType)
admin.site.register(ApproverStatus)


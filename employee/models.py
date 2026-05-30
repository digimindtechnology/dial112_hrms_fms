import uuid
from django.db import models
from accounts.models import Profile
from approvalrules.models import ApprovalType, ApproverStatus
from setup.models import EmployeeType, EmployeeCategory
from tenant.models import TenantProfile, Role
from django.contrib.auth.models import User
from masters.models import Gender, District, BaseModel


##Master Table
class EmployeeStatus(models.Model):
    employee_status_id = models.AutoField(primary_key=True)
    employee_status_name = models.CharField(max_length=200)
    employee_status_css = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('employee_status_id',)

    def __str__(self):
        return self.employee_status_name


class EmployeeRequestType(models.Model):
    employee_request_type_id = models.AutoField(primary_key=True)
    employee_request_type_name = models.CharField(max_length=200)
    employee_request_type_css = models.CharField(max_length=200, null=True, blank=True)
    employee_request_type_icon = models.CharField(max_length=200, null=True, blank=True)
    sequence = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('sequence',)

    def __str__(self):
        return self.employee_request_type_name


class EmployeeRequestStatus(models.Model):
    employee_request_status_id = models.AutoField(primary_key=True)
    employee_request_status_name = models.CharField(max_length=200)
    employee_request_status_css = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('employee_request_status_id',)

    def __str__(self):
        return self.employee_request_status_name


class EmployeeCaste(models.Model):
    employee_caste_id = models.AutoField(primary_key=True)
    employee_caste_name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('employee_caste_name',)

    def __str__(self):
        return self.employee_caste_name


class EmployeeRecruitmentCategory(models.Model):
    """Employee Recruitment Category (e.g., handcraft, Ex-Servicemen, etc.)"""
    recruitment_category_id = models.AutoField(primary_key=True)
    recruitment_category_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('recruitment_category_name',)


##Master Table


##Main Table
MARITAL_STATUS = [('Single', 'Single'), ('Married', 'Married'), ]
EMPLOYMENT_STATUS = [('Active', 'Active'), ('Inactive', 'Inactive'), ('Resigned', 'Resigned'), ('Terminated', 'Terminated'), ]
BLOOD_GROUPS = [('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ]


class EmployeeInfo(BaseModel):
    MARITAL_STATUS = MARITAL_STATUS
    EMPLOYMENT_STATUS = EMPLOYMENT_STATUS
    BLOOD_GROUPS = BLOOD_GROUPS
    employee_id = models.AutoField(primary_key=True)
    employee_unique_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    employee_code = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    mobile = models.CharField(max_length=20)

    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    picture = models.CharField(max_length=500, blank=True, null=True)  ##media/company_doc/1/employees/Emp_id/....

    father_name = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)

    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, blank=True)
    nationality = models.CharField(max_length=50, default='Indian')

    aadhaar_number = models.CharField(max_length=12, unique=True, blank=True, null=True)
    pan_number = models.CharField(max_length=10, unique=True, blank=True, null=True)
    profile_completion_percentage = models.IntegerField(default=0)
    passport_number = models.CharField(max_length=20, unique=True, blank=True, null=True)

    religion = models.CharField(max_length=100, blank=True)
    caste = models.ForeignKey(EmployeeCaste, related_name='caste_EmployeeInfo', null=True, blank=True, on_delete=models.CASCADE)
    empType = models.ForeignKey(EmployeeType, related_name='empType_EmployeeInfo', null=True, blank=True, on_delete=models.CASCADE)
    empCategory = models.ForeignKey(EmployeeCategory, related_name='empCategory_EmployeeInfo', null=True, blank=True, on_delete=models.CASCADE)
    empStatus = models.ForeignKey(EmployeeStatus, related_name='empStatus_EmployeeInfo', default=1, on_delete=models.CASCADE)

    district = models.ForeignKey(District, related_name='district_EmployeeInfo', null=True, blank=True, on_delete=models.CASCADE)
    city = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    current_address = models.TextField(null=True, blank=True)
    permanent_address = models.TextField(null=True, blank=True)

    department = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100)
    joining_date = models.DateField()

    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default='Active')
    work_location = models.CharField(max_length=100, blank=True)

    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    bank_name = models.CharField(max_length=100, blank=True)
    bank_address = models.CharField(max_length=500, blank=True)
    bank_account_number = models.CharField(max_length=30, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)

    is_gratuity = models.BooleanField(default=False)
    is_eligible_for_pf = models.BooleanField(default=False)
    pf_number = models.CharField(max_length=20, blank=True)

    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name="user_EmployeeInfo")
    empRole = models.ForeignKey(Role, default=20, on_delete=models.CASCADE, related_name="empRole_EmployeeInfo")  ##Employee Role ID=20
    userProfile = models.ForeignKey(Profile, blank=True, null=True, on_delete=models.CASCADE, related_name="userProfile_EmployeeInfo")

    tenantProfile = models.ForeignKey(TenantProfile, blank=True, null=True, related_name='tenantProfile_EmployeeInfo', on_delete=models.CASCADE, verbose_name="Tenant")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_EmployeeInfo")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="updated_by_EmployeeInfo")
    is_profile_lock = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class EmployeeFamilyDetail(models.Model):
    RELATION_CHOICES = [('Father', 'Father'), ('Mother', 'Mother'), ('Spouse', 'Spouse'), ('Son', 'Son'),
                        ('Daughter', 'Daughter'), ('Brother', 'Brother'), ('Sister', 'Sister'), ('Other', 'Other'), ]
    employee_family_detail_id = models.AutoField(primary_key=True, help_text="Unique family detail ID")
    employee = models.ForeignKey(EmployeeInfo, on_delete=models.CASCADE, related_name='family_details', help_text="Related employee")
    family_member_name = models.CharField(max_length=150, help_text="Family member full name")
    relationship = models.CharField(max_length=50, choices=RELATION_CHOICES, help_text="Relationship with employee")
    date_of_birth = models.DateField(null=True, blank=True, help_text="Family member date of birth")
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, null=True, blank=True, help_text="Family member gender")
    mobile_number = models.CharField(max_length=20, null=True, blank=True, help_text="Family member mobile number")
    occupation = models.CharField(max_length=100, blank=True, help_text="Family member occupation")
    aadhaar_number = models.CharField(max_length=12, blank=True, null=True, help_text="Family member Aadhaar number")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_EmployeeFamilyDetail', help_text="Created by user")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_by_EmployeeFamilyDetail', null=True, blank=True, help_text="Last updated by user")
    is_emergency_contact = models.BooleanField(default=False)

    class Meta:
        ordering = ('family_member_name',)
        verbose_name = "Employee Family Detail"
        verbose_name_plural = "Employee Family Details"

    def __str__(self):
        return f"{self.employee.full_name} - {self.family_member_name}"


class EmployeeEducation(BaseModel):
    employee_education_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(EmployeeInfo, on_delete=models.CASCADE, related_name='educations')
    qualification = models.CharField(max_length=500)
    institution_name = models.CharField(max_length=200)
    board_university = models.CharField(max_length=200)
    passing_year = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    certificate_file = models.CharField(max_length=500, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_EmployeeEducation', help_text="Created by user")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_by_EmployeeEducation', null=True, blank=True, help_text="Last updated by user")

    def __str__(self):
        return f"{self.employee.first_name} - {self.qualification}"


class EmployeeCertification(BaseModel):
    employee_certification_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(EmployeeInfo, on_delete=models.CASCADE, related_name='certifications')
    certification_name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    certificate_file = models.CharField(max_length=500, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_EmployeeCertification', help_text="Created by user")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_by_EmployeeCertification', null=True, blank=True, help_text="Last updated by user")

    def __str__(self):
        return f"{self.employee.first_name} - {self.certification_name}"


class EmployeeExperience(BaseModel):
    employee_experience_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(EmployeeInfo, on_delete=models.CASCADE, related_name='experiences')
    organization_name = models.CharField(max_length=500)
    department = models.CharField(max_length=250)
    designation = models.CharField(max_length=250)
    start_date = models.DateField()
    end_date = models.DateField()
    last_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reason_for_leaving = models.TextField(blank=True)
    reference_name = models.CharField(max_length=250, blank=True)
    reference_contact = models.CharField(max_length=20, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_EmployeeExperience', help_text="Created by user")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_by_EmployeeExperience', null=True, blank=True, help_text="Last updated by user")

    def __str__(self):
        return f"{self.employee.first_name} - {self.organization_name}"


class EmployeeLanguage(BaseModel):
    employee_language_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(EmployeeInfo, on_delete=models.CASCADE, related_name='languages')
    language_name = models.CharField(max_length=100)
    can_read = models.BooleanField(default=False)
    can_write = models.BooleanField(default=False)
    can_speak = models.BooleanField(default=False)
    is_mother_tongue = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_EmployeeLanguage', help_text="Created by user")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_by_EmployeeLanguage', null=True, blank=True, help_text="Last updated by user")

    def __str__(self):
        return f"{self.employee.first_name} - {self.language_name}"


class EmployeeJobHistory(BaseModel):
    employee_job_history_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(EmployeeInfo, on_delete=models.CASCADE, related_name='job_history')
    grade = models.CharField(max_length=100, blank=True)
    post = models.CharField(max_length=100)
    joining_date = models.DateField()
    probation_end_date = models.DateField(null=True, blank=True)
    confirmation_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_EmployeeJobHistory', help_text="Created by user")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_by_EmployeeJobHistory', null=True, blank=True, help_text="Last updated by user")

    def __str__(self):
        return f"{self.employee.first_name} - {self.grade}"


class EmployeeDocument(BaseModel):
    employee_document_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(EmployeeInfo, on_delete=models.CASCADE, related_name='employee_documents')
    document_name = models.CharField(max_length=500)
    file_doc = models.CharField(max_length=500, blank=True, null=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_EmployeeDocument', help_text="Created by user")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_by_EmployeeDocument', null=True, blank=True, help_text="Last updated by user")

    def __str__(self):
        return f"{self.employee.first_name} - {self.document_name}"


class EmployeeReportingManager(BaseModel):
    employee_reporting_manager_id = models.AutoField(primary_key=True, help_text="Unique reporting manager record ID")
    employee = models.ForeignKey(EmployeeInfo, on_delete=models.CASCADE, related_name='employee_reporting_managers', help_text="Employee assigned to reporting manager")
    reporting_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='manager_reporting_employees', help_text="Reporting manager employee")
    is_current = models.BooleanField(default=True, help_text="Whether this is the current reporting manager")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_EmployeeReportingManager', help_text="Created by user")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_by_EmployeeReportingManager', null=True, blank=True, help_text="Last updated by user")

    class Meta:
        ordering = ('employee_reporting_manager_id',)
        verbose_name = "Employee Reporting Manager"
        verbose_name_plural = "Employee Reporting Managers"

    def __str__(self):
        return f"{self.employee.first_name} -> {self.reporting_manager.last_name}"


class EmployeeAuditLog(BaseModel):
    employee_audit_log_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(EmployeeInfo, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_EmployeeAuditLog', help_text="Created by user")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_by_EmployeeAuditLog', null=True, blank=True, help_text="Last updated by user")

    def __str__(self):
        return f"{self.employee.first_name} - {self.field_name}"


class EmployeeDataApprover(BaseModel):
    employee_data_approver_id = models.AutoField(primary_key=True)
    sequence = models.IntegerField(default=0)
    approverType = models.ForeignKey(ApprovalType, related_name="approverType_EmployeeDataApprover", on_delete=models.CASCADE)
    employee = models.ForeignKey(EmployeeInfo, on_delete=models.CASCADE, related_name='employee_EmployeeDataApprover', help_text="employee")

    approved_date = models.DateField(null=True, blank=True)
    approved_remark = models.TextField(null=True, blank=True)

    rejected_date = models.DateField(null=True, blank=True)
    rejected_remark = models.TextField(null=True, blank=True)

    approver = models.ForeignKey(User, related_name="user_EmployeeDataApprover", on_delete=models.CASCADE, help_text="user-approver by")
    approver_role = models.ForeignKey(Role, related_name="role_EmployeeDataApprover", null=True, blank=True, on_delete=models.CASCADE, help_text="role of approver by")

    approverStatus = models.ForeignKey(ApproverStatus, default=1, related_name="approverStatus_EmployeeDataApprover", on_delete=models.CASCADE, help_text="approver status")

    tenantProfile = models.ForeignKey(TenantProfile, related_name="tenantProfile_EmployeeDataApprover", on_delete=models.CASCADE, verbose_name="Tenant")
    created_by = models.ForeignKey(User, related_name="created_EmployeeDataApprover", on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, related_name="updated_EmployeeDataApprover", null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ("sequence",)

    def __str__(self):
        return self.approver.get_full_name() or self.approver.username


class EmployeeProfileUpdateRequest(BaseModel):
    employee_profile_update_id = models.AutoField(primary_key=True)
    employee_profile_update_unique_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    change_request_description = models.TextField()
    employee = models.ForeignKey(EmployeeInfo, on_delete=models.CASCADE, related_name='employee_EmployeeProfileUpdateRequest', help_text="employee")
    empRequestStatus = models.ForeignKey(EmployeeRequestStatus, default=1, related_name="empRequestStatus_EmployeeProfileUpdateRequest", on_delete=models.CASCADE)
    approved_rejected_date = models.DateField(null=True, blank=True)
    approved_rejected_remark = models.TextField(null=True, blank=True)
    approved_rejected_created_by = models.ForeignKey(User,null=True, blank=True, related_name="approved_rejected_created_by_EmployeeProfileUpdateRequest", on_delete=models.CASCADE)
    is_send_to_approval = models.BooleanField(default=False)

    tenantProfile = models.ForeignKey(TenantProfile, related_name="tenantProfile_EmployeeProfileUpdateRequest", on_delete=models.CASCADE, verbose_name="Tenant")
    created_by = models.ForeignKey(User, related_name="created_EmployeeProfileUpdateRequest", on_delete=models.CASCADE)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class EmployeeActivityLog(BaseModel):
    employee_activity_log_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(EmployeeInfo, related_name='employee_EmployeeActivityLog', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name="created_by_EmployeeActivityLog")

    class Meta:
        ordering = ('employee_activity_log_id',)

    def __str__(self):
        return str(self.employee_activity_log_id)


##Main Table


class TempSelfRegEmployee(BaseModel):
    MARITAL_STATUS = MARITAL_STATUS
    EMPLOYMENT_STATUS = EMPLOYMENT_STATUS
    BLOOD_GROUPS = BLOOD_GROUPS

    temp_self_reg_employee_id = models.AutoField(primary_key=True)
    temp_self_reg_employee_unique_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    employee_code = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    mobile = models.CharField(max_length=20)

    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    picture = models.CharField(max_length=500, blank=True, null=True)  ##media/company_doc/1/temp_employees/....

    father_name = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)

    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, blank=True)
    nationality = models.CharField(max_length=50, default='Indian')

    aadhaar_number = models.CharField(max_length=12, unique=True, blank=True, null=True)
    pan_number = models.CharField(max_length=10, unique=True, blank=True, null=True)
    passport_number = models.CharField(max_length=20, unique=True, blank=True, null=True)

    religion = models.CharField(max_length=100, blank=True)
    caste = models.ForeignKey(EmployeeCaste, related_name='caste_TempSelfRegEmployee', null=True, blank=True, on_delete=models.CASCADE)
    empType = models.ForeignKey(EmployeeType, related_name='empType_TempSelfRegEmployee', null=True, blank=True, on_delete=models.CASCADE)

    district = models.ForeignKey(District, related_name='district_TempSelfRegEmployee', null=True, blank=True, on_delete=models.CASCADE)
    city = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    current_address = models.TextField(null=True, blank=True)
    permanent_address = models.TextField(null=True, blank=True)

    department = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100)
    joining_date = models.DateField()

    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default='Active')
    work_location = models.CharField(max_length=100, blank=True)

    bank_name = models.CharField(max_length=100, blank=True)
    bank_address = models.CharField(max_length=500, blank=True)
    bank_account_number = models.CharField(max_length=30, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)

    is_gratuity = models.BooleanField(default=False)
    is_eligible_for_pf = models.BooleanField(default=False)
    pf_number = models.CharField(max_length=20, blank=True)

    employeeInfo = models.ForeignKey(EmployeeInfo, blank=True, null=True, on_delete=models.SET_NULL, related_name="employeeInfo_TempSelfRegEmployee")
    created_by_name = models.CharField(max_length=50, default='Self')

    def __str__(self):
        return f"{self.temp_self_reg_employee_id} - {self.first_name} {self.last_name}"

from enum import Enum
from django.db import models
from datetime import datetime
import re
import os

import random
from django.utils.ipv6 import is_valid_ipv6_address
from django.core.exceptions import ValidationError
import ipaddress
from rest_framework.pagination import PageNumberPagination


def django_enum(cls):
    # decorator needed to enable enums in django templates
    cls.do_not_call_in_templates = True
    return cls


class Base(models.Model):
    @django_enum
    class RegExConst(Enum):
        stringPattern = r"^\S.*\S$"
        emailPattern = r"^[\w\.-]+@([\w-]+\.)+[A-Za-z]{2,5}$"
        mobileIndianPattern = r"^(\+91[- ]?)?[6-9]\d{9}$"  # +91-9822345654, 9822345654
        GSTPattern = r"^([0][1-9]|[1-2][0-9]|3[0-7])[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]$"
        PANPattern = r"^[A-Z]{5}\d{4}[A-Z]$"
        URLPattern = r"^(https?:\/\/)?([\w-]+\.)+[\w-]{2,5}(:\d{1,5})?(\/.*)?$"
        PostalCodePattern = r"^[1-9]\d{5}$"
        NumbersAnddecimalOnly = r"^\d+(\.\d{1,2})?$"
        NumbersAnddecimalOnly3Dec = r"^\d+(\.\d{1,3})?$"
        AadharNumber = r"^\d{12}$"
        LoginID = r"^[A-Za-z0-9_-]{4,20}$"
        Password = r"^.{4,12}$"
        CharacterAndSpaceOnly = r"^[A-Za-z ]*$"
        CharactersAndParanthisisOnly = r"^[A-Za-z ()'.-]+$"
        CharactersParanthisisAndSpecialCharOnly = r"^[A-Za-z() ]*$"
        CharactersAndCommaOnly = r"^[A-Za-z, ]{2,}$"
        CharactersOnly = r"^[A-Za-z]*$"
        General = r"^[ A-Za-z0-9_@./,#&+\-]{1,500}$"
        NumbersOnly = r"^[0-9+\-]+$"
        NumbersAndOneDecimalOnly = r"^\d+(\.\d{1,2})?$"
        NumbersWithPlusOnly = r"^[0-9+]+$"
        NumbersWithPlusAndSpaceOnly = r"^[0-9+ ]+$"
        AlphaNumericOnly = r"^[A-Za-z0-9]*$"
        AlphaNumericAndSpaceOnly = r"^[A-Za-z0-9 ]*$"
        IntegerGreaterthanZero = r"^[1-9]\d*$"
        DecimalGreaterthanZero = r"^(?=.*[1-9])\d*(\.\d{1,2})?$"
        EmailAddress = r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$"
        Decimal = r"^\d*(\.\d+)?$"

    @django_enum
    class Group(Enum):
        HomeGroup = "Home"
        TenantGroup = "Tenant"
        EmployeeGroup = "Employee"
        LeaveSetupGroup = "LeaveSetup"
        ShiftRosterGroup = 'ShiftRosterManagement'
        LeaveManagementGroup = "LeaveManagement"
        AttendanceManagementGroup = 'AttendanceManagement'
        TrainingManagementGroup = 'TrainingManagement'
        ViolationGroup = 'Violation'
        FRVManagementGroup = "FRVManagement"
        FRVGuidelineGroup = "FRVGuideline"
        FRVServiceCenterGroup = "FRVServiceCenter"
        SelfRegistrationRecordsGroup = "SelfRegistrationRecords"

        TicketGroup = "Ticket"
        HelpdeskGroup = "Helpdesk"
        SetupGroup = "Setup"
        UserGroup = "User"
        ReportGroup = "Report"
        LogoutGroup = "Logout"

    @django_enum
    class ApprovalRules(Enum):
        EmployeeApproval = "Employee Approval Rule"


def GenerateOTP():
    return random.randint(1000, 9999)


def GeneratePassword():
    return random.randint(100000, 999999)


def WriteLog(filePath, text):
    f = open(filePath, "a")
    f.write(text)
    f.close()


def GetPageList(CurrentPage, num_pages):
    start = max(1, CurrentPage - 3)
    end = min(num_pages, CurrentPage + 3)
    return list(range(start, end + 1))


def company_doc_path(instance, filename):
    return os.path.join('company_doc/', str(instance.company.id), filename)


def company_user_doc_path(instance, filename):
    return os.path.join('company_doc/' + str(instance.company.id) + '/', 'user/', filename)


class OnePageSetPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 1000


def validate_ipv4_address(value):
    try:
        ipaddress.IPv4Address(value)
    except ValueError:
        raise ValidationError('Enter a valid IPv4 address.')


def validate_ipv6_address(value):
    if not is_valid_ipv6_address(value):
        raise ValidationError('Enter a valid IPv6 address.')


def validate_ipv46_address(value):
    try:
        validate_ipv4_address(value)
    except ValidationError:
        try:
            validate_ipv6_address(value)
        except ValidationError:
            raise ValidationError('Enter a valid IP address.')


def GetUniqCode(txt):
    now = datetime.now()
    showtime = datetime.now().strftime("%d%m%Y%f")
    return showtime


def GSTValidate(value):
    # reg = re.compile( str(Base.RegExConst.GSTPattern))
    reg = re.compile(
        "^([0][1-9]|[1-2][0-9]|[3][0-7])([a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9a-zA-Z]{1}[zZ]{1}[0-9a-zA-Z]{1})+$")
    if not reg.match(value):
        raise ValidationError('Invalid GST Number "' + value + "'")


def PANValidate(value):
    # reg = re.compile( str(Base.RegExConst.GSTPattern))
    reg = re.compile("^([a-zA-Z]){5}([0-9]){4}([a-zA-Z]){1}?$")
    if not reg.match(value):
        raise ValidationError('Invalid PAN Number "' + value + "'")

# DIAL-112 HRMS & FMS — Back Office (Django)

Procurement back-office portal built on **Django 6.0.5** with Materio Bootstrap 5 theme. PostgreSQL backend, S3 file storage, SMS-based OTP authentication, role-based access control, and full CRUD with import/export.

---

## Quick Start

```bash
py -m pip install -r requirements.txt   # install deps
py manage.py runserver                  # start dev server
```

**.env** controls all configuration — see `.env` for DB, SMS, S3, email settings.

---

## Django Apps

| App | Purpose |
|-----|---------|
| `accounts/` | Auth 
| `masters/` | Master data: Country, State, District, Currency, etc. |
| `tenant/` | Company/tenant management, roles, timezone/date-format settings |
| `setup/` | CRUD + import/export for all master entities |
| `user/` | User CRUD, import/export, password management |
| `dashboard/` | Home page, not-authorized fallback |


---

## Key Functions (DO NOT RE-WRITE)

> **Do not make any changes to these functions without permission (SS).**

### decorators — `accounts/decorators.py`

| Decorator | Usage |
|-----------|-------|
| `@SuperUser_only` | Superuser only |
| `@Admin_only` | Admin role only |
| `@Manager_only` | Manager role only |
| `@Operator_only` | Operator role only |
| `@role_required('Admin','Manager')` | Any of listed roles |
| `@CheckRole('Admin','Manager')` | Role via auth Group membership (with SweetAlert error) |

### middleware — `accounts/middlewares.py`

`RoleMiddleware` sets these on every request:
- `request.role`, `request.roleID`, `request.tenantID`, `request.tenantName`
- `request.tenantLogo`, `request.tenantFavicon`
- `request.title` (breadcrumb/page title)
- `request.usertoken` (DRF Token)


### SMS / Email — `accounts/sms_helper.py`

**SMS**

```python
send_otp_sms(mobile, otp, username)  # Sends formatted OTP via SMS_API
send_sms(numbers, message)            # Low-level SMS send via API URL template
```

Uses `SMS_API` URL template (replaces `MOBILE_NUMBERS`, `SMS_MESSAGE`) and `DIGIMIND_OTP` message template (replaces `_USERNAME_`, `_OTP_`).

**Email**

All three functions return `True` on success, `False` on failure, and respect the `EMAIL_SERVICE_ON` kill-switch.  
`to` and `bcc` each accept a single address (str) or a list of addresses.

---

**1. Plain-text email**

```python
from accounts.helpers.sms_helper import send_email

send_email(
    to='user@example.com',  # or ['a@x.com', 'b@x.com']
    subject='Your account is ready',
    message='Hello, your account has been created.',
    bcc='audit@example.com',  # optional
)
```

Signature: `send_email(to, subject, message, from_email=None, bcc=None)`

---

**2. Plain-text email with attachment**

```python
from accounts.helpers.sms_helper import send_email_with_attachment

# From a file path
send_email_with_attachment(
    to='user@example.com',
    subject='Monthly Report',
    message='Please find the attached report.',
    attachment='/path/to/report.pdf',  # auto-detects filename & MIME type
    bcc='archive@example.com',  # optional
)

# From an in-memory file (BytesIO, InMemoryUploadedFile, …)
send_email_with_attachment(
    to='user@example.com',
    subject='Invoice',
    message='Your invoice is attached.',
    attachment=invoice_bytes_io,
    filename='invoice.xlsx',
    mime_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
)
```

Signature: `send_email_with_attachment(to, subject, message, attachment, filename=None, mime_type=None, from_email=None, bcc=None)`  
`filename` and `mime_type` are auto-derived from the path/object when omitted.

---

**3. HTML template email**

```python
from accounts.helpers.sms_helper import send_html_email

send_html_email(
    to='user@example.com',
    subject='Welcome to Procure10X',
    template_name='emails/base_email.html',
    context={
        'subject': 'Welcome to Procure10X',
        'preview_text': 'Your account is ready!',
        'greeting': 'Hello, John',
        'message': 'Your account has been created successfully.',
        'action_url': 'https://app.procure10x.com/login/',
        'action_text': 'Log In Now',
        'company_name': 'Procure10X',
    },
    text_message='Your account is ready. Visit https://app.procure10x.com/login/',
    bcc='audit@example.com',  # optional
)
```

Signature: `send_html_email(to, subject, template_name, context, text_message=None, from_email=None, bcc=None)`  
`text_message` is a plain-text fallback shown by clients that don't render HTML.

---

**Base email template** — `templates/emails/base_email.html`

Generic, email-client-safe template with inline CSS. Context keys:

| Key | Required | Description |
|-----|:--------:|-------------|
| `message` | ✓ | Main body paragraph |
| `subject` | — | Used in `<title>` |
| `greeting` | — | Bold greeting line, e.g. `"Hello, John"` |
| `extra_content` | — | Highlighted info block (left-bordered) |
| `action_url` + `action_text` | — | CTA button (both required together) |
| `preview_text` | — | Inbox preview snippet (hidden in body) |
| `company_name` | — | Defaults to `"Procure10X"` |
| `logo_url` | — | Header image; falls back to text company name |
| `footer_text` | — | Replaces default "sent by …" footer line |
| `unsubscribe_url` | — | Adds unsubscribe link in footer |

---

**`.env` keys**

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your@email.com
EMAIL_SERVICE_ON=True   # set False to disable all outbound email globally
```

### alerts —

```python
send_sweetalert(request, 'error', 'Your message here')  # Shows SweetAlert toast
```

Types: `'success'`, `'error'`, `'warning'`, `'info'`.

### base utilities — `accounts/base.py`

| Function | Returns |
|----------|---------|
| `GenerateOTP()` | Random 1000-9999 (int) |
| `GeneratePassword()` | Random 100000-999999 (int) |
| `WriteLog(text)` | None (appends to file) |
| `GetPageList(total, page, step)` | Pagination range list |
| `GSTValidate(gst)` | Bool |
| `PANValidate(pan)` | Bool |

### file handling — `ProcureBOApp/basicUtility.py`

| Function | Signature | Purpose |
|----------|-----------|---------|
| `GetFileUrl` | `(file_path)` | Resolve S3 or local URL from stored path |
| `UploadFileS3Server` | `(tenantId, directory, uploadFile, fileName='')` | Upload to S3; falls back to local on failure |
| `UploadFileLocalSystem` | `(tenantId, directory, uploadFile, fileName='')` | Upload to local `media/` |
| `UploadFileS3ServerProjectDirectory` | `(tenantId, directory, uploadFile, fileName='')` | Alias for `UploadFileS3Server` |
| `DownloadS3DocFile` | `(request)` | Stream S3 file download (POST: `file` key) |
| `GetFileNameFromS3Url` | `(fileUrl)` | Extract filename from an S3 URL |
| `DeleteFileFromS3` | `(key)` | Delete file from S3 bucket by key |

**`S3DirectoryManager`** (class, static methods):

| Method | Signature | Purpose |
|--------|-----------|---------|
| `create` | `(directory_name)` | Create an S3 "folder" |
| `rename` | `(old_directory, new_directory)` | Copy all objects to new prefix, delete old |
| `delete` | `(directory_name)` | Delete all objects under a prefix |

### import/export — `ProcureBOApp/import_export_utils.py`

| Function | Signature | Purpose |
|----------|-----------|---------|
| `export_csv` | `(queryset, field_names, header_map, filename)` | CSV download response |
| `export_xlsx` | `(queryset, field_names, header_map, filename)` | XLSX download response |
| `parse_upload` | `(file, fmt)` | Parse uploaded CSV/XLSX → list of dicts |

- `field_names` — ordered list of field names, e.g. `['name', 'tenant__name']`
- `header_map` — `{'field_name': 'Column Header'}` display labels
- `fmt` — `'csv'` or `'xlsx'`
- `__` in field names traverses FK relations via `getattr`

### template context — `accounts/context_processors.py`

Available in all templates:
- `{{ S3_URL }}`, `{{ LOGIN_URL }}`
- `{{ menu_list }}`, `{{ menu_list_child }}`
- `{{ RegExConst }}`, `{{ Group }}` (enums from `Base`)

### template filters — `accounts/templatetags/ui_filter_tags.py`

**Filters** (`{% load ui_filter_tags %}` required):

| Filter | Usage | Returns |
|--------|-------|---------|
| `dyn_date` | `{{ val\|dyn_date:request.date_format_value }}` | Date formatted as per user's date setting |
| `dyn_time` | `{{ val\|dyn_time:request.time_format_value }}` | Time formatted as per user's time setting |
| `file_url` | `{{ val\|file_url }}` | Resolve stored path to full S3 or media URL |
| `FormatDateYYYYMMDD` | `{{ val\|FormatDateYYYYMMDD }}` | Date as `YYYY-MM-DD` |
| `FormatDateDDMMYYYY` | `{{ val\|FormatDateDDMMYYYY }}` | Date as `DD-MM-YYYY` (legacy — prefer `dyn_date`) |
| `FormatDateYYYYMMDDHHMM` | `{{ val\|FormatDateYYYYMMDDHHMM }}` | Datetime as `YYYY-MM-DD HH:MM` (+5:30 offset) |
| `FormatTimeHHMM` | `{{ val\|FormatTimeHHMM }}` | Time as `HH:MM hrs` |
| `multipleVal` | `{{ val\|multipleVal:arg }}` | `val * arg` |
| `addVal` | `{{ val\|addVal:arg }}` | `val + arg` |
| `ConvertToDateTime` | `{{ val\|ConvertToDateTime }}` | Parse ISO string → `datetime` object |
| `GetRoleWiseUserList` | `{{ tenantId\|GetRoleWiseUserList:roleId }}` | Renders user avatar group HTML for a role |

**Simple tags**:

| Tag | Usage | Returns |
|-----|-------|---------|
| `GetTenantName` | `{% GetTenantName tenantId %}` | Tenant name string |
| `CurrentTime` | `{% CurrentTime "%H:%M" %}` | Current server time in given strftime format |

### error handling — `accounts/error_utils.py`

```python
handle_exception(request, exception)  # Logs error context to session, redirects back
```


## Layout Template Blocks

`templates/layout/layout_base.html`:

```
{% block title %}             — Page title
{% block content %}           — Main page content
{% block vendor_css %}        — Extra CSS libs
{% block vendor_js %}         — Extra JS libs (deferred)
{% block page_js %}           — Page-specific JS (deferred)
```




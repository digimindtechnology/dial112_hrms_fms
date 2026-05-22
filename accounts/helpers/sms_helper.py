import os
import logging
import mimetypes
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


# ─── SMS ──────────────────────────────────────────────────────────────────────

def send_sms(mobile_numbers, message):
    if not settings.SMS_API:
        return False
    url = settings.SMS_API.replace('MOBILE_NUMBERS', str(mobile_numbers))
    url = url.replace('SMS_MESSAGE', urllib.parse.quote(message))
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        logger.error(f"[SMS] Failed to send: {e}")
        return False


def send_otp_sms(mobile_numbers, otp, username='User'):
    if not settings.DIGIMIND_OTP:
        logger.warning("[SMS] DIGIMIND_OTP template not configured")
        return False
    message = settings.DIGIMIND_OTP.replace('_USERNAME_', username)
    message = message.replace('_OTP_', str(otp))
    return send_sms(mobile_numbers, message)


# ─── Email ─────────────────────────────────────────────────────────────────────

def _to_list(to):
    """Normalize recipient(s) to a list."""
    if not to:
        return []
    return [to] if isinstance(to, str) else list(to)


def send_email(to, subject, message, from_email=None, bcc=None):
    """Send a plain-text email.

    Args:
        to          : str or list of recipient email addresses.
        subject     : Email subject line.
        message     : Plain-text body.
        from_email  : Sender address. Defaults to DEFAULT_FROM_EMAIL.
        bcc         : str or list of BCC addresses. Optional.

    Returns:
        True on success, False on failure.

    Usage:
        send_email(
            to='user@example.com',
            subject='Welcome to Procure10X',
            message='Hello, your account has been created.',
            bcc='admin@example.com',
        )
    """
    if not getattr(settings, 'EMAIL_SERVICE_ON', True):
        logger.warning("[Email] EMAIL_SERVICE_ON is disabled. Email not sent.")
        return False
    try:
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            to=_to_list(to),
            bcc=_to_list(bcc),
        )
        email.send()
        logger.info(f"[Email] Plain email sent to {to!r} — subject: {subject!r}")
        return True
    except Exception as e:
        logger.error(f"[Email] send_email failed: {e}")
        return False


def send_email_with_attachment(to, subject, message, attachment, filename=None, mime_type=None, from_email=None, bcc=None):
    """Send a plain-text email with a single file attachment.

    Args:
        to          : str or list of recipient email addresses.
        subject     : Email subject line.
        message     : Plain-text body.
        attachment  : File path (str) OR binary file-like object.
        filename    : Attachment display name. Auto-derived from path when omitted.
        mime_type   : MIME type string. Auto-detected when omitted.
        from_email  : Sender address. Defaults to DEFAULT_FROM_EMAIL.
        bcc         : str or list of BCC addresses. Optional.

    Returns:
        True on success, False on failure.

    Usage — from a file path:
        send_email_with_attachment(
            to='user@example.com',
            subject='Monthly Report',
            message='Please find the attached report.',
            attachment='/path/to/report.pdf',
            bcc='archive@example.com',
        )

    Usage — from an in-memory file (e.g. Django uploaded file or BytesIO):
        send_email_with_attachment(
            to='user@example.com',
            subject='Invoice',
            message='Your invoice is attached.',
            attachment=invoice_bytes_io,
            filename='invoice.xlsx',
            mime_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
    """
    if not getattr(settings, 'EMAIL_SERVICE_ON', True):
        logger.warning("[Email] EMAIL_SERVICE_ON is disabled. Email not sent.")
        return False
    try:
        if isinstance(attachment, str):
            attach_filename = filename or os.path.basename(attachment)
            guessed, _ = mimetypes.guess_type(attachment)
            attach_mime = mime_type or guessed or 'application/octet-stream'
            with open(attachment, 'rb') as f:
                attach_content = f.read()
        else:
            attach_filename = filename or getattr(attachment, 'name', 'attachment')
            guessed, _ = mimetypes.guess_type(attach_filename)
            attach_mime = mime_type or guessed or 'application/octet-stream'
            attach_content = attachment.read()

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            to=_to_list(to),
            bcc=_to_list(bcc),
        )
        email.attach(attach_filename, attach_content, attach_mime)
        email.send()
        logger.info(f"[Email] Attachment email sent to {to!r} — subject: {subject!r}, file: {attach_filename!r}")
        return True
    except Exception as e:
        logger.error(f"[Email] send_email_with_attachment failed: {e}")
        return False


def send_html_email(to, subject, template_name, context, text_message=None, from_email=None, bcc=None):
    """Send an HTML email rendered from a Django template.

    Args:
        to            : str or list of recipient email addresses.
        subject       : Email subject line.
        template_name : Django template path, e.g. 'emails/base_email.html'.
        context       : dict passed to the template renderer.
        text_message  : Optional plain-text fallback. Shown by clients that
                        do not support HTML.
        from_email    : Sender address. Defaults to DEFAULT_FROM_EMAIL.
        bcc           : str or list of BCC addresses. Optional.

    Returns:
        True on success, False on failure.

    Usage:
        send_html_email(
            to='user@example.com',
            subject='Your account is ready',
            template_name='emails/base_email.html',
            context={
                'subject': 'Your account is ready',
                'preview_text': 'Welcome to Procure10X!',
                'greeting': 'Hello, John',
                'message': 'Your account has been created successfully.',
                'action_url': 'https://app.procure10x.com/login/',
                'action_text': 'Log In Now',
                'company_name': 'Procure10X',
            },
            text_message='Your account has been created. Visit https://app.procure10x.com/login/',
            bcc='audit@example.com',
        )
    """
    if not getattr(settings, 'EMAIL_SERVICE_ON', True):
        logger.warning("[Email] EMAIL_SERVICE_ON is disabled. Email not sent.")
        return False
    try:
        html_content = render_to_string(template_name, context)
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message or '',
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            to=_to_list(to),
            bcc=_to_list(bcc),
        )
        email.attach_alternative(html_content, 'text/html')
        email.send()
        logger.info(f"[Email] HTML email sent to {to!r} — subject: {subject!r}, template: {template_name!r}")
        return True
    except Exception as e:
        logger.error(f"[Email] send_html_email failed: {e}")
        return False

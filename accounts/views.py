import io
import base64
import random
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFont

from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.clickjacking import xframe_options_deny
from django.views.decorators.http import require_POST

from DmtHrmsFmsApp.settings import LOGIN_URL, SMS_SERVICE_ON
from accounts.helpers.message_helper import send_sweetalert
from accounts.helpers.sms_helper import send_otp_sms
from accounts.models import Profile, UserLoginTrace
from accounts.base import GenerateOTP


def generate_captcha_text(length=5):
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(random.choices(chars, k=length))


def generate_captcha_image(text):
    width, height = 100, 50

    image = Image.new('RGB', (width, height), (248, 249, 250))
    draw = ImageDraw.Draw(image)

    # noise dots
    for _ in range(random.randint(100, 200)):
        draw.point(
            (random.randint(0, width - 1), random.randint(0, height - 1)),
            fill=(
                random.randint(150, 220),
                random.randint(150, 220),
                random.randint(150, 220)
            )
        )

    # noise lines
    for _ in range(random.randint(3, 6)):
        draw.line(
            [
                (random.randint(0, width), random.randint(0, height)),
                (random.randint(0, width), random.randint(0, height))
            ],
            fill=(
                random.randint(100, 200),
                random.randint(100, 200),
                random.randint(100, 200)
            ),
            width=1
        )

    # font 20px
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    # center text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) / 2
    y = (height - text_height) / 2

    draw.text((x, y), text, fill=(20, 40, 80), font=font)

    draw.rectangle([0, 0, width - 1, height - 1], outline=(200, 200, 200), width=1)

    buffer = io.BytesIO()
    image.save(buffer, format='PNG')

    return base64.b64encode(buffer.getvalue()).decode()


class LoginForm(forms.Form):
    username = forms.CharField(max_length=80, min_length=5, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter your user id'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
        required=True)
    captcha = forms.CharField(max_length=10, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter the code shown above', 'id': 'captchaInput',
               'autocomplete': 'off'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_captcha(self):
        captcha_input = self.cleaned_data.get('captcha', '')
        expected = self.request.session.get('captcha_text', '') if self.request else ''
        if not expected:
            raise forms.ValidationError('CAPTCHA session expired. Please refresh and try again.')
        if captcha_input.upper().strip() != expected:
            raise forms.ValidationError('Invalid CAPTCHA. Please try again.')
        del self.request.session['captcha_text']
        return captcha_input


@never_cache
def get_captcha(request):
    captcha_text = generate_captcha_text()
    request.session['captcha_text'] = captcha_text
    return JsonResponse({
        'captcha_image': 'data:image/png;base64,' + generate_captcha_image(captcha_text)
    })


@never_cache
@xframe_options_deny
def custom_login(request):
    context = {}
    if request.method == "POST":
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if not user.is_active:
                    msg = (
                        'Your account has been locked due to multiple invalid login attempts. Please contact the IT Department.')
                    send_sweetalert(request, 'error', msg)
                else:
                    profile = Profile.objects.filter(user=user).first()
                    if profile and profile.is_login_with_otp and SMS_SERVICE_ON:
                        otp = str(GenerateOTP())
                        profile.user_otp = otp
                        profile.user_otp_expire_date = timezone.now() + timedelta(minutes=1)
                        profile.total_resend_otp = 0
                        profile.total_wrong_otp = 0
                        profile.save(
                            update_fields=['user_otp', 'user_otp_expire_date', 'total_resend_otp', 'total_wrong_otp'])
                        request.session['otp_user_id'] = user.id
                        if profile.mobile:
                            send_otp_sms(profile.mobile, otp, user.get_full_name() or user.username)
                        else:
                            print(f"[OTP] No mobile for {user.username}, OTP: {otp}")
                        send_sweetalert(request, 'info', 'OTP sent to your registered mobile number.')
                        return HttpResponseRedirect(reverse('otp-verify'))
                    login(request, user)
                    AddUserLoginTrace(request, user)
                    storage = messages.get_messages(request)
                    storage.used = True
                    UserLoginTrace.objects.create(user=user, )
                    send_sweetalert(request, 'success', "login successfully")
                    return HttpResponseRedirect(reverse(LOGIN_URL))
            else:
                msg = ('Invalid login credentials. Accounts are locked after 3 failed password attempts!')
                send_sweetalert(request, 'error', msg)

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    send_sweetalert(request, 'error', f"{field}: {error}")

        context['form'] = form
    else:
        context['form'] = LoginForm(request=request)
    return render(request, 'account/login.html', context)


def logout(request):
    try:
        context = {}
        from django.contrib.auth import logout
        logout(request)
        send_sweetalert(request, 'success', f"logout successfully")
        return render(request, 'account/logout.html', context)
    except Exception as e:
        print(e)
        send_sweetalert(request, 'error', str(e))
        return render(request, 'account/login.html')


def mask_mobile(mobile):
    if not mobile or len(mobile) < 4:
        return mobile
    return mobile[:2] + '*' * (len(mobile) - 4) + mobile[-2:]


@never_cache
def otp_verify(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        return HttpResponseRedirect(reverse('login'))

    profile = get_object_or_404(Profile, user_id=user_id)
    remaining_seconds = 0
    if profile.user_otp_expire_date:
        remaining_seconds = max(0, int((profile.user_otp_expire_date - timezone.now()).total_seconds()))

    if request.method == 'POST':
        otp_entered = request.POST.get('otp', '').strip()
        if not otp_entered:
            send_sweetalert(request, 'error', 'Please enter the OTP.')
        elif profile.user_otp is None or timezone.now() > profile.user_otp_expire_date:
            send_sweetalert(request, 'error', 'OTP has expired. Please request a new one.')
        elif otp_entered != profile.user_otp:
            profile.total_wrong_otp += 1
            profile.save(update_fields=['total_wrong_otp'])
            send_sweetalert(request, 'error', 'Invalid OTP. Please try again.')
        else:
            profile.user_otp = None
            profile.user_otp_expire_date = None
            profile.total_wrong_otp = 0
            profile.save(update_fields=['user_otp', 'user_otp_expire_date', 'total_wrong_otp'])
            user = profile.user
            login(request, user)
            AddUserLoginTrace(request, user)
            request.session.pop('otp_user_id', None)
            storage = messages.get_messages(request)
            storage.used = True
            send_sweetalert(request, 'success', 'Login successful.')
            return HttpResponseRedirect(reverse('dashboard-home'))

    return render(request, 'account/otp_verify.html', {
        'masked_mobile': mask_mobile(profile.mobile),
        'remaining_seconds': remaining_seconds,
    })


@require_POST
@never_cache
def otp_resend(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': 'Session expired.'}, status=400)

    profile = get_object_or_404(Profile, user_id=user_id)
    otp = str(GenerateOTP())
    profile.user_otp = otp
    profile.user_otp_expire_date = timezone.now() + timedelta(minutes=1)
    profile.total_resend_otp += 1
    profile.save(update_fields=['user_otp', 'user_otp_expire_date', 'total_resend_otp'])
    if profile.mobile:
        send_otp_sms(profile.mobile, otp, profile.user.get_full_name() or profile.user.username)
    else:
        print(f"[OTP] No mobile for {profile.user.username}, resent OTP: {otp}")
    return JsonResponse({'success': True, 'message': 'OTP resent successfully.'})


def AddUserLoginTrace(request, user):
    UserLoginTrace.objects.create(user=user, type='LOGIN', created_date=timezone.now(),
                                  ip_or_mac=request.META.get('REMOTE_ADDR'),
                                  browser_os_info=request.META.get('HTTP_USER_AGENT'),
                                  message='User logged in')


@never_cache
def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        if not username:
            send_sweetalert(request, 'error', 'Please enter your Login ID / Username.')
            return render(request, 'account/forgot_password.html')
        try:
            user = User.objects.get(username=username, is_active=True)
        except User.DoesNotExist:
            send_sweetalert(request, 'error', 'No account found with this Login ID.')
            return render(request, 'account/forgot_password.html')

        profile = Profile.objects.filter(user=user).first()
        if not profile or not profile.mobile:
            send_sweetalert(request, 'error', 'No registered mobile number found. Contact IT Department.')
            return render(request, 'account/forgot_password.html')

        otp = str(GenerateOTP())
        profile.user_otp = otp
        profile.user_otp_expire_date = timezone.now() + timedelta(minutes=1)
        profile.total_resend_otp = 0
        profile.total_wrong_otp = 0
        profile.save(update_fields=['user_otp', 'user_otp_expire_date', 'total_resend_otp', 'total_wrong_otp'])
        request.session['forgot_user_id'] = user.id
        send_otp_sms(profile.mobile, otp, user.get_full_name() or user.username)
        send_sweetalert(request, 'info', 'OTP sent to your registered mobile number.')
        return HttpResponseRedirect(reverse('forgot-password-verify'))

    return render(request, 'account/forgot_password.html')


@never_cache
def forgot_password_verify(request):
    user_id = request.session.get('forgot_user_id')
    if not user_id:
        return HttpResponseRedirect(reverse('forgot-password'))

    profile = get_object_or_404(Profile, user_id=user_id)
    remaining_seconds = 0
    if profile.user_otp_expire_date:
        remaining_seconds = max(0, int((profile.user_otp_expire_date - timezone.now()).total_seconds()))

    if request.method == 'POST':
        otp_entered = request.POST.get('otp', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not otp_entered:
            send_sweetalert(request, 'error', 'Please enter the OTP.')
        elif profile.user_otp is None or timezone.now() > profile.user_otp_expire_date:
            send_sweetalert(request, 'error', 'OTP has expired. Please request a new one.')
        elif otp_entered != profile.user_otp:
            profile.total_wrong_otp += 1
            profile.save(update_fields=['total_wrong_otp'])
            send_sweetalert(request, 'error', 'Invalid OTP. Please try again.')
        elif not new_password or len(new_password) < 6:
            send_sweetalert(request, 'error', 'Password must be at least 6 characters.')
        elif new_password != confirm_password:
            send_sweetalert(request, 'error', 'New Password and Confirm Password do not match.')
        else:
            user = profile.user
            user.set_password(new_password)
            user.save(update_fields=['password'])
            profile.user_otp = None
            profile.user_otp_expire_date = None
            profile.total_wrong_otp = 0
            profile.save(update_fields=['user_otp', 'user_otp_expire_date', 'total_wrong_otp'])
            request.session.pop('forgot_user_id', None)
            send_sweetalert(request, 'success', 'Password reset successfully. Please login with your new password.')
            return HttpResponseRedirect(reverse('login'))

    return render(request, 'account/forgot_password_verify.html', {
        'masked_mobile': mask_mobile(profile.mobile),
        'remaining_seconds': remaining_seconds,
    })


@require_POST
@never_cache
def forgot_password_resend(request):
    user_id = request.session.get('forgot_user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': 'Session expired.'}, status=400)

    profile = get_object_or_404(Profile, user_id=user_id)
    otp = str(GenerateOTP())
    profile.user_otp = otp
    profile.user_otp_expire_date = timezone.now() + timedelta(minutes=1)
    profile.total_resend_otp += 1
    profile.save(update_fields=['user_otp', 'user_otp_expire_date', 'total_resend_otp'])
    if profile.mobile:
        send_otp_sms(profile.mobile, otp, profile.user.get_full_name() or profile.user.username)
    else:
        print(f"[OTP] No mobile for {profile.user.username}, resent OTP: {otp}")
    return JsonResponse({'success': True, 'message': 'OTP resent successfully.'})

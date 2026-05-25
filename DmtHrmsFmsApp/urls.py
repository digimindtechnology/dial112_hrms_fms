from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.custom_login, name='login'),
    path('login/', AccountViews.custom_login, name='login'),
    path('get-captcha/', AccountViews.get_captcha, name='get-captcha'),
    path('login/otp/', AccountViews.otp_verify, name='otp-verify'),
    path('login/otp/resend/', AccountViews.otp_resend, name='otp-resend'),
    path('forgot-password/', AccountViews.forgot_password, name='forgot-password'),
    path('forgot-password/verify/', AccountViews.forgot_password_verify, name='forgot-password-verify'),
    path('forgot-password/resend/', AccountViews.forgot_password_resend, name='forgot-password-resend'),
    path('logout/', AccountViews.logout, name='logout'),
    path("auto-logout/", AccountViews.logout, name="auto_logout"),

    path('admin/', admin.site.urls),
    path('masters/', include('masters.urls')),
    path('setup/', include('setup.urls')),
    path('user/', include('user.urls')),
    path('tenant/', include('tenant.urls')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('search/', include('search.urls')),

    path('attendance/', include('attendance.urls')),
    path('employee/', include('employee.urls')),
    path('ticket/', include('ticket.urls')),
    path('training/', include('training.urls')),
    path('f-r-v/', include('frv.urls')),
    path('approval-rules/', include('approvalrules.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

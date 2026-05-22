from django.contrib import admin
from accounts.models import Profile, UserLoginTrace


admin.site.register(Profile)
admin.site.register(UserLoginTrace)

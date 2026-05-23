from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse
from accounts.helpers.message_helper import send_sweetalert

def role_required(*allowed_roles):
    """General role-based access decorator"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            role = getattr(request, 'role', None)
            if role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseRedirect(reverse('login'))
        return wrapper
    return decorator


# Specific role decorators (short & readable)
SuperUser_only = role_required("SuperUser")
Admin_only = role_required("Admin")
Manager_only = role_required("Manager")
Operator_only = role_required("Operator")


def CheckRole(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                user_roles = {g.name for g in request.user.groups.all()}
                if not any(r in user_roles for r in roles):
                    module = getattr(request, 'module', 'this page')
                    send_sweetalert(request, 'error', f"You don't have permission to access {module}")
                    return HttpResponseRedirect(reverse('unauthorized'))

                # Login error handling
                if getattr(request, 'loginErrorMessage', ''):
                    send_sweetalert(request, 'error', request.loginErrorMessage)
                    return HttpResponseRedirect(reverse('login'))

                return view_func(request, *args, **kwargs)

            except Exception as e:
                print(f"CheckRole Exception: {e}")
                send_sweetalert(request, 'error', str(e))
                if getattr(request.user, 'is_authenticated', False):
                    return HttpResponseRedirect(reverse('unauthorized'))
                return HttpResponseRedirect(reverse('login'))

        return wrapper
    return decorator


# class APIAccessAssetsGroup(BasePermission):
#     def has_permission(self, request, view):
#         user_token = request.headers.get('Authorization').replace("token ", "").replace("Token ", "")
#         userToken = Token.objects.get(key=user_token).user
#         for g in userToken.groups.all():
#             if g.name == Base.Group.AssetsGroup.value:
#                 return True
#         return False

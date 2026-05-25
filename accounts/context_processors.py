from django.db import connection
from django.core.cache import cache
from DmtHrmsFmsApp.settings import S3_URL, LOGIN_URL, IS_RunServer, AUTO_LOGOUT
from accounts.helpers.base import Base


def BaseEnum(request):
    bm = {'RegExConst': Base.RegExConst, 'Group': Base.Group}
    return bm


def menu_list(request):
    if not request.user.is_authenticated:
        return {"S3_URL": S3_URL, "LOGIN_URL": LOGIN_URL, "IS_RunServer": IS_RunServer, "AUTO_LOGOUT": AUTO_LOGOUT,
                "menu_list": [], "menu_list_child": []}
    with connection.cursor() as cur:
        cur.callproc('fun_GetMenuListByUser', (request.user.id, 0,))
        parent_menus = list(cur.fetchall())
        cur.callproc('fun_GetMenuListByUser', (request.user.id, 1,))
        child_menus = list(cur.fetchall())
    return {"S3_URL": S3_URL, "LOGIN_URL": LOGIN_URL, "IS_RunServer": IS_RunServer, "AUTO_LOGOUT": AUTO_LOGOUT,
            "menu_list": parent_menus, "menu_list_child": child_menus}

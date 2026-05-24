from django.db import connection
from django.core.cache import cache
from DmtHrmsFmsApp.settings import S3_URL, LOGIN_URL, IS_RunServer, AUTO_LOGOUT
from accounts.helpers.base import Base


def BaseEnum(request):
    bm = {'RegExConst': Base.RegExConst, 'Group': Base.Group}
    return bm


def db_GetMenuListByUser(userid, p_id):
    with connection.cursor() as cur:
        cur.callproc('fun_GetMenuListByUser', (userid, p_id,))
        return cur.fetchall()


def menu_list(request):
    if not request.user.is_authenticated:
        return {"S3_URL": S3_URL, "LOGIN_URL": LOGIN_URL, "IS_RunServer": IS_RunServer, "AUTO_LOGOUT": AUTO_LOGOUT,
                "menu_list": [], "menu_list_child": []}
    menu_list = list(db_GetMenuListByUser(request.user.id, 0))
    menu_list_child = list(db_GetMenuListByUser(request.user.id, 1))
    return {"S3_URL": S3_URL, "LOGIN_URL": LOGIN_URL, "IS_RunServer": IS_RunServer, "AUTO_LOGOUT": AUTO_LOGOUT,
            "menu_list": menu_list, "menu_list_child": menu_list_child}

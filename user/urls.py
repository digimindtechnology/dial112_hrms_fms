from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import users_view, UserListJson, ExportUsersCSV, ExportUsersExcel, ImportUsers, user_create, user_detail

urlpatterns = [
    path("list/", login_required(users_view), name="user-list", ),
    path("list/json/", login_required(UserListJson), name="user-list-json"),

    path("create/", login_required(user_create), name="user-create-form"),
    path("<int:user_id>/update/", login_required(user_create), name="user-update-form"),
    path("<int:user_id>/detail/", login_required(user_detail), name="user-detail"),

    # Import / Export
    path("export/csv/", login_required(ExportUsersCSV), name="ExportUsersCSV"),
    path("export/excel/", login_required(ExportUsersExcel), name="ExportUsersExcel"),
    path("import/", login_required(ImportUsers), name="ImportUsers"),
]

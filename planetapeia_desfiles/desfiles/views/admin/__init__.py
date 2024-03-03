from django.urls import path

from .roles_view import RolesView

paths = [
    path("adm/roles", RolesView.as_view(), name="admin_roles"),
]

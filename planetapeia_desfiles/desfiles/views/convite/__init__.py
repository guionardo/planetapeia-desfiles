from django.urls import path, re_path

from .convite import ConviteView
from .convite_chave import ConviteChaveView

paths = [
    path("convite", ConviteView.as_view(), name="convite_vazio"),
    path("convite/chave", ConviteChaveView.as_view(), name="convite_chave"),
    re_path(r"^convite/(?P<hash>[0-9A-F]{8})/$", ConviteView.as_view(), name="convite"),
]

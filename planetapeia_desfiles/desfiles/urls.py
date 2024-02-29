from django.urls import path, re_path

from .views.auth import LoginView, logoff
from .views.cadastro import CadastroPessoaView
from .views.convidado.convites import MeusConvites
from .views.convite import ConviteView
from .views.convite_chave import ConviteChaveView
from .views.home import HomeView
from .views.index import Index
from .views.perfil import (
    PerfilAlterarSenhaView,
    PerfilEditarView,
    PerfilFotoView,
    PerfilRevisarSenha,
    PerfilView,
)

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("home", HomeView.as_view(), name="home"),
    path("login", LoginView.as_view(), name="login"),
    path("logoff", logoff, name="logoff"),
    path("perfil", PerfilView.as_view(), name="perfil"),
    path("perfil/editar", PerfilEditarView.as_view(), name="perfil_editar"),
    path("perfil/senha", PerfilAlterarSenhaView.as_view(), name="perfil_senha"),
    path("perfil/foto", PerfilFotoView.as_view(), name="perfil_foto"),
    re_path(
        r"^perfil/revisar_senha/(?P<cpf>[0-9]{11})/$",
        PerfilRevisarSenha.as_view(),
        name="perfil_revisar_senha",
    ),
    path("perfil/convites", MeusConvites.as_view(), name="perfil_convites"),
    path("convite", ConviteView.as_view(), name="convite_vazio"),
    path("convite/chave", ConviteChaveView.as_view(), name="convite_chave"),
    re_path(r"^convite/(?P<hash>[0-9A-F]{8})/$", ConviteView.as_view(), name="convite"),
    path("cadastro/pessoa", CadastroPessoaView.as_view(), name="cadastro_pessoa"),
]

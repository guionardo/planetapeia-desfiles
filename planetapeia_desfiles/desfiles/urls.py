from django.urls import path

from .views.auth import LoginView, logoff
from .views.cadastro import CadastroPessoaView
from .views.convite import ConviteView
from .views.home import HomeView
from .views.index import Index
from .views.perfil import PerfilAlterarSenhaView, PerfilView

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("home", HomeView.as_view(), name="home"),
    path("login", LoginView.as_view(), name="login"),
    path("logoff", logoff, name="logoff"),
    path("perfil", PerfilView.as_view(), name="perfil"),
    path("perfil/senha", PerfilAlterarSenhaView.as_view(), name="perfil_senha"),
    path("convite", ConviteView.as_view(), name="convite_vazio"),
    path("convite/<str:hash>", ConviteView.as_view(), name="convite"),
    path("cadastro/pessoa", CadastroPessoaView.as_view(), name="cadastro_pessoa"),
]

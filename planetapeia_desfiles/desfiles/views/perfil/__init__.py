from django.urls import path, re_path

from .cadastro import CadastroPessoaView
from .perfil_alterar_senha_view import AlterarSenhaView
from .perfil_editar_view import EditarView
from .perfil_foto_view import FotoView
from .perfil_meus_convites import MeusConvitesView
from .perfil_revisar_senha_view import RevisarSenha
from .perfil_view import PerfilView

paths = [
    path("perfil", PerfilView.as_view(), name="perfil"),
    path("perfil/editar", EditarView.as_view(), name="perfil_editar"),
    path("perfil/senha", AlterarSenhaView.as_view(), name="perfil_senha"),
    path("perfil/foto", FotoView.as_view(), name="perfil_foto"),
    re_path(
        r"^perfil/revisar_senha/(?P<cpf>[0-9]{11})/$",
        RevisarSenha.as_view(),
        name="perfil_revisar_senha",
    ),
    path("perfil/convites", MeusConvitesView.as_view(), name="perfil_convites"),
    path("perfil/cadastro", CadastroPessoaView.as_view(), name="cadastro_pessoa"),
]

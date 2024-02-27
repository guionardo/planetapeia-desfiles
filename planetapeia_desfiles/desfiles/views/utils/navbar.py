from dataclasses import dataclass, field

from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.templatetags.static import static
from django.urls import reverse

from ...services.user_messages import UserMessageLevelChoices, UserMessages


@dataclass
class Link:
    label: str
    to: str = field(default="")
    disabled: bool = field(default=False)
    active: bool = field(default=False)
    title: str = ""

    @property
    def divider(self) -> bool:
        return self.label.startswith("-")

    def __post_init__(self):
        if self.to and not self.to.startswith("http"):
            self.to = reverse(self.to)


class NavBar:
    def __init__(self, request: HttpRequest):
        self.user: User = request.user
        self.pessoa = request.pessoa
        self.localizacao = str(request.location)
        self.userlinks = self.get_userlinks()
        self.is_logged = self.pessoa and self.user.is_active
        self.user_messages = list(UserMessages(request).get_unreadmessages())
        self.user_messages_badge_color = "bg-info"
        self.user_messages_badge_icon = "bi-envelope"
        for msg in self.user_messages:
            match msg.level:
                case UserMessageLevelChoices.ERROR:
                    self.user_messages_badge_color = "bg-danger"
                    self.user_messages_badge_icon = "bi-envelope-exclamation-fill"
                    messages.warning(request, "Você tem mensagens de erro não lidas")
                    break
                case UserMessageLevelChoices.WARN:
                    self.user_messages_badge_color = "bg-warning"
                    self.user_messages_badge_icon = "bi-envelope-fill"
                    messages.warning(request, "Você tem mensagens de alerta não lidas")
                    break

    @property
    def get_foto(self):
        if self.pessoa:
            return self.pessoa.get_foto()
        if self.user.is_active:
            return static("icon_admin.svg")

    @property
    def get_name(self):
        if self.pessoa:
            return self.pessoa.nome
        if self.user.is_active:
            return self.user.get_full_name() or self.user.get_username()
        return "anônimo"

    def get_userlinks(self) -> list[Link]:
        if not self.user.is_active:
            return []
        links = []
        links.extend(
            [
                Link(self.get_name, disabled=True),
                Link("-"),
                Link("Home", "home"),
                Link("Perfil", "perfil"),
                Link(
                    "Foto",
                    "perfil_foto",
                    title="Alterar foto",
                ),
                Link(
                    "Alterar senha",
                    "admin:password_change" if self.user.is_staff else "perfil_senha",
                ),
            ]
        )
        if self.user.is_staff:
            links.extend([Link("-"), Link("Administração", "admin:index")])

        links.extend(
            [
                Link(
                    f"Localização: {self.localizacao}",
                    disabled=True,
                    title="Localização ",
                ),
                Link("-"),
                Link("Logoff", "logoff"),
            ]
        )

        return links

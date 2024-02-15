from dataclasses import dataclass, field

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.templatetags.static import static
from django.urls import reverse

from ...models import Pessoa


@dataclass
class Link:
    label: str
    to: str = field(default="")
    disabled: bool = field(default=False)
    active: bool = field(default=False)

    @property
    def divider(self) -> bool:
        return self.label.startswith("-")

    def __post_init__(self):
        if self.to and not self.to.startswith("http"):
            self.to = reverse(self.to)


class NavBar:
    def __init__(self, request: HttpRequest):
        self.user: User = request.user
        self.pessoa = self.get_pessoa(request)
        self.userlinks = self.get_userlinks()

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

    @classmethod
    def get_pessoa(cls, request: HttpRequest) -> Pessoa | None:
        if pessoa := Pessoa.objects.filter(cpf=request.user.username).first():
            return pessoa

    def get_userlinks(self) -> list[Link]:
        return [
            Link(self.get_name, disabled=True),
            Link("-"),
            Link("Painel", "home"),
            Link("Perfil", "perfil"),
            Link("-"),
            Link("Logoff", "logoff"),
        ]


# <li><a class="dropdown-item disabled" href="#" aria-current="page">{{ pessoa.nome }}</a></li>
#                     <li>
#                         <hr class="dropdown-divider">
#                     </li>
#                     <li><a class="dropdown-item" href="{% url 'perfil' %}">Perfil</a></li>
#                     <li><a class="dropdown-item" href="#">Customers</a></li>
#                     <li><a class="dropdown-item" href="#">Products</a></li>
#                     <li>
#                         <hr class="dropdown-divider">
#                     </li>
#                     <li><a class="dropdown-item" href="#">Reports</a></li>
#                     <li><a class="dropdown-item" href="#">Analytics</a></li>

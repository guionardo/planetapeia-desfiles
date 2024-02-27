from django.http import HttpRequest
from django.urls import reverse

from ...services.user_messages import UserMessages
from .decorators import just_admin
from .home_card import HomeCard


@just_admin
def get_revisoes_senha(request: HttpRequest):
    if revisoes := len(list(UserMessages(request).get_revisoes_senha())):
        return HomeCard(
            "Revisões de senha",
            links=[
                (
                    "Revisar",
                    reverse("admin:desfiles_pessoarevisarsenha_changelist")
                    + "?atendida_por__isempty=1",
                )
            ],
            text=f"{revisoes} {'pendência' if revisoes==1 else 'pendências'}",
        )

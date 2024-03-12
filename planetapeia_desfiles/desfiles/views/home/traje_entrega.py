from django.http import HttpRequest
from django.urls import reverse

from ...roles import ALMOXARIFE
from .home_card import HomeCard


def get_traje_entrega(request: HttpRequest):
    if request.user.has_perm(ALMOXARIFE):
        return HomeCard(
            "Entrega de traje",
            text="Entregar traje ao convidado para o desfile",
            links=[("Acessar", reverse("trajes_entrega"))],
        )

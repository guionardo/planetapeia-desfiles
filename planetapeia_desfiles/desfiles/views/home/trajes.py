from django.http import HttpRequest
from django.urls import reverse

from ...roles import ALMOXARIFE
from .home_card import HomeCard


def get_trajes(request: HttpRequest):
    if request.user.has_perm(ALMOXARIFE):
        return HomeCard(
            "Gestão de Trajes",
            text="Movimentação de trajes (entrada, entrega, devolução, manutenção, etc)",
            links=[("Acessar", reverse("trajes_index"))],
        )

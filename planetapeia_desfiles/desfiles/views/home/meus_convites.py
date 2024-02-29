from datetime import date

from django.http import HttpRequest
from django.urls import reverse

from ...models import InscricaoDesfile
from .home_card import HomeCard


def get_meus_convites(request: HttpRequest):
    if InscricaoDesfile.objects.filter(
        pessoa=request.pessoa, desfile__data__gte=date.today()
    ).all():
        return HomeCard(
            "Convites",
            text="Seus convites para desfilar no Planetapéia",
            links=[("Acessar", reverse("perfil_convites"))],
        )

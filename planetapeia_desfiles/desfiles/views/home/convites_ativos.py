from datetime import date

from django.http import HttpRequest

from ...models import Convite, Pessoa
from .home_card import HomeCard


def get_convites_ativos(request: HttpRequest) -> HomeCard:
    try:
        pessoa = Pessoa.objects.get(pk=request.user.username)
        convites = Convite.objects.filter(
            grupo=pessoa.grupo, desfile_data__gte=date.today()
        )
        text = f"Convites ativos para o grupo {pessoa.grupo}"
    except Pessoa.DoesNotExist:
        convites = Convite.objects.filter(desfile__data__gte=date.today())
        text = "Todos os convites ativos"

    links = []
    for convite in convites:
        links.append((f"{convite.desfile} [{convite.grupo}]", "http://localhost"))

    return HomeCard("Convites ativos", links=links, text=text)

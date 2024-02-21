from datetime import date

from django.http import HttpRequest
from django.urls import reverse
from ...models import Convite, Pessoa
from .home_card import HomeCard
from .decorators import just_admin


@just_admin
def get_convites_ativos(request: HttpRequest) -> HomeCard:
    try:
        pessoa = Pessoa.objects.get(pk=request.user.username)
        convites = Convite.objects.filter(
            grupo=pessoa.grupo, desfile__data__gte=date.today()
        )
        text = f"Convites ativos para o grupo {pessoa.grupo}"
    except Pessoa.DoesNotExist:
        convites = Convite.objects.filter(desfile__data__gte=date.today())
        text = "Todos os convites ativos"

    links = []
    for convite in convites:
        # links.append((f"{convite.desfile} [{convite.grupo}]", "http://localhost"))
        links.append(
            (
                f"{convite.desfile} [{convite.grupo}]",
                reverse("admin:desfiles_inscricaodesfile_changelist")
                + f"?aprovacao__exact=A&grupo__id__exact={convite.grupo.id}",
            )  # &
        )

    return HomeCard("Convites aprovados", links=links, text=text)

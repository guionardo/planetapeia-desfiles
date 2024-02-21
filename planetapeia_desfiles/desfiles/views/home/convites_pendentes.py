from datetime import date

from django.http import HttpRequest
from django.urls import reverse

from ...models import AprovacaoChoices, Convite, InscricaoDesfile, Pessoa
from .home_card import HomeCard

from .decorators import just_admin


@just_admin
def get_convites_pendentes(request: HttpRequest) -> HomeCard:
    try:
        pessoa = Pessoa.objects.get(pk=request.user.username)
        convites = Convite.objects.filter(
            grupo=pessoa.grupo, desfile__data__gte=date.today()
        )
    except Pessoa.DoesNotExist:
        convites = Convite.objects.filter(desfile__data__gte=date.today())
    convites_pendentes = []
    links = []
    for convite in convites:
        if pendentes := InscricaoDesfile.objects.filter(
            convite=convite, aprovacao=AprovacaoChoices.PENDENTE
        ).count():
            convites_pendentes.append(
                ([f"{convite.desfile} [{convite.grupo}]"], pendentes)
            )
            links.append(
                (
                    f"{convite.desfile} [{convite.grupo}]",
                    reverse("admin:desfiles_inscricaodesfile_changelist")
                    + f"?aprovacao__exact=P&grupo__id__exact={convite.grupo.id}",
                    pendentes,
                )  # &
            )

    return HomeCard(
        "Convites pendentes", badged_list_items=convites_pendentes, links=links
    )

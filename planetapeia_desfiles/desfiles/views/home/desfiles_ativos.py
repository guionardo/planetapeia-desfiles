from datetime import date, timedelta

from django.http import HttpRequest
from django.urls import reverse

from ...models import Desfile
from .home_card import HomeCard


def get_desfiles_ativos(request: HttpRequest) -> HomeCard:
    desde = date.today() - timedelta(days=30)
    desfiles = [str(desfile) for desfile in Desfile.objects.filter(data__gte=desde)]

    return HomeCard(
        "Desfiles",
        list_items=desfiles,
        links=[("Administração", reverse("admin:desfiles_desfile_changelist"))],
        text=f"Desfiles a partir de {desde:%d/%m/%Y}",
    )

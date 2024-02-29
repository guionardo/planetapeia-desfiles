from datetime import date

from django.contrib import messages
from django.forms import ValidationError
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from ...models import Convite
from ..utils import NavBar


class ConviteChaveView(TemplateView):
    template_name = "convite/convite_chave.html"

    def _get_convite(self, hash: str) -> Convite:
        if convite := Convite.objects.filter(hash=hash).first():
            if convite.valido_ate < date.today():
                raise ValidationError("Este convite não é mais válido")
            if convite.convidados_confirmados >= convite.max_convidados:
                raise ValidationError(
                    f"O limite de {convite.max_convidados} pessoas para este convite já foi atingido"
                )
            return convite
        else:
            raise Convite.DoesNotExist()

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "navbar": NavBar(request),
            "title": "Planetapéia - Convite",
            "header": "Convite por chave",
        }
        return self.render_to_response(context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        if not (chave := request.POST.get("chave")):
            messages.warning(request, "Chave do convite não foi informada")

        elif not Convite.objects.filter(hash=chave).first():
            messages.warning(request, "Não existe convite com a chave informada")

        else:
            return redirect("convite", chave)
        context = {
            "navbar": NavBar(request),
            "title": "Planetapéia - Convite",
            "header": "Convite por chave",
        }
        return self.render_to_response(context=context)

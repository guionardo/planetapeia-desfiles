from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.views.generic import TemplateView

from ...models import AprovacaoChoices, InscricaoDesfile
from ..utils import use_genero, NavBar


class MeusConvitesView(LoginRequiredMixin, TemplateView):
    template_name = "perfil/perfil_convites.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {"header": "Meus convites", "navbar": NavBar(request)}
        if inscricoes := InscricaoDesfile.objects.filter(
            pessoa=request.pessoa, desfile__data__gte=date.today()
        ).all():
            inscricoes_texto = []
            for inscricao in inscricoes:
                match inscricao.aprovacao:
                    case AprovacaoChoices.APROVADO:
                        inscricoes_texto.append(
                            f"Você foi {use_genero(request,'aprovad')} para o desfile {inscricao.desfile}"
                            + (
                                ""
                                if not inscricao.veiculo
                                else f" no {inscricao.veiculo}"
                            )
                        )
                    case AprovacaoChoices.REJEITADO:
                        inscricoes_texto.append(
                            f"Verifique com seu padrinho a situação da sua inscrição para o desfile {inscricao.desfile}"
                        )
                    case AprovacaoChoices.PENDENTE:
                        inscricoes_texto.append(
                            f"Sua inscrição para o desfile {inscricao.desfile} ainda está pendente"
                        )
        else:
            inscricoes_texto = [
                f"Você não está {use_genero(request,'inscrit')} em nenhum desfile"
            ]

        context["inscricoes"] = inscricoes_texto
        return self.render_to_response(context)

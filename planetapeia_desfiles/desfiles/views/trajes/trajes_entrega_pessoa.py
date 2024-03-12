from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from ...roles import ALMOXARIFE
from ...services import desfile_service, pessoa_service, trajes_service
from ..utils import NavBar, get_post_data


class TrajesEntregaPessoa(PermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "trajes/entrega_pessoa.html"
    permission_required = ALMOXARIFE

    def get(self, request: HttpRequest, cpf: str) -> HttpResponse:
        try:
            if not (pessoa := pessoa_service.get_pessoa(cpf)):
                raise ValidationError(f"Pessoa inexistente [{cpf}]")
            if traje := trajes_service.traje_com_pessoa(pessoa):
                raise ValidationError(f"{pessoa} já está de posse do traje {traje}")
            inscricao = desfile_service.validar_pessoa_convidada(pessoa)
            trajes = list(
                trajes_service.obter_inventario_trajes_disponiveis(
                    inscricao.veiculo.veiculo, pessoa.genero, pessoa.tamanho_traje
                )
            )
            context = dict(
                header="Entrega de traje",
                navbar=NavBar(request),
                trajes=trajes,
                pessoa=pessoa,
                inscricao=inscricao,
                checklist=trajes_service.obter_checklist_vazio(trajes[0]),
            )

            return self.render_to_response(context)

        except ValidationError as exc:
            messages.warning(request, exc.messages[0])
        return redirect("trajes_index")

    def post(self, request: HttpRequest, cpf: str) -> HttpResponse:
        try:
            cpf, inventario = get_post_data(request, "cpf", "inventario")
            if not (pessoa := pessoa_service.get_pessoa(cpf)):
                raise ValidationError(f"Pessoa inexistente [{cpf}]")
            if not (traje_inventario := trajes_service.obter_inventario(inventario)):
                raise ValidationError(f"Inventário #{inventario} não encontrado")
            checklist, obs = trajes_service.obter_checklist(request, traje_inventario)
            _ = trajes_service.entregar_traje(
                traje_inventario, pessoa, request.user, obs, checklist
            )
            messages.success(request, f"Traje {traje_inventario} entregue a {pessoa}")
        except ValidationError as exc:
            messages.warning(request, exc.messages[0])
        except Exception as exc:
            messages.warning(request, str(exc))

        return redirect("trajes_index")

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from ...models import SituacaoTrajeChoices
from ...models_utils import get_pessoa_name
from ...roles import ALMOXARIFE
from ...services import trajes_service
from ..utils import NavBar, get_post_data


class TrajesDevolucao(PermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "trajes/devolucao.html"
    permission_required = ALMOXARIFE

    def get(self, request: HttpRequest, num_inventario: int) -> HttpResponse:
        context = {
            "header": "Gerenciamento de trajes",
            "navbar": NavBar(request),
        }
        try:
            inventario = trajes_service.validar_devolucao_traje(num_inventario)
            context.update(
                {
                    "inventario": inventario,
                    "manutencao": inventario.situacao
                    == SituacaoTrajeChoices.MANUTENCAO,
                    "checklist": [
                        {"id": index, "item": item, "checado": False}
                        for index, item in enumerate(inventario.get_checklist_itens())
                    ],
                    "recebedor": get_pessoa_name(request.user),
                }
            )

        except ValidationError as exc:
            messages.warning(request, exc.messages[0])

        return self.render_to_response(context)

    def post(self, request: HttpRequest, num_inventario: int) -> HttpResponse:
        cpf, inventario = get_post_data(request, "cpf", "inventario")
        context = {
            "header": "Gerenciamento de trajes",
            "navbar": NavBar(request),
        }
        try:
            inventario = trajes_service.validar_devolucao_traje(num_inventario)
            mensagem_sucesso = f'{inventario} {"Retornando de manutenção" if inventario.situacao == SituacaoTrajeChoices.MANUTENCAO else f"Devolvido por {get_pessoa_name(inventario.pessoa)}"}'
            checklist, obs = trajes_service.obter_checklist(request, inventario)
            trajes_service.devolver_traje(request.user, inventario, checklist, obs)

            context.update(
                {
                    "inventario": inventario,
                    "manutencao": inventario.situacao
                    == SituacaoTrajeChoices.MANUTENCAO,
                    "checklist": [
                        {"id": index, "item": item, "checado": bool}
                        for index, item in enumerate(inventario.get_checklist_itens())
                    ],
                    "recebedor": get_pessoa_name(request.user),
                }
            )
            messages.success(request, mensagem_sucesso)

        except ValidationError as exc:
            messages.warning(request, exc.messages[0])

        return redirect("trajes_index")
        return self.render_to_response(context)

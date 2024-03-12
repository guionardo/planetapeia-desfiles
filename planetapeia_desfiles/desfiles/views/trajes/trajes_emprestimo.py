from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from ...roles import ALMOXARIFE
from ..utils import NavBar, get_post_data
from ...services import trajes_service


class TrajesEmprestimo(PermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "trajes/emprestimo.html"
    permission_required = ALMOXARIFE

    def get(
        self, request: HttpRequest, num_inventario: int, pessoa_id: str
    ) -> HttpResponse:
        try:
            (
                traje_inventario,
                pessoa,
                inscricao_desfile,
            ) = trajes_service.validar_entrega_traje(pessoa_id, num_inventario)
            context = {
                "header": "Empréstimo de traje",
                "navbar": NavBar(request),
                "pessoa": pessoa,
                "desfile": inscricao_desfile.desfile,
                "traje_inventario": traje_inventario,
                "checklist": [
                    {"id": index, "item": item, "checado": bool}
                    for index, item in enumerate(traje_inventario.get_checklist_itens())
                ],
            }
            return self.render_to_response(context)
        except ValidationError as exc:
            messages.warning(request, exc.messages[0])
            return redirect("trajes_index")

    def post(
        self, request: HttpRequest, num_inventario: int, pessoa_id: str
    ) -> HttpResponse:
        cpf, inventario, obs = get_post_data(request, "cpf", "inventario", "obs")
        (
            traje_inventario,
            pessoa,
            inscricao_desfile,
        ) = trajes_service.validar_entrega_traje(pessoa_id, num_inventario)
        checklist = [
            (item, request.POST.get(f"check_{index}") is not None)
            for index, item in enumerate(traje_inventario.get_checklist_itens())
        ]

        traje_historico = trajes_service.entregar_traje(
            traje_inventario, pessoa, request.user, obs, checklist
        )
        messages.success(request, f"{traje_historico}")

        return redirect("trajes_index")

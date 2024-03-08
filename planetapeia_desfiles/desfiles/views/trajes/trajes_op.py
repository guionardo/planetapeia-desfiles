from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.views.generic import TemplateView

from ...models import Pessoa, TrajeInventario
from ...roles import ALMOXARIFE
from ..utils import NavBar, get_post_data


class TrajesOp(LoginRequiredMixin, TemplateView):
    template_name = "trajes/op.html"

    def get(self, request: HttpRequest, num_inventario: int) -> HttpResponse:
        if not request.user.has_perm(ALMOXARIFE):
            return HttpResponseForbidden()
        context = {
            "header": "Gerenciamento de trajes",
            "navbar": NavBar(request),
        }

        return self.render_to_response(context)

    def post(self, request: HttpRequest, num_inventario: int) -> HttpResponse:
        cpf, inventario = get_post_data(request, "cpf", "inventario")
        context = {
            "header": "Gerenciamento de trajes",
            "navbar": NavBar(request),
        }
        traje, pessoa = None, None
        try:
            if not (cpf or inventario):
                raise Exception("Informe um dos campos!")

            if cpf:
                if not (pessoa := Pessoa.objects.filter(pk=cpf).first()):
                    raise Exception(f"Não encontrei nenhuma pessoa com CPF {cpf}")
            if inventario:
                if not (traje := TrajeInventario.objects.filter(pk=inventario).first()):
                    raise Exception(
                        f"Não encontrei nenhum traje com inventário nº {inventario}"
                    )

            if pessoa and not traje:
                # Tenta localizar um traje sob posse da pessoa
                # if traje := TrajeInventario.objects.filter(pessoa=pessoa).all():

                if not (trajes := TrajeInventario.objects.filter(pessoa=pessoa).all()):
                    raise Exception(f"{pessoa} não consta com nenhum traje")
                if len(trajes) > 1:
                    raise Exception(
                        f"{pessoa} consta com os seguintes trajes [{tuple(traje.num_inventario for traje in trajes)}]"
                    )
                traje = trajes[0]
            elif traje := TrajeInventario.objects.filter(pk=inventario).first():
                pessoa = traje.pessoa
            else:
                raise Exception(
                    f"Não encontrei nenhum traje com inventário nº {inventario}"
                )

        except Exception as exc:
            messages.warning(request, str(exc))
            return self.render_to_response(context)

        context.update({"traje": traje, "pessoa": pessoa})
        return redirect("traje_op", (traje.num_inventario))

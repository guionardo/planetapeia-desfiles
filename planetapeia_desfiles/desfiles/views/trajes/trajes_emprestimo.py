from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.views.generic import TemplateView

from ...models import (
    AprovacaoChoices,
    InscricaoDesfile,
    Pessoa,
    SituacaoTrajeChoices,
    Traje,
    TrajeInventario,
)
from ...roles import ALMOXARIFE
from ...services.date_time_provider import DateTimeProvider
from ..utils import NavBar, get_post_data


class TrajesEmprestimo(LoginRequiredMixin, TemplateView):
    template_name = "trajes/emprestimo.html"

    def get(
        self, request: HttpRequest, num_inventario: int, pessoa_id: str
    ) -> HttpResponse:
        if not request.user.has_perm(ALMOXARIFE):
            return HttpResponseForbidden()
        if not (pessoa := Pessoa.objects.filter(pk=pessoa_id).first()):
            messages.warning(
                request, f"Não foi encontrada uma pessoa com CPF {pessoa_id}"
            )
            return redirect("trajes_index")

        if not (
            inscricao := InscricaoDesfile.objects.filter(
                pessoa=pessoa,
                aprovacao=AprovacaoChoices.APROVADO,
                data_desfile__gte=DateTimeProvider.today(),
            ).first()
        ):
            messages.warning(
                request,
                f"Não foi encontrada nenhuma inscrição para desfile aprovada para {pessoa}",
            )
            return redirect("trajes_index")

        if not (
            traje := Traje.objects.filter(
                veiculo=inscricao.veiculo, genero=pessoa.genero
            ).first()
        ):
            messages.warning(
                request,
                f"Não foi encontrado nenhum traje {pessoa.get_genero_display()} para {inscricao.veiculo}",
            )
            return redirect("trajes_index")

        if not (
            inventarios := TrajeInventario.objects.filter(
                traje=traje,
                tamanho=pessoa.tamanho_traje,
                situacao=SituacaoTrajeChoices.DISPONIVEL,
            ).all()
        ):
            messages.warning(
                request,
                f"Não há trajes {pessoa.get_genero_display()} para {inscricao.veiculo} no tamanho {pessoa.get_tamanho_traje_display()} disponíveis",
            )
            return redirect("trajes_index")

        context = {
            "header": "Empréstimo de traje",
            "navbar": NavBar(request),
            "pessoa": pessoa,
            "inventarios": inventarios,
        }

        if num_inventario:
            if traje := TrajeInventario.objects.filter(pk=num_inventario).first():
                trajes = [traje]
            else:
                trajes = []
        else:
            # Localizar trajes disponíveis para a pessoa
            trajes = TrajeInventario.objects.filter(
                # traje__traje__genero=pessoa.genero,
                # traje__tamanho=pessoa.tamanho_traje,
                situacao=SituacaoTrajeChoices.DISPONIVEL,
            ).all()

        # TODO: Implementar validação dos trajes disponíveis para o tamanho da pessoa,
        context["trajes"] = trajes
        return self.render_to_response(context)

    def post(
        self, request: HttpRequest, num_inventario: int, pessoa_id: str
    ) -> HttpResponse:
        if not request.user.has_perm(ALMOXARIFE):
            return HttpResponseForbidden()
        cpf, inventario = get_post_data(request, "cpf", "inventario")
        context = {
            "header": "Gerenciamento de trajes",
            "navbar": NavBar(request),
        }
        # TODO: Implementar atualização do inventário: empréstimo

        return self.render_to_response(context)

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.views.generic import TemplateView

from ...models import (
    Pessoa,
    SituacaoTrajeChoices,
    TrajeInventario,
    InscricaoDesfile,
    AprovacaoChoices,
    Traje,
)
from ...roles import ALMOXARIFE
from ..utils import NavBar, get_post_data
from ...services.date_time_provider import DateTimeProvider


class TrajesIndex(LoginRequiredMixin, TemplateView):
    template_name = "trajes/index.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.has_perm(ALMOXARIFE):
            return HttpResponseForbidden()
        context = {
            "header": "Gerenciamento de trajes",
            "navbar": NavBar(request),
        }

        return self.render_to_response(context)

    def traje_entrega(self, request: HttpRequest, context: dict) -> HttpResponse:
        cpf, inventario = get_post_data(request, "cpf", "inventario")
        if not (pessoa := Pessoa.objects.filter(pk=cpf).first()):
            messages.warning(request, f"Não encontrei nenhuma pessoa com o CPF {cpf}")
            return context
        if not inventario:
            messages.warning(request, "Número do inventário é obrigatório")
            return context
        if not (
            traje_inventario := TrajeInventario.objects.filter(pk=inventario).first()
        ):
            messages.warning(
                request,
                f"Não encontrei nenhum traje inventariado sob o número {inventario}",
            )
            return context
        if traje_inventario.situacao != SituacaoTrajeChoices.DISPONIVEL:
            messages.warning(
                request,
                f"O traje {traje_inventario} está {traje_inventario.get_situacao_display()}",
            )
            return context

        if not (
            inscricao := InscricaoDesfile.objects.filter(
                pessoa=pessoa,
                data_desfile__gte=DateTimeProvider.today(),
                aprovacao=AprovacaoChoices.APROVADO,
            ).first()
        ):
            messages.warning(
                request, f"Não há inscrição aprovada em desfile para {pessoa}"
            )
            return context
        if not (
            traje := Traje.objects.filter(veiculo=inscricao.veiculo.veiculo).first()
        ):
            messages.warning(
                request, f"Não encontrei o traje relacionado à inscrição {inscricao}"
            )
            return context
        if traje.pk != traje_inventario.traje.pk:
            messages.warning(
                request,
                f"A inscrição para o veículo {inscricao.veiculo.veiculo} pede o traje {traje} mas você selecionou o inventário {traje_inventario}",
            )
            return context
        if traje_inventario.tamanho != pessoa.tamanho_traje:
            messages.warning(
                request,
                f"{pessoa} está cadastrada com tamanho de traje {pessoa.get_tamanho_traje_display()} mas o inventário {traje_inventario} tem tamanho {traje_inventario.get_tamanho_display()}",
            )
            return context

        # TODO: Verificar a cobrança antecipada do traje
        # TODO: Implementar salvar a entrega do traje
        return context

    def post(self, request: HttpRequest) -> HttpResponse:
        context = {
            "header": "Gerenciamento de trajes",
            "navbar": NavBar(request),
        }
        ops = request.POST.get("ops")

        match ops:
            case "traje_entrega":
                context = self.traje_entrega(request, context)

            case _:
                messages.error(request, "Operação inválida")

        return self.render_to_response(context)

        cpf, inventario = get_post_data(request, "cpf", "inventario")
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
                if trajes := TrajeInventario.objects.filter(pessoa=pessoa).all():
                    if len(trajes) > 1:
                        raise Exception(
                            f"{pessoa} consta com os seguintes trajes [{tuple(traje.num_inventario for traje in trajes)}]"
                        )
                    traje = trajes[0]
            elif traje and not pessoa:
                pessoa = traje.pessoa

            if traje and traje.pessoa and pessoa and traje.pessoa.pk != pessoa.pk:
                raise Exception(f"Traje {traje} consta com a pessoa {pessoa}")

            if pessoa and not traje:
                # Pessoa sem traje, opção = empréstimo
                return redirect("traje_emprestimo", 0, pessoa.pk)

            if pessoa and traje:
                if traje.pessoa:
                    # Pessoa consta com o traje: opção = devolução
                    return redirect("traje_devolucao", (traje.pk,))
                else:
                    # Pessoa não tem traje e fará o empréstimo
                    return redirect(
                        "traje_emprestimo",
                        kwargs={"num_inventario": traje.pk, "pessoa_id": pessoa.pk},
                    )

            if traje:
                # Apenas o traje = manutenção ou devolução
                if traje.situacao == SituacaoTrajeChoices.DISPONIVEL:
                    # Manutenção, Descarte, Extravio
                    return redirect("traje_saida", (traje.pk,))
                elif traje.situacao in [SituacaoTrajeChoices.MANUTENCAO]:
                    # Em manutenção => Devolução
                    return redirect("traje_devolucao", (traje.pk,))

        except Exception as exc:
            messages.warning(request, str(exc))
            return self.render_to_response(context)

        context.update({"traje": traje, "pessoa": pessoa})
        return redirect("trajes_op", (traje.num_inventario))

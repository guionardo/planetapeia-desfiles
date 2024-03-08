from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ...models import (
    AprovacaoChoices,
    InscricaoDesfile,
    Pessoa,
    Traje,
    TrajeInventario,
    nome_pesquisavel,
)
from ...services.date_time_provider import DateTimeProvider


@csrf_exempt
def busca_pessoa(request: HttpRequest):
    response = dict(count=0, items=[])
    if nome := nome_pesquisavel(request.GET.get("nome")):
        if (cpf := "".join([c for c in nome if c.isnumeric()])) and len(cpf) == 11:
            pessoas = [Pessoa.objects.filter(pk=cpf).first()]
        else:
            pessoas = (
                Pessoa.objects.filter(nome_busca__icontains=nome)
                .order_by("nome_busca")
                .all()
            )
        for pessoa in pessoas:
            traje_inventario = TrajeInventario.objects.filter(pessoa=pessoa).first()
            inscricao = InscricaoDesfile.objects.filter(
                pessoa=pessoa,
                data_desfile__gte=DateTimeProvider.today(),
                aprovacao=AprovacaoChoices.APROVADO,
            ).first()
            traje = (
                None
                if not inscricao
                else Traje.objects.filter(veiculo=inscricao.veiculo.veiculo).first()
            )
            response["items"].append(
                dict(
                    cpf=pessoa.pk,
                    nome=pessoa.nome,
                    traje_inventario=traje_inventario.pk if traje_inventario else None,
                    traje_inventario_desc=str(traje_inventario)
                    if traje_inventario
                    else "",
                    inscricao=None if not inscricao else str(inscricao),
                    traje=None
                    if not traje
                    else (f"{traje} {pessoa.get_tamanho_traje_display()}"),
                )
            )

        response["count"] = len(response["items"])

    return JsonResponse(response)

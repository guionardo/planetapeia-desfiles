from typing import List, Tuple

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http.request import HttpRequest

from ..models import (
    AprovacaoChoices,
    GenerosChoices,
    InscricaoDesfile,
    Pessoa,
    SituacaoDesfileChoices,
    SituacaoTrajeChoices,
    TamanhosTrajeChoices,
    Traje,
    TrajeHistorico,
    TrajeInventario,
    TrajeMovimentoChoices,
    Veiculo,
)
from ..services.date_time_provider import DateTimeProvider
from ..utils.genero import parse_genero
from .pessoa_service import get_pessoa


def validar_entrega_traje(
    cpf: str, inventario: int
) -> Tuple[TrajeInventario | None, Pessoa | None, InscricaoDesfile | None]:
    """Validar se a pessoa do CPF pode receber o traje"""
    if not inventario:
        raise ValidationError("Inventário do traje não foi informado")
    # Validar traje inventário existente e disponível
    if not (traje_inventario := TrajeInventario.objects.filter(pk=inventario).first()):
        raise ValidationError(f"Traje não encontrado [#{inventario}]")
    if traje_inventario.situacao != SituacaoTrajeChoices.DISPONIVEL:
        raise ValidationError(traje_inventario.situacao_str())

    if not (pessoa := get_pessoa(cpf)):
        raise ValidationError(f"CPF não encontrado [{cpf}]")

    if not (
        inscricao := InscricaoDesfile.objects.filter(
            pessoa=pessoa,
            desfile__situacao=SituacaoDesfileChoices.CONFIRMADO,
            desfile__data__gte=DateTimeProvider.today(),
        ).first()
    ):
        raise ValidationError(
            f"{pessoa} não consta com inscrição em nenhum desfile confirmado"
        )

    if inscricao.aprovacao != AprovacaoChoices.APROVADO:
        raise ValidationError(str(inscricao))

    if traje_inventario.traje.veiculo.pk != inscricao.veiculo.veiculo.pk:
        raise ValidationError(
            f"{pessoa} tem inscrição para {inscricao.veiculo.veiculo}, mas o traje do inventário é para {traje_inventario.traje.veiculo}"
        )

    if traje_inventario.tamanho != pessoa.tamanho_traje:
        raise ValidationError(
            parse_genero(
                f"{pessoa} está cadastrad~o|a~ com tamanho de traje "
                f"{pessoa.get_tamanho_traje_display()} mas o inventário {traje_inventario} "
                "tem tamanho {traje_inventario.get_tamanho_display()}",
                pessoa.genero,
            )
        )

    return traje_inventario, pessoa, inscricao


def entregar_traje(
    traje_inventario: TrajeInventario,
    pessoa: Pessoa,
    usuario: User,
    obs: str,
    checklist: List[tuple[str, bool]],
) -> TrajeHistorico:
    if traje_inventario.situacao != SituacaoTrajeChoices.DISPONIVEL:
        raise ValidationError(
            f"Traje {traje_inventario} indisponível para entrega: {traje_inventario.situacao_str()}"
        )

    historico = TrajeHistorico.objects.create(
        traje=traje_inventario,
        pessoa=pessoa,
        movimento=TrajeMovimentoChoices.EMPRESTIMO,
        usuario=usuario,
        obs=obs,
    )
    for item, checado in checklist:
        historico.checagem.filter(item=item).update(checado=checado)
    return historico


def validar_devolucao_traje(inventario: int) -> TrajeInventario:
    """Verifica se o inventário pode ser devolvido"""
    if not (traje_inventario := TrajeInventario.objects.filter(pk=inventario).first()):
        raise ValidationError(f"Traje #{inventario} inexistente")
    if traje_inventario.situacao not in [
        SituacaoTrajeChoices.EMPRESTADO,
        SituacaoTrajeChoices.MANUTENCAO,
    ]:
        raise ValidationError(
            f"Traje {traje_inventario} indisponível para devolução: {traje_inventario.situacao_str()}"
        )
    return traje_inventario


def obter_checklist(
    request: HttpRequest, traje_inventario: TrajeInventario
) -> Tuple[List[Tuple[str, bool]], str]:
    """Obtém uma lista de checks e a observação"""
    checklist = [
        (item, request.POST.get(f"check_{index}") is not None)
        for index, item in enumerate(traje_inventario.get_checklist_itens())
    ]
    obs = request.POST.get("obs")
    return checklist, obs


def obter_checklist_vazio(traje_inventario: TrajeInventario):
    return [
        dict(item=item, checado=False)
        for item in traje_inventario.get_checklist_itens()
    ]


def devolver_traje(
    user: User,
    inventario: TrajeInventario,
    checklist: List[Tuple[str, bool]],
    obs: str,
):
    try:
        historico = TrajeHistorico.objects.create(
            traje=inventario,
            obs=obs,
            movimento=TrajeMovimentoChoices.DEVOLUCAO,
            usuario=user,
            pessoa=None,
        )
        checks = {item: checado for item, checado in checklist}
        for check in historico.checagem.all():
            check.checado = checks.get(check.item, False)
            check.save()
    except ValidationError:
        raise
    except Exception as exc:
        raise ValidationError(str(exc))


def obter_inventario_trajes_disponiveis(
    veiculo: Veiculo, genero: GenerosChoices, tamanho: TamanhosTrajeChoices
) -> List[TrajeInventario]:
    if not (trajes := Traje.objects.filter(veiculo=veiculo, genero=genero).all()):
        raise ValidationError(f"Não existem trajes cadastrados para {veiculo}")
    inventarios = []
    for traje in trajes:
        inventarios.extend(
            TrajeInventario.objects.filter(
                traje=traje, tamanho=tamanho, situacao=SituacaoTrajeChoices.DISPONIVEL
            ).all()
        )

    if not inventarios:
        raise ValidationError(f"Não existem trajes disponíveis para {veiculo}")
    return inventarios


def traje_com_pessoa(pessoa: Pessoa) -> TrajeInventario | None:
    return TrajeInventario.objects.filter(pessoa=pessoa).first()


def obter_inventario(inventario: int | str) -> TrajeInventario | None:
    return TrajeInventario.objects.filter(pk=inventario).first()

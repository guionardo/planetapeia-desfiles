from typing import List, Tuple

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ..models import (
    InscricaoDesfile,
    Pessoa,
    SituacaoDesfileChoices,
    SituacaoTrajeChoices,
    TrajeHistorico,
    TrajeInventario,
    TrajeMovimentoChoices,
)
from ..services.date_time_provider import DateTimeProvider
from .pessoa import PessoaService


class TrajesService:
    @classmethod
    def validar_entrega_traje(
        cls, cpf: str, inventario: int
    ) -> Tuple[TrajeInventario | None, Pessoa | None, InscricaoDesfile | None]:
        """Validar se a pessoa do CPF pode receber o traje"""

        # Validar traje inventário existente e disponível
        if not (
            traje_inventario := TrajeInventario.objects.filter(pk=inventario).first()
        ):
            raise ValidationError(f"Traje não encontrado [#{inventario}]")
        if traje_inventario.situacao != SituacaoTrajeChoices.DISPONIVEL:
            raise ValidationError(traje_inventario.situacao_str())

        if not (pessoa := PessoaService.get_pessoa(cpf)):
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

        if traje_inventario.traje.veiculo.pk != inscricao.veiculo.veiculo.pk:
            raise ValidationError(
                f"{pessoa} tem inscrição para {inscricao.veiculo.veiculo}, mas o traje do inventário é para {traje_inventario.traje.veiculo}"
            )

        if traje_inventario.tamanho != pessoa.tamanho_traje:
            raise ValidationError(
                f"{pessoa} está cadastrada com tamanho de traje {pessoa.get_tamanho_traje_display()} mas o inventário {traje_inventario} tem tamanho {traje_inventario.get_tamanho_display()}"
            )

        return traje_inventario, pessoa, inscricao

    @classmethod
    def entregar_traje(
        cls,
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
            # historico.checagem.add(
            #     TrajeHistoricoChecklistItem.objects.create(
            #         historico=historico, item=item, checado=checado
            #     )
            # )
        return historico

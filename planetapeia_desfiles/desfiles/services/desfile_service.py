from django.core.exceptions import ValidationError

from ..models import AprovacaoChoices, InscricaoDesfile, Pessoa, SituacaoDesfileChoices


def validar_pessoa_convidada(pessoa: Pessoa) -> InscricaoDesfile:
    """Verifica se a pessoa tem inscrição para um desfile confirmado"""
    if not (
        inscricoes := InscricaoDesfile.objects.filter(
            pessoa=pessoa, desfile__situacao=SituacaoDesfileChoices.CONFIRMADO
        ).all()
    ):
        raise ValidationError(f"{pessoa} não tem inscrição para desfile confirmado")

    for inscricao in inscricoes:
        if inscricao.aprovacao == AprovacaoChoices.APROVADO:
            return inscricao

    raise ValidationError(
        f'{pessoa} tem inscrição não aprovada para desfile(s): {", ".join(str(inscricao.desfile) for inscricao in inscricoes)}'
    )

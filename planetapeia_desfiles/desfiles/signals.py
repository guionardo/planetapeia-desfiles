import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    AprovacaoChoices,
    Convite,
    InscricaoDesfile,
    StaffPadraoVeiculo,
    Veiculo,
)
from .models_utils import get_robot_user


@receiver(post_save, sender=InscricaoDesfile)
def post_save_inscricao_desfile(
    sender: InscricaoDesfile, instance: InscricaoDesfile, **kwargs
):
    if not instance.convite:
        return

    # Recalcula número de inscritos aprovados
    count = InscricaoDesfile.objects.filter(
        convite_id=instance.convite.id, aprovacao=AprovacaoChoices.APROVADO
    ).count()
    if instance.convite.convidados_confirmados != count:
        logging.getLogger("signals").info(
            f"[post_save_inscricao_desfile] {instance.convite} convidados_confirmados {instance.convite.convidados_confirmados} -> {count}"
        )
        Convite.objects.filter(pk=instance.convite.pk).update(
            convidados_confirmados=count
        )
        # instance.convite.convidados_confirmados = count
        # instance.convite.save()


@receiver(post_save, sender=Veiculo)
def post_save_veiculo(sender, instance: Veiculo, **kwargs):
    if StaffPadraoVeiculo.objects.filter(veiculo=instance).count():
        return

    spv = StaffPadraoVeiculo.objects.create(veiculo=instance, usuario=get_robot_user())
    logging.getLogger("signals").info(
        f"[post_save_veiculo] criado staff padrão para {spv}"
    )


def enable():
    pass

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AprovacaoChoices, InscricaoDesfile, Veiculo, StaffPadraoVeiculo
from .models_utils import get_robot_user


@receiver(post_save, sender=InscricaoDesfile)
def post_save_inscricao_desfile(
    sender: InscricaoDesfile, instance: InscricaoDesfile, **kwargs
):
    if instance.convite:
        # Recalcula número de inscritos aprovados
        count = InscricaoDesfile.objects.filter(
            convite_id=instance.convite.id, aprovacao=AprovacaoChoices.APROVADO
        ).count()
        if instance.convite.convidados_confirmados != count:
            instance.convite.convidados_confirmados = count
            instance.convite.save()


@receiver(post_save, sender=Veiculo)
def post_save_veiculo(sender, instance: Veiculo, **kwargs):
    if StaffPadraoVeiculo.objects.filter(veiculo=instance).count():
        return

    _ = StaffPadraoVeiculo.objects.create(veiculo=instance, usuario=get_robot_user())
    # TODO: Implementar log da operação


def enable():
    pass


print("Signals enabled")

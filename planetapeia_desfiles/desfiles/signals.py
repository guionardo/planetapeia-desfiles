from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AprovacaoChoices, InscricaoDesfile


@receiver(post_save, sender=InscricaoDesfile)
def post_save_inscricao_desfile(sender: InscricaoDesfile, instance:InscricaoDesfile, **kwargs):
    if instance.convite:
        # Recalcula número de inscritos aprovados
        count = InscricaoDesfile.objects.filter(
            convite_id=instance.convite.id, aprovacao=AprovacaoChoices.APROVADO
        ).count()
        if instance.convite.convidados_confirmados != count:
            instance.convite.convidados_confirmados = count
            instance.convite.save()


def enable():
    pass

print('Signals enabled')
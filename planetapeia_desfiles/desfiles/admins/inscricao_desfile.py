from collections import defaultdict

from django.contrib import admin, messages
from django.urls import reverse

from ..models import AprovacaoChoices
from ..services.date_time_provider import DateTimeProvider
from ..services.user_messages import UserMessages


@admin.action(description="Aprovar")
def aprovar_inscricao(modeladmin, request, queryset):
    outros_aprovadores = defaultdict(list)
    for inscricao in queryset:
        if inscricao.aprovacao == AprovacaoChoices.REJEITADO:
            if inscricao.aprovador == request.user:
                inscricao.aprovacao = AprovacaoChoices.APROVADO
                inscricao.data_aprovacao = DateTimeProvider.now()
                inscricao.save()
                messages.success(request, str(inscricao))
            else:
                messages.warning(request, f"Rejeição por outro admin: {inscricao}")
                outros_aprovadores[inscricao.aprovador].append(inscricao)
        elif inscricao.aprovacao == AprovacaoChoices.PENDENTE:
            inscricao.aprovacao = AprovacaoChoices.APROVADO
            inscricao.data_aprovacao = DateTimeProvider.now()
            inscricao.aprovador = request.user
            inscricao.save()
            messages.success(request, str(inscricao))
    if outros_aprovadores:
        um = UserMessages(request)
        for outro_aprovador, inscricoes in outros_aprovadores.items():
            texto_inscricoes = ", ".join(str(inscricao) for inscricao in inscricoes)
            um.send_message(
                outro_aprovador,
                f"Verificar aprovação de inscrições: {texto_inscricoes}",
                link=reverse("admin:desfiles_inscricaodesfile_changelist"),
            )


class InscricaoDesfileAdmin(admin.ModelAdmin):
    list_filter = ["aprovacao", "desfile", "grupo"]
    list_display = [
        "desfile",
        "pessoa",
        "grupo",
        "responsavel_convite",
        "status_aprovacao",
    ]
    search_fields = ["pessoa__nome"]

    @admin.display(description="Responsável pelo convite")
    def responsavel_convite(self, obj):
        return obj.convite.usuario.get_full_name() or obj.convite.usuario

    @admin.display(description="Aprovação")
    def status_aprovacao(self, obj):
        return obj.status_aprovacao()

    actions = [aprovar_inscricao]

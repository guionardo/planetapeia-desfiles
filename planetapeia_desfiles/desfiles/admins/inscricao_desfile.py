from django.contrib import admin, messages

from ..models import AprovacaoChoices


@admin.action(description="Aprovar")
def aprovar_inscricao(modeladmin, request, queryset):
    # TODO: Implementar mensagens quando a aprovação for de um inscrito previamente rejeitado

    if all(inscricao.aprovacao == AprovacaoChoices.PENDENTE for inscricao in queryset):
        # Ok, todo mundo pendente
        queryset.update(aprovacao=AprovacaoChoices.APROVADO, aprovador=request.user)
        messages.success(request, "Inscrições aprovadas com sucesso")


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

from django.contrib import admin, messages
from django.contrib.admin.filters import EmptyFieldListFilter

from ..services.date_time_provider import DateTimeProvider


@admin.action(description="Confirmar revisão(ões)")
def confirmar_revisao(modeladmin, request, queryset):
    for revisao in queryset:
        if revisao.atendida_por and revisao.atendida_em:
            messages.warning(request, str(revisao))
            continue
        revisao.atendida_por = request.user
        revisao.atendida_em = DateTimeProvider.now()

        revisao.save()
        messages.success(request, str(revisao))


@admin.action(description="Cancelar revisão(ões)")
def cancelar_revisao(modeladmin, request, queryset):
    for revisao in queryset:
        if revisao.atendida_por == request.user and revisao.ativa:
            revisao.atendida_por = None
            revisao.atendida_em = None
            revisao.save()
            messages.success(request, str(revisao))
        else:
            messages.warning(
                request,
                f"Você não pode cancelar a revisão dada por outro usuário: {revisao}",
            )


class RevisaoSenhaAdmin(admin.ModelAdmin):
    actions = [confirmar_revisao, cancelar_revisao]
    list_display = [
        "pessoa",
        "data_solicitacao",
        "get_atendimento",
        "ativa",
    ]
    list_display_links = None
    list_filter = ["ativa", ("atendida_por", EmptyFieldListFilter)]

    def has_add_permission(self, request):
        return False

    # def has_delete_permission(self, request, obj=None) -> bool:
    #     return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    @admin.display(description="Atendida por")
    def get_atendente(self, obj):
        return (
            ""
            if not obj.atendida_por
            else (obj.atendida_por.get_full_name() or obj.atendida_por.get_username())
        )

    @admin.display(description="Atendimento")
    def get_atendimento(self, obj):
        if not obj.atendida_por:
            return ""
        return f"{(obj.atendida_por.get_full_name() or obj.atendida_por.get_username())} em {obj.atendida_em:%d/%m/%Y %H:%M}"

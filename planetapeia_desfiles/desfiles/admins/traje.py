from typing import Any
from django.contrib import admin
from django.http import HttpRequest

from ..models import TrajeHistorico, TrajeInventario, TrajeMovimentoChoices


class TrajeInventarioInline(admin.TabularInline):
    model = TrajeInventario
    show_change_link = True
    show_full_result_count = True
    readonly_fields = ["num_inventario", "tamanho", "situacao"]
    extra = 0


class TrajeAdmin(admin.ModelAdmin):
    inlines = [TrajeInventarioInline]


class TrajeHistoricoInline(admin.TabularInline):
    model = TrajeHistorico
    extra = 0
    fields = ["data", "movimento", "obs", "usuario", "pessoa"]
    readonly_fields = ["data"]
    show_change_link = True

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


# class TrajeTaxaInline(admin.TabularInline):
#     model = TrajeTaxa


class TrajeInventarioAdmin(admin.ModelAdmin):
    inlines = [TrajeHistoricoInline]
    list_display = [
        "num_inventario",
        "traje",
        "tamanho",
        "situacao",
        "usuario",
        "pessoa",
        "ultima_atualizacao",
    ]
    list_filter = ["situacao", "traje"]
    fields = [
        "num_inventario",
        "traje",
        "tamanho",
        "situacao",
        "usuario",
        "pessoa",
        "ultima_atualizacao",
    ]
    readonly_fields = ["situacao", "ultima_atualizacao", "usuario", "pessoa"]
    show_change_link = True

    def get_readonly_fields(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> list[str] | tuple[Any, ...]:
        readonly_fields = ["situacao", "ultima_atualizacao", "usuario", "pessoa"]
        if obj.id:
            readonly_fields.extend(["num_inventario", "traje", "tamanho"])
        return readonly_fields


class TrajeHistoricoAdmin(admin.ModelAdmin):
    list_display = ["traje", "data", "get_situacao", "get_checklist"]
    list_filter = ["traje"]
    ordering = ["traje", "data"]

    @admin.display(description="Situação")
    def get_situacao(self, obj: TrajeHistorico) -> str:
        match obj.movimento:
            case TrajeMovimentoChoices.ENTRADA:
                return "Entrada"
            case TrajeMovimentoChoices.EMPRESTIMO:
                return f"Empréstimo para {obj.pessoa}"
            case TrajeMovimentoChoices.DEVOLUCAO:
                return "Devolvido"
            case TrajeMovimentoChoices.DESCARTE:
                return "Descartado"
            case TrajeMovimentoChoices.MANUTENCAO:
                return "Enviado para manutenção"

        return "Não sei ainda"

    @admin.display(description="Checagem")
    def get_checklist(self, obj: TrajeHistorico) -> str:
        if obj.movimento not in [
            TrajeMovimentoChoices.EMPRESTIMO,
            TrajeMovimentoChoices.DEVOLUCAO,
        ]:
            return ""

        return ", ".join(str(check) for check in obj.checagem.all())

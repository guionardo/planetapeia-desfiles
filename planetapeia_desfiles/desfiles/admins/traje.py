from typing import Any
from django.contrib import admin
from django.http import HttpRequest

from ..models import TrajeHistorico, TrajeInventario


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

    def get_readonly_fields(
        self, request: HttpRequest, obj: Any | None = ...
    ) -> list[str] | tuple[Any, ...]:
        readonly_fields = ["situacao", "ultima_atualizacao", "usuario", "pessoa"]
        if obj.id:
            readonly_fields.extend(["num_inventario", "traje", "tamanho"])
        return readonly_fields

from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet


class UltimaLocalizacaoListFilter(admin.SimpleListFilter):
    title = "Última localização"
    parameter_name = "last"

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [
            (True, "Todas as localizações"),
            (True, "Somente a última localização"),
        ]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value():
            return queryset.order_by("pessoa", "-when").distinct("pessoa")
        return queryset


class LocalizacaoAdmin(admin.ModelAdmin):
    list_display = ["pessoa", "when", "ip", "pais", "estado", "cidade"]
    list_filter = ["pessoa", UltimaLocalizacaoListFilter]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

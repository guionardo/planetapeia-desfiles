from django.contrib import admin

from ..models import TrajeHistorico, TrajeInventario


class TrajeInventarioInline(admin.TabularInline):
    model = TrajeInventario
    show_change_link = True
    show_full_result_count = True
    readonly_fields = ["num_inventario", "tamanho", "situacao"]


class TrajeAdmin(admin.ModelAdmin):
    inlines = [TrajeInventarioInline]


class TrajeHistoricoInline(admin.TabularInline):
    model = TrajeHistorico


# class TrajeTaxaInline(admin.TabularInline):
#     model = TrajeTaxa


class TrajeInventarioAdmin(admin.ModelAdmin):
    inlines = [TrajeHistoricoInline]

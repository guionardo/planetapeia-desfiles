from django.contrib import admin
from ..models import InscricaoDesfile


class InscricaoDesfileInline(admin.TabularInline):
    model = InscricaoDesfile
    # TODO: Obter os veículos do desfile


class ConviteAdmin(admin.ModelAdmin):
    fields = [
        "desfile",
        "grupo",
        "valido_ate",
        "usuario",
        "data",
        "max_convidados",
        "convidados_confirmados",
        "hash",
    ]
    readonly_fields = ["data", "hash", "convidados_confirmados"]
    inlines = [InscricaoDesfileInline]

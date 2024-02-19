from datetime import date

from django.contrib import admin
from django.utils.html import format_html

from ..models import Pessoa, TiposCobrancaTrajeChoices


class PessoaAdmin(admin.ModelAdmin):
    list_display = ("nome", "grupo", "cpf", "image_tag")
    list_filter = ("grupo", "tipo")
    sortable_by = ["nome"]
    list_select_related = True
    fields = [
        ("cpf", "nome"),
        ("telefone", "data_nascimento", "genero", "idade"),
        ("peso", "altura", "tamanho_traje"),
        ("grupo", "tipo"),
        ("tipo_cobranca_traje", "cobrar_traje_str"),
    ]
    readonly_fields = ["cobrar_traje_str", "idade"]
    search_fields = ["nome"]

    def image_tag(self, obj: Pessoa):
        return format_html('<img src="{}" width="128" />'.format(obj.get_foto()))

    image_tag.short_description = "Foto"

    @admin.display(description="Cobrar traje")
    def cobrar_traje_str(self, obj):
        if obj.tipo_cobranca_traje == TiposCobrancaTrajeChoices.GRUPO:
            cobrar = obj.grupo.tipo_cobranca_traje
            grupo = True
        else:
            cobrar = obj.tipo_cobranca_traje == TiposCobrancaTrajeChoices.SIM
            grupo = False

        return ("Isento(a)" if not cobrar else "Cobrança") + (
            " [grupo]" if grupo else ""
        )

    @admin.display(description="Idade")
    def idade(self, obj: Pessoa):
        if not obj.data_nascimento:
            return "-"
        return f'{int((date.today()-obj.data_nascimento).days/365.25)} ({"Criança" if obj.e_crianca else "Adulto"})'

import datetime
from datetime import date

from django.contrib import admin
from django.contrib.auth.models import User
from django.http.request import HttpRequest

from .models import (
    Convite,
    Desfile,
    Grupo,
    InscricaoDesfile,
    Pessoa,
    TiposCobrancaTrajeChoices,
    Traje,
    TrajeHistorico,
    TrajeInventario,
    TrajeTaxa,
    Veiculo,
)

from .signals import enable


class PessoaAdmin(admin.ModelAdmin):
    list_display = ("nome", "grupo", "cpf")
    sortable_by = ["nome"]
    list_select_related = True
    fields = [
        ("cpf", "nome"),
        ("telefone", "data_nascimento", "genero", "idade"),
        ("peso", "altura", "tamanho_traje"),
        ("grupo", "tipo_cobranca_traje", "cobrar_traje_str"),
    ]
    readonly_fields = ["cobrar_traje_str", "idade"]

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
    def idade(self, obj):
        return f'{int((date.today()-obj.data_nascimento).days/365.25)} ({"Criança" if obj.e_crianca else "Adulto"})'


class GrupoAdmin(admin.ModelAdmin):
    pass


class VeiculoAdmin(admin.ModelAdmin):
    list_display = ["nome"]
    fields = [
        ("nome", "imagem"),
        (
            "capacidade",
            "qtd_staffs",
            "qtd_max_criancas",
            "qtd_max_mulheres",
            "qtd_max_homens",
        ),
        ("peso_individual_max", "peso_total_max"),
    ]


class DesfileAdmin(admin.ModelAdmin):
    fields = [
        "nome",
        ("local", "data"),
        ("confirmado", "data_aprovacao", "aprovador"),
        "veiculos",
    ]

    def get_fields(self, request: HttpRequest, obj):
        confirmado = []
        if obj.confirmado:
            confirmado.extend(["data_aprovacao", "aprovador"])
        # confirmado.append("aprovador")
        fields = ["nome", ("local", "data"), "confirmado", confirmado, "veiculos"]
        return fields

    def get_readonly_fields(self, request, obj: Desfile):
        if obj.confirmado:
            return ["nome", "local", "data", "veiculos", "aprovador", "data_aprovacao"]
        return []

    def get_form(self, request: HttpRequest, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if field := form.base_fields.get("aprovador"):
            field.queryset = User.objects.filter(id=request.user.id)
        return form

    def save_model(self, request, obj: Desfile, form, change) -> None:
        if obj.confirmado and not obj.aprovador:
            obj.aprovador = request.user
            obj.data_aprovacao = datetime.datetime.now()

        return super().save_model(request, obj, form, change)


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


class InscricaoDesfileAdmin(admin.ModelAdmin):
    pass


admin.site.register(Pessoa, PessoaAdmin)
admin.site.register(Grupo, GrupoAdmin)
admin.site.register(Veiculo, VeiculoAdmin)
admin.site.register(Desfile, DesfileAdmin)

admin.site.register(Traje, TrajeAdmin)
admin.site.register(TrajeInventario, TrajeInventarioAdmin)

admin.site.register(Convite, ConviteAdmin)
admin.site.register(InscricaoDesfile, InscricaoDesfileAdmin)

admin.site.site_title = "Planetapéia Desfiles"
admin.site.site_header = "Planetapéia Desfiles"

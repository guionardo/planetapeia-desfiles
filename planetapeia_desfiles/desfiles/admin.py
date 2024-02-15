import datetime
import logging
from collections import OrderedDict
from datetime import date
from typing import Any

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.query import QuerySet
from django.forms.models import ModelMultipleChoiceField
from django.http.request import HttpRequest
from django.utils.html import format_html

from .models import (
    Convite,
    Desfile,
    Grupo,
    InscricaoDesfile,
    Pessoa,
    PessoaStaff,
    StaffPadrao,
    StaffPadraoVeiculo,
    TiposCobrancaTrajeChoices,
    TiposPessoasChoices,
    Traje,
    TrajeHistorico,
    TrajeInventario,
    Veiculo,
)


class PessoaAdmin(admin.ModelAdmin):
    list_display = ("nome", "grupo", "cpf", "image_tag")
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
        if obj and obj.confirmado:
            confirmado.extend(["data_aprovacao", "aprovador"])
        # confirmado.append("aprovador")
        fields = ["nome", ("local", "data"), "confirmado", confirmado, "veiculos"]
        return fields

    def get_readonly_fields(self, request, obj: Desfile):
        if obj and obj.confirmado:
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


class StaffInline(admin.TabularInline):
    model = StaffPadrao
    extra = 0

    def get_formset(self, request: Any, obj: Any | None = ..., **kwargs: Any) -> Any:
        fs = super().get_formset(request, obj, **kwargs)
        return fs


class StaffPadraoVeiculoAdmin(admin.ModelAdmin):
    list_display = ["veiculo", "capacidade", "staffs", "pessoas_count"]
    fields = ["veiculo", "ultimo_ajuste", "usuario"]
    readonly_fields = ["ultimo_ajuste"]
    inlines = [StaffInline]

    def formfield_for_manytomany(
        self, db_field, request, **kwargs
    ) -> ModelMultipleChoiceField:
        if db_field.name == "pessoas":
            kwargs["queryset"] = StaffPadrao.objects.filter(
                ~Q(pessoa__tipo=TiposPessoasChoices.CONVIDADO)
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def capacidade(self, instance):
        return instance.veiculo.capacidade

    @admin.display(description="Máximo de staffs")
    def staffs(self, instance):
        return instance.veiculo.qtd_staffs

    @admin.display(description="Staffs registrados")
    def pessoas_count(self, instance: StaffPadraoVeiculo):
        return StaffPadrao.objects.filter(staff_padrao_veiculo=instance).count()


class StaffsAdmin(admin.ModelAdmin):
    list_display = ["__str__", "staff_padrao_veiculo"]
    # fields = ["__str__", "staff_padrao_veiculo"]
    readonly_fields = ["staff_padrao_veiculo"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        queryset = (
            super().get_queryset(request).filter(~Q(tipo=TiposPessoasChoices.CONVIDADO))
        )
        return queryset

    def staff_padrao_veiculo(self, obj: PessoaStaff):
        if spv := obj.staff_padrao_veiculo:
            return f"{obj.nome} [{obj.get_tipo_display()} - {spv.veiculo}]"

    def get_actions(self, request: HttpRequest) -> OrderedDict[Any, Any]:
        actions = super().get_actions(request)
        logger = logging.getLogger("staffs")
        for spv in StaffPadraoVeiculo.objects.all():

            def add_to_spv(staff: PessoaStaff, request: HttpRequest, queryset):
                for pessoa in queryset:
                    if staff_padrao := StaffPadrao.objects.filter(
                        pessoa=pessoa
                    ).first():
                        if staff_padrao.staff_padrao_veiculo == spv:
                            continue
                        anterior = staff_padrao.staff_padrao_veiculo
                        staff_padrao.staff_padrao_veiculo = spv
                        staff_padrao.save()
                        logger.info("Alterando %s: %s -> %s", pessoa, anterior, spv)

                    else:
                        staff_padrao = StaffPadrao.objects.create(
                            pessoa=pessoa, staff_padrao_veiculo=spv
                        )
                        logger.info("Atribuindo %s -> %s", pessoa, spv)

            actions[f"add_spv_{spv.veiculo.id}"] = (
                add_to_spv,
                f"add_spv_{spv.veiculo.id}",
                f"Adicionar a {spv}",
            )

        return actions


admin.site.register(Pessoa, PessoaAdmin)
admin.site.register(PessoaStaff, StaffsAdmin)
admin.site.register(Grupo, GrupoAdmin)
admin.site.register(StaffPadraoVeiculo, StaffPadraoVeiculoAdmin)
admin.site.register(Veiculo, VeiculoAdmin)
admin.site.register(Desfile, DesfileAdmin)

admin.site.register(Traje, TrajeAdmin)
admin.site.register(TrajeInventario, TrajeInventarioAdmin)

admin.site.register(Convite, ConviteAdmin)
admin.site.register(InscricaoDesfile, InscricaoDesfileAdmin)


admin.site.site_title = "Planetapéia Desfiles"
admin.site.site_header = "Planetapéia Desfiles"

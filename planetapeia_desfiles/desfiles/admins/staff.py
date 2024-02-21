import logging

from django.contrib import admin
from django.db.models import Q
from django.forms.models import ModelMultipleChoiceField
from django.http.request import HttpRequest

from ..models import PessoaStaff, StaffPadrao, StaffPadraoVeiculo, TiposPessoasChoices


class StaffInline(admin.TabularInline):
    model = StaffPadrao
    extra = 0

    def get_formset(self, request, obj, **kwargs):
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

    def get_queryset(self, request: HttpRequest):
        queryset = (
            super().get_queryset(request).filter(~Q(tipo=TiposPessoasChoices.CONVIDADO))
        )
        return queryset

    def staff_padrao_veiculo(self, obj: PessoaStaff):
        if spv := obj.staff_padrao_veiculo:
            return f"{obj.nome} [{obj.get_tipo_display()} - {spv.veiculo}]"

    def get_actions(self, request: HttpRequest):
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

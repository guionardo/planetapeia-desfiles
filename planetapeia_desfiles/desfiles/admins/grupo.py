from django.contrib import admin
from django.db.models import Q
from django.http.request import HttpRequest

from ..models import Pessoa, TiposPessoasChoices


class GrupoAdmin(admin.ModelAdmin):
    def get_form(self, request: HttpRequest, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if field := form.base_fields.get("anfitrioes"):
            field.queryset = Pessoa.objects.filter(
                Q(grupo=obj) & ~Q(tipo=TiposPessoasChoices.CONVIDADO)
            )
        return form

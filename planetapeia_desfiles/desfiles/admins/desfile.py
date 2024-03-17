from django.contrib import admin
from django.contrib.auth.models import User
from django.http.request import HttpRequest

from ..models import Desfile
from ..services.date_time_provider import DateTimeProvider


class DesfileAdmin(admin.ModelAdmin):
    fields = [
        "nome",
        ("local", "data"),
        ("confirmado", "data_aprovacao", "aprovador"),
        "situacao",
        "veiculos",
    ]

    def get_fields(self, request: HttpRequest, obj):
        confirmado = []
        if obj and obj.confirmado:
            confirmado.extend(["data_aprovacao", "aprovador"])
        # confirmado.append("aprovador")
        fields = [
            "nome",
            ("local", "data"),
            "confirmado",
            confirmado,
            "situacao",
            "veiculos",
            "valor_taxa_traje",
        ]
        return fields

    def get_readonly_fields(self, request, obj: Desfile):
        if obj and obj.confirmado:
            return [
                "nome",
                "local",
                "data",
                "veiculos",
                "aprovador",
                "data_aprovacao",
                "valor_taxa_traje",
            ]
        return []

    def get_form(self, request: HttpRequest, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if field := form.base_fields.get("aprovador"):
            field.queryset = User.objects.filter(id=request.user.id)
        return form

    def save_model(self, request, obj: Desfile, form, change) -> None:
        if obj.confirmado and not obj.aprovador:
            obj.aprovador = request.user
            obj.data_aprovacao = DateTimeProvider.now()

        return super().save_model(request, obj, form, change)

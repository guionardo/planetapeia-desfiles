from django.contrib import admin


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

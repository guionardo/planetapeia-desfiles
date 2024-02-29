# Generated by Django 5.0.2 on 2024-02-29 04:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("desfiles", "0031_remove_pessoarevisarsenha_idx_guid_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="pessoarevisarsenha",
            options={
                "verbose_name": "Revisão de senha",
                "verbose_name_plural": "Revisões de senha",
            },
        ),
        migrations.AlterModelOptions(
            name="trajehistorico",
            options={
                "verbose_name": "Histórico do traje",
                "verbose_name_plural": "Históricos do traje",
            },
        ),
        migrations.AlterModelOptions(
            name="trajeinventario",
            options={
                "verbose_name": "Inventário",
                "verbose_name_plural": "Inventários",
            },
        ),
        migrations.AddField(
            model_name="trajeinventario",
            name="pessoa",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="desfiles.pessoa",
                verbose_name="Pessoa",
            ),
        ),
        migrations.AddField(
            model_name="trajeinventario",
            name="usuario",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Responsável",
            ),
        ),
        migrations.AlterField(
            model_name="trajehistorico",
            name="movimento",
            field=models.CharField(
                choices=[
                    ("E", "Entrada"),
                    ("B", "Empréstimo"),
                    ("D", "Devolução"),
                    ("M", "Manutenção"),
                    ("X", "Descarte"),
                    ("x", "Extravio"),
                ],
                max_length=1,
                verbose_name="Movimento",
            ),
        ),
        migrations.AlterField(
            model_name="trajehistorico",
            name="pessoa",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="desfiles.pessoa",
                verbose_name="Pessoa atual",
            ),
        ),
        migrations.AlterField(
            model_name="trajehistorico",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Responsável atual",
            ),
        ),
        migrations.AlterField(
            model_name="trajeinventario",
            name="situacao",
            field=models.CharField(
                choices=[
                    ("D", "Disponível"),
                    ("E", "Emprestado"),
                    ("M", "Em Manutenção"),
                    ("X", "Descartado"),
                    ("x", "Extraviado"),
                ],
                max_length=1,
                verbose_name="Situação",
            ),
        ),
    ]

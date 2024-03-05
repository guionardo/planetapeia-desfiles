# Generated by Django 5.0.2 on 2024-03-04 12:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("desfiles", "0035_traje_campos_checklist"),
    ]

    operations = [
        migrations.CreateModel(
            name="TrajeHistoricoChecklistItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("item", models.CharField(max_length=40, verbose_name="Item")),
                ("checado", models.BooleanField(default=False, verbose_name="Checado")),
                (
                    "historico",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="desfiles.trajehistorico",
                        verbose_name="Histórico",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="trajehistorico",
            name="checagem",
            field=models.ManyToManyField(
                to="desfiles.trajehistoricochecklistitem", verbose_name="Checagem"
            ),
        ),
    ]

# Generated by Django 5.0.2 on 2024-02-09 19:38

import datetime
import desfiles.models_utils
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("desfiles", "0008_alter_trajetaxa_traje"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Convite",
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
                (
                    "valido_ate",
                    models.DateField(
                        default=datetime.date(1, 1, 1), verbose_name="Válido até"
                    ),
                ),
                (
                    "data",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criação"),
                ),
                (
                    "max_convidados",
                    models.PositiveSmallIntegerField(
                        default=20, verbose_name="Máximo de convidados"
                    ),
                ),
                (
                    "hash",
                    models.CharField(
                        default=desfiles.models_utils.convite_hash,
                        editable=False,
                        max_length=8,
                        verbose_name="Hash",
                    ),
                ),
                (
                    "desfile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="desfiles.desfile",
                        verbose_name="Desfile",
                    ),
                ),
                (
                    "grupo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="desfiles.grupo",
                        verbose_name="Grupo",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Responsável",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="inscricaodesfile",
            name="convite",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="desfiles.convite",
                verbose_name="Convite",
            ),
        ),
    ]

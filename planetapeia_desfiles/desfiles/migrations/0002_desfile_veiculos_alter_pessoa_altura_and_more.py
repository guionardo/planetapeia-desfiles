# Generated by Django 5.0.2 on 2024-02-08 19:54

import desfiles.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("desfiles", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="desfile",
            name="veiculos",
            field=models.ManyToManyField(to="desfiles.veiculo"),
        ),
        migrations.AlterField(
            model_name="pessoa",
            name="altura",
            field=models.IntegerField(
                validators=[
                    django.core.validators.MinValueValidator(30, "Altura mínima 30"),
                    django.core.validators.MaxValueValidator(220, "Altura máxima 220"),
                ],
                verbose_name="Altura (cm)",
            ),
        ),
        migrations.AlterField(
            model_name="pessoa",
            name="cpf",
            field=models.CharField(
                max_length=11,
                primary_key=True,
                serialize=False,
                validators=[desfiles.models.cpf_validator],
                verbose_name="CPF",
            ),
        ),
        migrations.AlterField(
            model_name="pessoa",
            name="data_nascimento",
            field=models.DateField(
                validators=[desfiles.models.data_nascimento_validator],
                verbose_name="Data de Nascimento",
            ),
        ),
        migrations.AlterField(
            model_name="veiculo",
            name="capacidade",
            field=models.IntegerField(
                help_text="Capacidade todal de pessoas",
                validators=[
                    django.core.validators.MinValueValidator(1, "Capacidade mínima"),
                    django.core.validators.MaxValueValidator(99, "Capacidade máxima"),
                ],
                verbose_name="Capacidade",
            ),
        ),
        migrations.AlterField(
            model_name="veiculo",
            name="imagem",
            field=models.ImageField(
                help_text="Logotipo para ser usada nos relatórios",
                upload_to=desfiles.models.upload_to,
                verbose_name="Imagem",
            ),
        ),
        migrations.AlterField(
            model_name="veiculo",
            name="peso_individual_max",
            field=models.IntegerField(
                default=130, help_text="kg", verbose_name="Peso individual máximo"
            ),
        ),
        migrations.AlterField(
            model_name="veiculo",
            name="peso_total_max",
            field=models.IntegerField(
                default=0, help_text="kg", verbose_name="Peso total máximo"
            ),
        ),
    ]

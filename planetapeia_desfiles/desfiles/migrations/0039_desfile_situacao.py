# Generated by Django 5.0.2 on 2024-03-09 01:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("desfiles", "0038_pessoa_nome_busca"),
    ]

    operations = [
        migrations.AddField(
            model_name="desfile",
            name="situacao",
            field=models.CharField(
                choices=[
                    ("A", "Aberto"),
                    ("C", "Confirmado"),
                    ("X", "Cancelado"),
                    ("T", "Terminado"),
                ],
                default="A",
                max_length=1,
                verbose_name="Situação",
            ),
        ),
    ]
# Generated by Django 5.0.2 on 2024-02-08 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("desfiles", "0002_desfile_veiculos_alter_pessoa_altura_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="desfile",
            name="confirmado",
            field=models.BooleanField(
                default=False,
                help_text="Desfiles confirmados não podem ter seus dados alterados",
                verbose_name="Confirmado",
            ),
        ),
    ]

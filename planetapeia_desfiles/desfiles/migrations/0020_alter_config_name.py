# Generated by Django 5.0.2 on 2024-02-18 12:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("desfiles", "0019_config"),
    ]

    operations = [
        migrations.AlterField(
            model_name="config",
            name="name",
            field=models.CharField(
                choices=[("pes.cad.hab", "Cadastro de pessoas habilitado")],
                max_length=20,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
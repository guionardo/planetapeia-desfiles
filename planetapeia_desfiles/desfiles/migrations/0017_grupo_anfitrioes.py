# Generated by Django 5.0.2 on 2024-02-16 20:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("desfiles", "0016_pessoa_foto"),
    ]

    operations = [
        migrations.AddField(
            model_name="grupo",
            name="anfitrioes",
            field=models.ManyToManyField(
                related_name="grupo_anfitriao",
                to="desfiles.pessoa",
                verbose_name="Anfitriões",
            ),
        ),
    ]
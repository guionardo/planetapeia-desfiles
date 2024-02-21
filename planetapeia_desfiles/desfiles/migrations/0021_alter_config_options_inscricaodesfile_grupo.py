# Generated by Django 5.0.2 on 2024-02-18 14:12

import django.db.models.deletion
from django.db import migrations, models


def fix_inscricao_desfile_grupo(apps, schema_editor):
    InscricaoDesfile = apps.get_model("desfiles", "InscricaoDesfile")
    for inscricao in InscricaoDesfile.objects.filter(grupo=None):
        inscricao.grupo = inscricao.convite.grupo
        inscricao.save()


class Migration(migrations.Migration):
    dependencies = [
        ("desfiles", "0020_alter_config_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="config",
            options={
                "verbose_name": "Configuração",
                "verbose_name_plural": "Configurações",
            },
        ),
        migrations.AddField(
            model_name="inscricaodesfile",
            name="grupo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="desfiles.grupo",
                verbose_name="Grupo",
            ),
        ),
        migrations.RunPython(fix_inscricao_desfile_grupo, migrations.RunPython.noop),
    ]

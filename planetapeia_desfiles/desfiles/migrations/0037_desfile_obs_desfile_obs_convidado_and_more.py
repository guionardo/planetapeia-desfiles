# Generated by Django 5.0.2 on 2024-03-05 04:16

from django.db import migrations, models


def fix_desfile_data(apps, schema_editor):
    InscricaoDesfile = apps.get_model("desfiles", "InscricaoDesfile")
    for inscricao in InscricaoDesfile.objects.filter(grupo=None):
        inscricao.data_desfile = inscricao.desfile.data if inscricao.desfile else None
        inscricao.save()


class Migration(migrations.Migration):
    dependencies = [
        ("desfiles", "0036_trajehistoricochecklistitem_trajehistorico_checagem"),
    ]

    operations = [
        migrations.AddField(
            model_name="desfile",
            name="obs",
            field=models.TextField(
                default="",
                help_text="Observações internas do desfile",
                max_length=512,
                verbose_name="Observações",
            ),
        ),
        migrations.AddField(
            model_name="desfile",
            name="obs_convidado",
            field=models.TextField(
                default="",
                help_text="Observações que serão adicionadas ao convite e mostradas no painel do convidado",
                max_length=512,
                verbose_name="Observações para o convidado",
            ),
        ),
        migrations.AddField(
            model_name="inscricaodesfile",
            name="data_desfile",
            field=models.DateField(
                blank=True, null=True, verbose_name="Data do desfile"
            ),
        ),
        migrations.RunPython(fix_desfile_data, migrations.RunPython.noop),
    ]
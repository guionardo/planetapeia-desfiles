# Generated by Django 5.0.2 on 2024-02-18 15:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("desfiles", "0022_usermessage"),
    ]

    operations = [
        migrations.AddField(
            model_name="usermessage",
            name="title",
            field=models.CharField(default="", max_length=40, verbose_name="Título"),
            preserve_default=False,
        ),
    ]
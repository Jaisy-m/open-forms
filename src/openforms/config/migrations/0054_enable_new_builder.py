# Generated by Django 3.2.23 on 2024-01-26 09:24

from django.db import migrations


def enable_new_builder(apps, _):
    GlobalConfiguration = apps.get_model("config", "GlobalConfiguration")
    # there can only ever be one record
    config = GlobalConfiguration.objects.first()
    if config is None or config.enable_react_formio_builder:
        return

    config.enable_react_formio_builder = True
    config.save()


class Migration(migrations.Migration):

    dependencies = [
        ("config", "0001_initial_to_v250"),
    ]

    operations = [
        migrations.RunPython(enable_new_builder, migrations.RunPython.noop),
    ]

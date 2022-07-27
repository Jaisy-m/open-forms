# Generated by Django 3.2.14 on 2022-07-26 11:51

from django.db import migrations, models


def remove_static_form_variables(apps, schema_editor):
    FormVariable = apps.get_model("forms", "FormVariable")

    FormVariable.objects.filter(source="static").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("forms", "0035_auto_20220725_0918"),
    ]

    operations = [
        migrations.RunPython(remove_static_form_variables, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="formvariable",
            name="source",
            field=models.CharField(
                choices=[("component", "Component"), ("user_defined", "User defined")],
                help_text="Where will the data that will be associated with this variable come from",
                max_length=50,
                verbose_name="source",
            ),
        ),
    ]

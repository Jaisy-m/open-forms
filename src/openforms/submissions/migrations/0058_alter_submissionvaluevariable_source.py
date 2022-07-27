# Generated by Django 3.2.14 on 2022-07-26 11:51

from django.db import migrations, models


def remove_static_submission_variables(apps, schema_editor):
    SubmissionValueVariable = apps.get_model("submissions", "SubmissionValueVariable")

    SubmissionValueVariable.objects.filter(source="static").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("submissions", "0057_alter_submissionvaluevariable_key"),
    ]

    operations = [
        migrations.RunPython(
            remove_static_submission_variables, migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name="submissionvaluevariable",
            name="source",
            field=models.CharField(
                choices=[
                    ("sensitive_data_cleaner", "Sensitive data cleaner"),
                    ("user_input", "User input"),
                    ("prefill", "Prefill"),
                    ("logic", "Logic"),
                    ("dmn", "DMN"),
                ],
                help_text="Where variable value came from",
                max_length=50,
                verbose_name="source",
            ),
        ),
    ]

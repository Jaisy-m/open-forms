# Generated by Django 4.2.11 on 2024-04-16 12:59

from django.db import migrations
import re

from openforms.formio.migration_converters import (
    convert_simple_conditionals,
)


def fix_forms_simple_conditionals(apps, schema_editor):
    FormDefinition = apps.get_model("forms", "FormDefinition")

    all_definitions = FormDefinition.objects.all()
    if not len(all_definitions):
        return

    # Check for simple conditionals where the "when" is not an empty string
    raw_pattern = r'"conditional": \{[\w\s",:]*"when": "(\w+)"[\w\s",:]*\}'
    pattern = re.compile(raw_pattern)

    definitions_to_update = []
    for definition in all_definitions:
        config_modified = convert_simple_conditionals(
            definition.configuration, pattern=pattern
        )

        if config_modified:
            definitions_to_update.append(definition)

    FormDefinition.objects.bulk_update(definitions_to_update, fields=["configuration"])


class Migration(migrations.Migration):

    dependencies = [
        ("forms", "0096_fix_invalid_validate_configuration"),
    ]

    operations = [
        migrations.RunPython(fix_forms_simple_conditionals, migrations.RunPython.noop),
    ]

# Generated by Django 4.2.10 on 2024-03-06 14:38
from typing import TypedDict

from django.db import migrations
from django.db.models import QuerySet

from openforms.variables.models import ServiceFetchConfiguration

from ..models import FormLogic, FormVariable
from ..constants import LogicActionTypes


class UpdatedObjects(TypedDict):
    rules: list[FormLogic]
    variables: list[FormVariable]


def convert_to_new_service_fetch_format(
    rules: list[FormLogic],
    available_service_fetch_configs: QuerySet[ServiceFetchConfiguration],
) -> UpdatedObjects:
    updated_rules = []
    updated_variables = []
    for rule in rules:
        rule_updated = False
        for action in rule.actions:
            if action["action"]["type"] != LogicActionTypes.fetch_from_service:
                continue

            if (service_fetch_config_pk := str(action["action"]["value"])) == "":
                continue

            action["action"]["value"] = ""
            rule_updated = True
            if not (
                service_fetch_config := available_service_fetch_configs.filter(
                    pk=service_fetch_config_pk
                ).first()
            ):
                # Case in which the configuration is broken: the rule points to a non-existing service fetch config.
                # We just empty the value and do nothing with the value it contained.
                continue

            variable = rule.form.formvariable_set.filter(key=action["variable"]).first()
            if not variable:
                # Another case of broken configuration.
                # The variable does not exist, so we can't update its configuration for service fetch.
                continue

            variable.service_fetch_configuration = service_fetch_config
            updated_variables.append(variable)

        if rule_updated:
            updated_rules.append(rule)

    return UpdatedObjects(rules=updated_rules, variables=updated_variables)


def update_logic_rules(apps, schema_editor):
    FormLogic = apps.get_model("forms", "FormLogic")
    FormVariable = apps.get_model("forms", "FormVariable")
    ServiceFetchConfiguration = apps.get_model("variables", "ServiceFetchConfiguration")

    available_configurations = ServiceFetchConfiguration.objects.all()
    rules = FormLogic.objects.all()

    updated_objects = convert_to_new_service_fetch_format(
        rules, available_configurations
    )

    FormLogic.objects.bulk_update(updated_objects["rules"], fields=["actions"])
    FormVariable.objects.bulk_update(
        updated_objects["variables"], fields=["service_fetch_configuration"]
    )


class Migration(migrations.Migration):

    dependencies = [
        ("forms", "0093_fix_prefill_bis"),
        ("variables", "0012_servicefetchconfiguration_cache_timeout"),
    ]

    operations = [
        migrations.RunPython(
            update_logic_rules,
            migrations.RunPython.noop,
        )
    ]

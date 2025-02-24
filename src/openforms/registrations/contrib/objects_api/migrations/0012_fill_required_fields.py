# Generated by Django 3.2.24 on 2024-02-12 16:47

from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import StateApps

from openforms.registrations.contrib.objects_api.plugin import (
    PLUGIN_IDENTIFIER as OBJECTS_API_PLUGIN_IDENTIFIER,
)


def fill_objects_api_registration_backend_required_fields(
    apps: StateApps, schema_editor: BaseDatabaseSchemaEditor
) -> None:
    """Explicitly use the globally configured ProductAanvraag objecttype and version for forms relying on the default."""

    ObjectsAPIConfig = apps.get_model("registrations_objects_api", "ObjectsAPIConfig")

    try:
        objects_api_config = ObjectsAPIConfig.objects.get()
    except ObjectsAPIConfig.DoesNotExist:
        return

    objecttype_url = objects_api_config.objecttype
    objecttype_version = objects_api_config.objecttype_version

    if not (objecttype_url and objecttype_version):
        return

    FormRegistrationBackend = apps.get_model("forms", "FormRegistrationBackend")

    for form_registration_backend in FormRegistrationBackend.objects.filter(
        backend=OBJECTS_API_PLUGIN_IDENTIFIER
    ).iterator():
        form_registration_backend.options.setdefault("objecttype", objecttype_url)
        form_registration_backend.options.setdefault(
            "objecttype_version", objecttype_version
        )
        form_registration_backend.save()


class Migration(migrations.Migration):

    dependencies = [
        ("registrations_objects_api", "0011_create_objecttypesypes_service_from_url"),
        ("forms", "0001_initial_to_v250"),
    ]

    operations = [
        migrations.RunPython(
            fill_objects_api_registration_backend_required_fields,
            migrations.RunPython.noop,
        ),
    ]

# Generated by Django 3.2.15 on 2022-08-12 12:15

from django.db import migrations
from django.db.models import Q

from ..constants import AuthAttribute

REGISTER = {
    "digid": AuthAttribute.bsn,
    "eherkenning": AuthAttribute.kvk,
    "eidas": AuthAttribute.pseudo,
    "digid_oidc": AuthAttribute.bsn,
    "digid_machtigen_oidc": AuthAttribute.bsn,
    "eherkenning_oidc": AuthAttribute.kvk,
    "eherkenning_bewindvoering_oidc": AuthAttribute.kvk,
    # demo/test plugins
    "demo": AuthAttribute.bsn,
    "demo-kvk": AuthAttribute.kvk,
    "demo-outage": AuthAttribute.bsn,
    "bsn-outage": AuthAttribute.bsn,
    "kvk-outage": AuthAttribute.kvk,
    "digid-mock": AuthAttribute.bsn,
}


def forward(apps, schema_editor):
    AuthInfo = apps.get_model("of_authentication", "AuthInfo")
    Submission = apps.get_model("submissions", "Submission")

    submissions = Submission.objects.filter(~Q(auth_plugin=""))

    auth_info_to_create = []
    for submission in submissions:
        if hasattr(submission, "auth_info"):
            continue

        plugin = submission.auth_plugin
        attribute = REGISTER[plugin]
        value = getattr(submission, attribute)

        auth_info_to_create.append(
            AuthInfo(
                attribute=attribute,
                value=value,
                plugin=plugin,
                attribute_hashed=submission.auth_attributes_hashed,
                submission=submission,
            )
        )

    AuthInfo.objects.bulk_create(auth_info_to_create)


def backwards(apps, schema_editor):
    AuthInfo = apps.get_model("of_authentication", "AuthInfo")
    Submission = apps.get_model("submissions", "Submission")

    auth_infos = AuthInfo.objects.all()

    submissions_to_update = []
    for auth_info in auth_infos:
        if auth_info.attribute not in ["kvk", "bsn", "pseudo"]:
            continue

        submission = auth_info.submission
        setattr(submission, auth_info.attribute, auth_info.value)
        submission.auth_attributes_hashed = auth_info.attribute_hashed
        submission.auth_plugin = auth_info.plugin
        submissions_to_update.append(submission)

    Submission.objects.bulk_update(
        submissions_to_update,
        fields=["bsn", "kvk", "pseudo", "auth_attributes_hashed", "auth_plugin"],
    )


class Migration(migrations.Migration):

    run_before = [
        ("submissions", "0060_auto_20220812_1439"),
    ]

    dependencies = [
        ("of_authentication", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(forward, backwards),
    ]

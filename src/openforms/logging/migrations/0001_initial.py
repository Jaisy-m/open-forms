# Generated by Django 2.2.24 on 2021-09-20 09:32

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("timeline_logger", "0004_alter_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="TimelineLogProxy",
            fields=[],
            options={
                "verbose_name": "timeline log entry",
                "verbose_name_plural": "timeline log entries",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("timeline_logger.timelinelog",),
        ),
    ]

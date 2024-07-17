from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OpenAfspraakPluginConfig(AppConfig):
    name = "openforms.appointments.contrib.openafspraak"
    verbose_name = _("OpenAfspraak appointment plugin")

    def ready(self):
        from . import plugin  # noqa

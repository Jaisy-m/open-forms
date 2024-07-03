from django.db import models
from django.utils.translation import gettext_lazy as _

from django_jsonform.models.fields import ArrayField
from solo.models import SingletonModel
from zgw_consumers.constants import APITypes

from .constants import CustomerFields


class OpenAfspraakConfigManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("service")


def get_default_customer_fields() -> list[CustomerFields]:
    return [
        CustomerFields.first_name,
        CustomerFields.last_name,
        CustomerFields.email,
    ]


class OpenAfspraakConfig(SingletonModel):
    """
    Global configuration and defaults
    """

    service = models.OneToOneField(
        "zgw_consumers.Service",
        verbose_name=_("Calendar API"),
        on_delete=models.PROTECT,
        limit_choices_to={"api_type": APITypes.orc},
        related_name="+",
        null=True,
        help_text=_(
            "The OpenAfspraak API. " "Example: https://example.com:8443/api/v1/"
        ),
    )
    required_customer_fields = ArrayField(
        models.CharField(max_length=50, choices=CustomerFields.choices),
        verbose_name=_("Required customer fields"),
        help_text=_(
            "Select the customer fields for the contact details step. "
            "Fields that you select here are REQUIRED fields for the user making the "
            "appointment. You must have at least one field to be able to identify "
            "the customer."
        ),
        default=get_default_customer_fields,
        blank=False,
    )

    objects = OpenAfspraakConfigManager()

    class Meta:
        verbose_name = _("OpenAfspraak configuration")

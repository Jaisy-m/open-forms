from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from openforms.formio.typing import Component


class CustomerFields(TextChoices):
    """
    Enum of possible customer field names offered by OpenAfspraak.

    Documentation reference: "Book an appointment for a selected branch, service, date
    and time" and the "Customer" data model.

    note:: first_name, last_name and email are always required fields.

    The enum values are the fields as they go in the customer record.
    """

    public_id = "public_id", _("Public ID")  # uuid
    first_name = "firstName", _("First name")  # string, max length 100
    last_name = "lastName", _("Last name")  # string, max length 100
    email = "email", _("Email address")  # string, max length 255
    phone = "phone", _("Phone number")  # string, max length 20
    street_name = "street name", _("Street name")  # string, max length 100
    house_number = "houseNumber", _("House number")  # string, max length 255
    city = "city", _("City")  # string, max length 255
    postal_code = "postalCode", _("Postal code")  # string, max length 255
    birthday = "dateOfBirth", _("Birthday")


FIELD_TO_FORMIO_COMPONENT: dict[str, Component] = {
    CustomerFields.first_name: {
        "type": "textfield",
        "key": CustomerFields.first_name.value,
        "label": CustomerFields.first_name.label,
        "autocomplete": "given-name",
        "validate": {
            "required": True,
            "maxLength": 200,
        },
    },
    CustomerFields.last_name: {
        "type": "textfield",
        "key": CustomerFields.last_name.value,
        "label": CustomerFields.last_name.label,
        "autocomplete": "family-name",
        "validate": {
            "required": True,
            "maxLength": 200,
        },
    },
    CustomerFields.email: {
        "type": "email",
        "key": CustomerFields.email.value,
        "label": CustomerFields.email.label,
        "autocomplete": "email",
        "validate": {
            "required": True,
            "maxLength": 255,
        },
    },
    CustomerFields.phone: {
        "type": "phoneNumber",
        "key": CustomerFields.phone.value,
        "label": CustomerFields.phone.label,
        "autocomplete": "tel",
        "validate": {
            "required": True,
            "maxLength": 50,
        },
    },
    CustomerFields.street_name: {
        "type": "textfield",
        "key": CustomerFields.street_name.value,
        "label": CustomerFields.street_name.label,
        "autocomplete": "address-line1",
        "validate": {
            "required": True,
            "maxLength": 255,
        },
    },
    CustomerFields.house_number: {
        "type": "textfield",
        "key": CustomerFields.house_number.value,
        "label": CustomerFields.house_number.label,
        "autocomplete": "address-line2",
        "validate": {
            "required": True,
            "maxLength": 255,
        },
    },
    CustomerFields.city: {
        "type": "textfield",
        "key": CustomerFields.city.value,
        "label": CustomerFields.city.label,
        "autocomplete": "address-line2",
        "validate": {
            "required": True,
            "maxLength": 255,
        },
    },
    CustomerFields.postal_code: {
        "type": "textfield",
        "key": CustomerFields.postal_code.value,
        "label": CustomerFields.postal_code.label,
        "autocomplete": "address-level1",
        "validate": {
            "required": True,
            "maxLength": 255,
        },
    },
    CustomerFields.birthday: {
        "type": "date",
        "key": CustomerFields.birthday.value,
        "label": CustomerFields.birthday.label,
        "autocomplete": "bday",
        "validate": {
            "required": True,
        },
        "openForms": {
            "widget": "inputGroup",
        },
    },
}


# sanity check
for member in CustomerFields.values:
    if member == CustomerFields.public_id:
        continue
    assert (
        member in FIELD_TO_FORMIO_COMPONENT
    ), f"Missing field '{member}' in FIELD_TO_FORMIO_COMPONENT mapping"

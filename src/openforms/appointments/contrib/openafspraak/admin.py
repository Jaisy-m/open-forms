from django import forms
from django.contrib import admin

from solo.admin import SingletonModelAdmin

from openforms.utils.form_fields import (
    CheckboxChoicesArrayField,
    get_arrayfield_choices,
)

from .models import OpenAfspraakConfig


class RequiredCustomerFieldsField(CheckboxChoicesArrayField):
    @staticmethod
    def get_field_choices():
        return get_arrayfield_choices(OpenAfspraakConfig, "required_customer_fields")


class OpenAfspraakConfigForm(forms.ModelForm):
    class Meta:
        model = OpenAfspraakConfig
        fields = "__all__"
        field_classes = {
            "required_customer_fields": RequiredCustomerFieldsField,
        }


@admin.register(OpenAfspraakConfig)
class OpenAfspraakConfigAdmin(SingletonModelAdmin):
    form = OpenAfspraakConfigForm

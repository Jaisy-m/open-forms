from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypeAlias, TypedDict
from uuid import UUID

from typing_extensions import Required

ConfigVersion: TypeAlias = Literal[1, 2]

if TYPE_CHECKING:
    from .models import ObjectsAPIGroupConfig


class _BaseRegistrationOptions(TypedDict, total=False):
    objects_api_group: Required[ObjectsAPIGroupConfig]
    objecttype: Required[UUID]
    objecttype_version: Required[int]
    informatieobjecttype_submission_report: str
    upload_submission_csv: bool
    informatieobjecttype_submission_csv: str
    informatieobjecttype_attachment: str
    organisatie_rsin: str


class RegistrationOptionsV1(_BaseRegistrationOptions, total=False):
    version: Required[Literal[1]]
    productaanvraag_type: str
    content_json: str
    payment_status_update_json: str


class ObjecttypeVariableMapping(TypedDict):
    variable_key: str
    target_path: list[str]


class RegistrationOptionsV2(_BaseRegistrationOptions, total=False):
    version: Required[Literal[2]]
    variables_mapping: Required[list[ObjecttypeVariableMapping]]
    geometry_variable_key: str


RegistrationOptions: TypeAlias = RegistrationOptionsV1 | RegistrationOptionsV2
"""The Objects API registration options (either V1 or V2)."""

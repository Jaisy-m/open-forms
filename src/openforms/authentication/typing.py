from typing import TypedDict

from typing_extensions import NotRequired

from openforms.typing import JSONObject

from .constants import AuthAttribute


class BaseAuth(TypedDict):
    """The base structure of authentication data."""

    plugin: str
    """The unique identifier of the plugin that inititiated the authentication data."""

    attribute: AuthAttribute
    value: str


class FormAuth(BaseAuth):
    loa: NotRequired[str]
    acting_subject_identifier_type: NotRequired[str]
    acting_subject_identifier_value: NotRequired[str]
    legal_subject_identifier_type: NotRequired[str]
    legal_subject_identifier_value: NotRequired[str]
    mandate_context: NotRequired[JSONObject]

    # deprecated
    machtigen: NotRequired[dict | None]

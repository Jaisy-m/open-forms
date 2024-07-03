from datetime import date, datetime
from typing import TypedDict

from ape_pie.client import APIClient
from zgw_consumers.client import build_client
from zgw_consumers.models import Service

from .exceptions import OpenAfspraakException
from .models import OpenAfspraakConfig

# API DATA DEFINITIONS


class ServiceDict(TypedDict):
    publicId: str
    name: str
    # could be float too in theory, documentation is not specific (it gives an int example)
    duration: int
    additionalCustomerDuration: int
    custom: str | None


class FullServiceDict(ServiceDict):
    active: bool
    publicEnabled: bool
    created: int
    updated: int


class ServiceGroupDict(TypedDict):
    services: list[ServiceDict]


class BranchDict(TypedDict):
    branchPublicId: str
    branchName: str
    serviceGroups: list[ServiceGroupDict]


class BranchDetailDict(TypedDict):
    name: str
    publicId: str
    phone: str
    email: str
    branchPrefix: str | None

    addressLine1: str | None
    addressLine2: str | None
    addressZip: str | None
    addressCity: str | None
    addressState: str | None
    addressCountry: str | None

    latitude: float | None
    longitude: float | None
    timeZone: str
    fullTimeZone: str
    custom: str | None
    created: int
    updated: int


class NoServiceConfigured(RuntimeError):
    pass


# API CLIENT IMPLEMENTATIONS, per major version of the API


def OpenAfspraakClient() -> "Client":
    """
    Create a Qmatic client instance from the database configuration.
    """
    config = OpenAfspraakConfig.get_solo()
    assert isinstance(config, OpenAfspraakConfig)
    if (service := config.service) is None:
        raise NoServiceConfigured("No OpenAfspraak service defined, aborting!")
    assert isinstance(service, Service)
    return build_client(service, client_factory=Client)


class Client(APIClient):
    """
    Client implementation for OpenAfspraak.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers["Content-Type"] = "application/json"

    def request(self, method: str, url: str, *args, **kwargs):
        # ensure there is a version identifier in the URL
        response = super().request(method, url, *args, **kwargs)

        if response.status_code == 500:
            error_msg = response.headers.get(
                "error_message", response.content.decode("utf-8")
            )
            raise OpenAfspraakException(
                f"Server error (HTTP {response.status_code}): {error_msg}"
            )

        return response

    def list_products(self) -> list[FullServiceDict]:
        pass

    def list_product_locations(
        self, service_ids: list[str], location_id: str = ""
    ) -> list[ServiceGroupDict]:
        pass

    def list_dates(self, location_id: str, product_id: str) -> list[date]:
        """
        Get list of available dates for multiple services and customers.

        ``num_customers`` is the total number of customers, which affects the
        appointment duration in Qmatic (using
        ``duration + additionalCustomerDuration * numAdditionalCustomers``, where
        ``numAdditionalCustomers`` is ``numCustomers - 1``.
        ).

        Note that Qmatic returns a list of datetimes without timezone information.
        """
        pass

    def list_times(
        self, location_id: str, product_id: str, day: date
    ) -> list[datetime]:
        """
        Get list of available times for multiple services and customers.

        ``num_customers`` is the total number of customers, which affects the
        appointment duration in Qmatic (using
        ``duration + additionalCustomerDuration * numAdditionalCustomers``, where
        ``numAdditionalCustomers`` is ``numCustomers - 1``.
        ).

        Note that Qmatic returns a list of datetimes without timezone information.
        """
        pass

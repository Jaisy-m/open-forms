from datetime import date, datetime
from typing import TypedDict

from ape_pie.client import APIClient
from zgw_consumers.client import build_client
from zgw_consumers.models import Service

from .exceptions import OpenAfspraakException
from .models import OpenAfspraakConfig


class ProductDict(TypedDict):
    public_id: str
    name: str
    description: str
    appointment_duration: str
    price: float


class LocationDict(TypedDict):
    public_id: str
    name: str
    address: str
    city: str
    postal_code: str


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

    def list_products(self) -> list[ProductDict]:
        endpoint = "products"
        response = self.get(endpoint)
        response.raise_for_status()
        return response.json()

    def list_product_locations(self, product_id: str = "") -> list[LocationDict]:
        assert product_id, "Unexpectedly received empty product ID"

        endpoint = f"products/{product_id}/locations"
        response = self.get(endpoint)
        response.raise_for_status()
        return response.json()

    def list_dates(self, location_id: str, product_id: str) -> list[date]:
        """
        Get list of available dates for a product and location.
        """
        assert location_id, "Unexpectedly received empty location ID"
        assert product_id, "Unexpectedly received empty product ID"

        endpoint = "dates"
        response = self.get(
            endpoint,
            params={
                "location_id": location_id,
                "product_id": product_id,
            },
        )
        response.raise_for_status()
        return [date.fromisoformat(entry["date"]) for entry in response.json()]

    def list_times(
        self, location_id: str, product_id: str, day: date
    ) -> list[datetime]:
        """
        Get list of available times for multiple services and customers.
        """
        assert location_id, "Unexpectedly received empty location ID"
        assert product_id, "Unexpectedly received empty product ID"

        endpoint = "timeslots"
        response = self.get(
            endpoint,
            params={
                "location_id": location_id,
                "product_id": product_id,
                "date": day.isoformat(),
            },
        )
        response.raise_for_status()

        date_format = "%Y-%m-%dT%H:%M:%S%z"

        return [
            datetime.strptime(entry["start_time"], date_format)
            for entry in response.json()
        ]

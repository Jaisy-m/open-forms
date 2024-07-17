import logging
import warnings
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from requests.exceptions import RequestException

from openforms.formio.typing import Component
from openforms.plugins.exceptions import InvalidPluginConfiguration

from ...base import (
    AppointmentDetails,
    BasePlugin,
    Customer,
    CustomerDetails,
    Location,
    Product,
)
from ...exceptions import AppointmentCreateFailed
from ...registry import register
from .client import OpenAfspraakClient, ProductDict
from .constants import FIELD_TO_FORMIO_COMPONENT, CustomerFields
from .exceptions import GracefulOpenAfspraakException, OpenAfspraakException
from .models import OpenAfspraakConfig

logger = logging.getLogger(__name__)

_CustomerDetails = CustomerDetails[CustomerFields]


@contextmanager
def log_api_errors(template: str, *args):
    try:
        yield
    except (OpenAfspraakException, RequestException) as e:
        logger.exception(template, *args, exc_info=e)
        raise GracefulOpenAfspraakException("API call failed") from e
    except Exception as exc:
        raise OpenAfspraakException from exc


Param = ParamSpec("Param")
T = TypeVar("T")
FuncT = Callable[Param, T]


def with_graceful_default(default: T):
    def decorator(func: FuncT) -> FuncT:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except GracefulOpenAfspraakException:
                return default

        return wrapper

    return decorator


def normalize_customer_details(client: _CustomerDetails | Customer) -> _CustomerDetails:
    # Phasing out Customer in favour of CustomerDetails, so convert to the new type
    if isinstance(client, Customer):
        warnings.warn(
            "Fixed customer fields via the Customer class are deprecated, use "
            "dynamic CustomerDetails with 'get_required_customer_fields' instead.",
            DeprecationWarning,
        )
        client = _CustomerDetails(
            details={
                CustomerFields.last_name: client.last_name,
                CustomerFields.first_name: client.initials or "",
            }
        )
    return client


def parse_product(product: ProductDict) -> Product:
    """
    Parse the product data from the API into a Product object.
    Since the duration is given as 00:00:00, we need to parse it into a timedelta.
    """
    try:
        hours, minutes, seconds = product["appointment_duration"].split(":")
        duration = timedelta(
            hours=int(hours), minutes=int(minutes), seconds=int(seconds)
        )
    except ValueError:
        raise OpenAfspraakException(
            "Invalid time format for duration field: %s"
            % product["appointment_duration"]
        )

    return Product(
        product["public_id"],
        product["name"],
        duration=duration,
    )


@register("openafspraak")
class OpenAfspraakAppointment(BasePlugin[CustomerFields]):
    """
    Plugin for OpenAfspraak API (july 2024)
    """

    verbose_name = _("OpenAfspraak")
    # See "Book an appointment for multiple customers and multiple services" in the
    # documentation.
    supports_multiple_products = False

    @staticmethod
    def _count_products(products: list[Product]) -> tuple[list[str], int]:
        pass

    @with_graceful_default(default=[])
    def get_available_products(
        self,
        current_products: list[Product] | None = None,
        location_id: str = "",
    ) -> list[Product]:
        """
        Retrieve all available products to create an appointment for.

        OpenAfspraak has a endpoint that returns all available products. The response
        contains all the information needed.
        """

        client = OpenAfspraakClient()

        with log_api_errors("Could not retrieve products"):
            products = client.list_products()

        appointment_products = []  # type: list[Product]

        for product in products:
            appointment_products.append(parse_product(product))

        return appointment_products

    @with_graceful_default(default=[])
    def get_locations(
        self,
        products: list[Product] | None = None,
    ) -> list[Location]:
        """
        Retrieve all available locations.

        Obtaining all the locations without a product ID is not yet supported by the
        API. Since this is only used for the initial setup of the plugin, we can safely
        ignore this for now.
        """
        # assert products, "Location retrieval without products is not supported."

        if products is None or len(products) > 1:
            raise GracefulOpenAfspraakException(
                "Multiple products are not supported by the OpenAfspraak API, only "
                "the first product is used."
            )

        client = OpenAfspraakClient()
        products_id = products[0].identifier

        with log_api_errors("Could not retrieve locations for product"):
            locations = client.list_product_locations(products_id)

        return [
            Location(
                entry["public_id"],
                entry["name"],
                entry["address"],
                entry["postal_code"],
                entry["city"],
            )
            for entry in locations
            if entry["address"]
        ]

    @with_graceful_default(default=[])
    def get_dates(
        self,
        products: list[Product],
        location: Location,
        start_at: date | None = None,
        end_at: date | None = None,
    ) -> list[date]:
        """
        Retrieve all available dates for given ``product`` and ``location``.

        .. note:: The API does not support getting dates between a start and end
           date. The `start_at` and `end_at` arguments are ingored. The dates
           will always be 30 days from now.
        """
        assert products, "Can't retrieve dates without having product information"

        if len(products) > 1:
            raise GracefulOpenAfspraakException(
                "Multiple products are not supported by the OpenAfspraak API, only "
                "the first product is used."
            )

        product = products[0].identifier
        client = OpenAfspraakClient()

        with log_api_errors(
            "Could not retrieve dates for product '%s' at location '%s'",
            product,
            location,
        ):
            return client.list_dates(
                location_id=location.identifier,
                product_id=product,
            )

    @with_graceful_default(default=[])
    def get_times(
        self,
        products: list[Product],
        location: Location,
        day: date,
    ) -> list[datetime]:
        assert products, "Can't retrieve dates without having product information"
        assert day >= date.today(), "Can't retrieve times for past dates"

        if len(products) > 1:
            raise GracefulOpenAfspraakException(
                "Multiple products are not supported by the OpenAfspraak API, only "
                "the first product is used."
            )

        product = products[0].identifier
        client = OpenAfspraakClient()

        with log_api_errors(
            "Could not retrieve times for products '%s' at location '%s' on %s",
            product,
            location,
            day,
        ):
            return client.list_times(
                location_id=location.identifier,
                product_id=product,
                day=day,
            )

    def get_required_customer_fields(
        self,
        products: list[Product],
    ) -> list[Component]:
        # TODO:: Actually get the required fields for a specific product from the API.
        config = OpenAfspraakConfig.get_solo()
        assert isinstance(config, OpenAfspraakConfig)
        components = [
            FIELD_TO_FORMIO_COMPONENT[field]
            for field in config.required_customer_fields
        ]
        return components

    def create_appointment(
        self,
        products: list[Product],
        location: Location,
        start_at: datetime,
        client: _CustomerDetails | Customer,
        remarks: str = "",
    ) -> str:
        assert (
            products
        ), "Can't create an appointment without having product information"
        customer = normalize_customer_details(client)

        if len(products) > 1:
            raise GracefulOpenAfspraakException(
                "Multiple products are not supported by the OpenAfspraak API, only "
                "the first product is used."
            )

        # Since the duration is not stored, we need to duration time of the product to
        # calculate the end time we need to get the product from the API.
        # This is a bit of a hack, but it's the only way to get the duration.
        api_client = OpenAfspraakClient()
        product_identifier = products[0].identifier

        with log_api_errors(
            "Could not create appointment for product '%s' at location '%s' starting at %s",
            product_identifier,
            location,
            start_at,
        ):
            endpoint = f"products/{product_identifier}"
            response = api_client.get(endpoint)
            response.raise_for_status()
            product = parse_product(response.json())

        # Now that we got the duration of the product we can can culate the end time and continue
        # with creating the appointment.
        end_time = start_at + product.duration

        body = {
            "product_id": product.identifier,
            "location_id": location.identifier,
            "start_time": start_at.isoformat(),
            "end_time": end_time.isoformat(),
            "customers": [
                {choice: value for choice, value in customer.details.items() if value}
            ],
        }

        endpoint = "bookings"

        try:
            response = api_client.post(endpoint, json=body)
            print(response.json())
            response.raise_for_status()
            return response.json()["public_id"]
        except (OpenAfspraakException, RequestException, KeyError) as exc:
            logger.error(
                "Could not create appointment for product '%s' at location '%s' starting at %s",
                product,
                location,
                start_at,
                exc_info=exc,
                extra={
                    "product_id": product,
                    "location": location.identifier,
                    "start_time": start_at,
                },
            )
            raise AppointmentCreateFailed("Could not create appointment") from exc
        except Exception as exc:
            raise AppointmentCreateFailed(
                "Unexpected appointment create failure"
            ) from exc

    def delete_appointment(self, identifier: str) -> None:
        print("delete_appointment")
        pass

    def get_appointment_details(self, identifier: str) -> AppointmentDetails:
        print("get_appointment_details")
        pass

    def check_config(self):
        client = OpenAfspraakClient()
        try:
            response = client.get("products")
            response.raise_for_status()
        except (OpenAfspraakException, RequestException) as e:
            raise InvalidPluginConfiguration(
                _("Invalid response: {exception}").format(exception=e)
            )

    def get_config_actions(self):
        return [
            (
                _("Configuration"),
                reverse(
                    "admin:openafspraak_openafspraakconfig_change",
                    args=(OpenAfspraakConfig.singleton_instance_id,),
                ),
            ),
        ]

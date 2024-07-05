import logging
import warnings
from contextlib import contextmanager
from datetime import date, datetime
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
from ...registry import register
from .client import OpenAfspraakClient
from .constants import CustomerFields
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

        return [
            Product(
                entry["public_id"],
                entry["name"],
                entry["appointment_duration"],
            )
            for entry in products
        ]

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
        assert products, "Location retrieval without products is not supported."

        if len(products) > 1:
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
        pass

    def create_appointment(
        self,
        products: list[Product],
        location: Location,
        start_at: datetime,
        client: _CustomerDetails | Customer,
        remarks: str = "",
    ) -> str:
        pass

    def delete_appointment(self, identifier: str) -> None:
        pass

    def get_appointment_details(self, identifier: str) -> AppointmentDetails:
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

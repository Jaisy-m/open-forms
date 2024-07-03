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
        Retrieve all available products and services to create an appointment for.

        Qmatic has a couple of possible endpoints for this, most notably one returning
        a flat list of products (all or filtered by branch) and two others that return
        product groups. The product groups dictate which products can be booked together.

        We have to use all of these, since the flat list of products contains additional
        information like whether a product is public and/or active, which is not included
        in the service groups.

        The service groups per branch requires v2 API client, the rest can be done with
        the v1 client.
        """

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
        if products is None or len(products) == 0:
            raise GracefulOpenAfspraakException(
                "Location retrieval without products is not supported."
            )

        # client = OpenAfspraakClient()

        # products = products or []
        # product_ids = [product.identifier for product in products]
        #
        # endpoint = f"services/{product_ids[0]}/branches" if product_ids else "branches"
        #
        # with log_api_errors(
        #     "Could not retrieve locations for product, using API endpoint '%s'",
        #     endpoint,
        # ):
        #     response = client.get(endpoint)
        #     response.raise_for_status()
        #
        # # NOTE: Filter out locations that do not have a postal code to prevent
        # # non-physical addresses.
        #
        # return [
        #     Location(entry["publicId"], entry["name"])
        #     for entry in response.json()["branchList"]
        #     if entry["addressZip"]
        # ]

    @with_graceful_default(default=[])
    def get_dates(
        self,
        products: list[Product],
        location: Location,
        start_at: date | None = None,
        end_at: date | None = None,
    ) -> list[date]:
        """
        Retrieve all available dates for given ``products`` and ``location``.

        From the documentation:

            numberOfCustomers will be used on all services when calculating the
            appointment duration. For example, a service with Duration of 10 minutes and
            additionalCustomerDuration of 5 minutes will result in an appointment
            duration of 50 when minutes for 4 customers and 2 services.

        The example given shows that it makes little sense to attach number of customers
        to a particular product/service. E.g. if you have amount=2 for product 1 and
        amount=3 for product 2, booking the appointment for 3 customers results in time
        for 3 people for each product (which is more than you need). Using 5 customers (
        2 + 3) would result in time reserved for 10 people and is incorrect in this
        situation.

        .. note:: The API does not support getting dates between a start and end
           date. The `start_at` and `end_at` arguments are ingored.
        """

    @with_graceful_default(default=[])
    def get_times(
        self,
        products: list[Product],
        location: Location,
        day: date,
    ) -> list[datetime]:
        pass

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
            response = client.get("services")
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
                    "admin:qmatic_qmaticconfig_change",
                    args=(OpenAfspraakConfig.singleton_instance_id,),
                ),
            ),
        ]

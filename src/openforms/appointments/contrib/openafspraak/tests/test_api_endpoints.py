from django.test import TestCase

import requests_mock

from ..exceptions import OpenAfspraakException
from ..plugin import OpenAfspraakAppointment
from .utils import OPENAFSPRAAK_BASE_URL, MockConfigMixin

plugin = OpenAfspraakAppointment("openafspraak")


class ResponseCodeTests(MockConfigMixin, TestCase):
    @requests_mock.Mocker()
    def test_internal_server_error(self, m):
        m.get(
            f"{OPENAFSPRAAK_BASE_URL}/products",
            status_code=500,
            text="Internal Server Error",
        )

        with self.assertRaises(OpenAfspraakException) as context:
            plugin.get_available_products()
            self.assertEqual(
                "Server error (HTTP 500): Internal Server Error", str(context.exception)
            )


# class ListAvailableProductsTests(MockConfigMixin, TestCase):
# def test_listing_products_without_location(self):
#     products = plugin.get_available_products()
#     self.assertEqual(len(products), 2)
#
#     self.assertEqual(
#         products[0],
#         Product(
#             identifier="1",
#             name="Product 1",
#             code="Product 1 description",
#             duration=timedelta(minutes=30),
#         ),
#     )

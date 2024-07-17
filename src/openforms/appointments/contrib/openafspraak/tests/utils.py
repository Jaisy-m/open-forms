from pathlib import Path
from unittest.mock import patch

from zgw_consumers.constants import AuthTypes

from openforms.utils.tests.cache import clear_caches

from ....models import AppointmentsConfig
from ..models import OpenAfspraakConfig
from .factories import ServiceFactory

TESTS_DIR = Path(__file__).parent.resolve()

MOCK_DIR = TESTS_DIR / "mock"
VCR_DIR = TESTS_DIR / "data"
OPENAFSPRAAK_BASE_URL = "http://localhost:8080/api/v1/"


def mock_response(filename: str):
    full_path = MOCK_DIR / filename
    return full_path.read_text()


class MockConfigMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()  # type: ignore

        cls.service = ServiceFactory.create(auth_type=AuthTypes.no_auth, api_root=OPENAFSPRAAK_BASE_URL)

    def setUp(self):
        super().setUp()  # type: ignore

        self.addCleanup(clear_caches)  # type: ignore

        main_config_patcher = patch(
            "openforms.appointments.utils.AppointmentsConfig.get_solo",
            return_value=AppointmentsConfig(plugin="qmatic"),
        )
        main_config_patcher.start()
        self.addCleanup(main_config_patcher.stop)  # type: ignore

        self.openafspraak_config = OpenAfspraakConfig(service=self.service)
        self.api_root = self.openafspraak_config.service.api_root
        openafspraak_config_patchers = [
            patch(
                "openforms.appointments.contrib.openafspraak.client.OpenAfspraakConfig.get_solo",
                return_value=self.openafspraak_config,
            ),
            patch(
                "openforms.appointments.contrib.openafspraak.plugin.OpenAfspraakConfig.get_solo",
                return_value=self.openafspraak_config,
            ),
        ]
        for patcher in openafspraak_config_patchers:
            patcher.start()
            self.addCleanup(patcher.stop)  # type: ignore

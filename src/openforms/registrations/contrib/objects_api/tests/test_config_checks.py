from django.test import TestCase

import requests
import requests_mock
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openforms.plugins.exceptions import InvalidPluginConfiguration

from ..models import ObjectsAPIGroupConfig
from ..plugin import PLUGIN_IDENTIFIER, ObjectsAPIRegistration


class ConfigCheckTests(TestCase):
    def setUp(self):
        super().setUp()

        self.config = ObjectsAPIGroupConfig.objects.create(
            objects_service=ServiceFactory.create(
                api_root="https://objects.example.com/api/v1/",
            ),
            objecttypes_service=ServiceFactory.create(
                api_root="https://objecttypes.example.com/api/v1/",
            ),
            drc_service=ServiceFactory.create(
                api_root="https://documents.example.com/api/v1/",
                api_type=APITypes.drc,
            ),
            catalogi_service=ServiceFactory.create(
                api_root="https://catalogi.example.com/api/v1/",
                api_type=APITypes.drc,
            ),
            organisatie_rsin="123456782",
        )

    def _mockForValidServiceConfiguration(self, m: requests_mock.Mocker) -> None:
        m.get(
            "https://objects.example.com/api/v1/objects?pageSize=1",
            json={"results": []},
        )
        m.get(
            "https://objecttypes.example.com/api/v1/objecttypes?pageSize=1",
            json={"results": []},
        )
        m.get(
            "https://documents.example.com/api/v1/enkelvoudiginformatieobjecten",
            json={"results": []},
        )
        m.get(
            "https://catalogi.example.com/api/v1/informatieobjecttypen",
            json={"results": []},
        )

    def test_no_objects_service_configured(self):
        self.config.objects_service = None
        self.config.save()
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        with self.assertRaises(InvalidPluginConfiguration):
            plugin.check_config()

    @requests_mock.Mocker()
    def test_no_objecttypes_service_configured(self, m: requests_mock.Mocker):
        # Objects API needs to be set up as services are checked in a certain order
        m.get(
            "https://objects.example.com/api/v1/objects?pageSize=1",
            json={"results": []},
        )
        self.config.objecttypes_service = None
        self.config.save()
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        with self.assertRaises(InvalidPluginConfiguration):
            plugin.check_config()

    @requests_mock.Mocker()
    def test_objects_service_misconfigured_connection_error(self, m):
        m.get(
            "https://objects.example.com/api/v1/objects?pageSize=1",
            exc=requests.ConnectionError,
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        with self.assertRaises(InvalidPluginConfiguration):
            plugin.check_config()

    @requests_mock.Mocker()
    def test_objects_service_misconfigured_http_error(self, m):
        m.get(
            "https://objects.example.com/api/v1/objects?pageSize=1",
            status_code=400,
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        with self.assertRaises(InvalidPluginConfiguration):
            plugin.check_config()

    @requests_mock.Mocker()
    def test_objects_service_misconfigured_redirect(self, m):
        m.get(
            "https://objects.example.com/api/v1/objects?pageSize=1",
            status_code=302,
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        with self.assertRaises(InvalidPluginConfiguration):
            plugin.check_config()

    @requests_mock.Mocker()
    def test_objecttypes_service_misconfigured_redirect(self, m):
        m.get(
            "https://objects.example.com/api/v1/objects?pageSize=1",
            json={"results": []},
        )
        m.get(
            "https://objecttypes.example.com/api/v1/objecttypes?pageSize=1",
            status_code=302,
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        with self.assertRaises(InvalidPluginConfiguration):
            plugin.check_config()

    @requests_mock.Mocker()
    def test_no_documents_service_configured(self, m):
        self.config.drc_service = None
        self.config.save()
        m.get(
            "https://objects.example.com/api/v1/objects?pageSize=1",
            json={"results": []},
        )
        m.get(
            "https://objecttypes.example.com/api/v1/objecttypes?pageSize=1",
            json={"results": []},
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        with self.assertRaises(InvalidPluginConfiguration):
            plugin.check_config()

    @requests_mock.Mocker()
    def test_no_catalogi_service_configured(self, m):
        self.config.catalogi_service = None
        self.config.save()
        m.get(
            "https://objects.example.com/api/v1/objects?pageSize=1",
            json={"results": []},
        )
        m.get(
            "https://objecttypes.example.com/api/v1/objecttypes?pageSize=1",
            json={"results": []},
        )
        m.get(
            "https://documents.example.com/api/v1/enkelvoudiginformatieobjecten",
            json={"results": []},
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        with self.assertRaises(InvalidPluginConfiguration):
            plugin.check_config()

    @requests_mock.Mocker()
    def test_config_valid(self, m):
        self._mockForValidServiceConfiguration(m)

        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)
        plugin.check_config()

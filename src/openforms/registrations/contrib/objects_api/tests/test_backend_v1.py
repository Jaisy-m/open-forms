import textwrap
from datetime import date
from unittest.mock import patch
from uuid import UUID

from django.test import TestCase, override_settings, tag
from django.utils import timezone

import requests_mock
from zgw_consumers.test import generate_oas_component

from openforms.authentication.service import AuthAttribute
from openforms.payments.constants import PaymentStatus
from openforms.payments.tests.factories import SubmissionPaymentFactory
from openforms.submissions.tests.factories import (
    SubmissionFactory,
    SubmissionFileAttachmentFactory,
)

from ....constants import RegistrationAttribute
from ..models import ObjectsAPIConfig, ObjectsAPIRegistrationData
from ..plugin import PLUGIN_IDENTIFIER, ObjectsAPIRegistration
from ..submission_registration import ObjectsAPIV1Handler
from ..typing import RegistrationOptionsV1
from .factories import ObjectsAPIGroupConfigFactory


def get_create_json(req, ctx):
    request_body = req.json()
    return {
        "url": "https://objecten.nl/api/v1/objects/1",
        "uuid": "095be615-a8ad-4c33-8e9c-c7612fbf6c9f",
        "type": request_body["type"],
        "record": {
            "index": 0,
            **request_body["record"],  # typeVersion, data and startAt keys
            "endAt": None,  # see https://github.com/maykinmedia/objects-api/issues/349
            "registrationAt": date.today().isoformat(),
            "correctionFor": 0,
            "correctedBy": "",
        },
    }


@requests_mock.Mocker()
class ObjectsAPIBackendV1Tests(TestCase):
    maxDiff = None

    def setUp(self):
        super().setUp()

        config = ObjectsAPIConfig(
            productaanvraag_type="terugbelnotitie",
            content_json=textwrap.dedent(
                """
                {
                    "bron": {
                        "naam": "Open Formulieren",
                        "kenmerk": "{{ submission.kenmerk }}"
                    },
                    "type": "{{ productaanvraag_type }}",
                    "aanvraaggegevens": {% json_summary %},
                    "taal": "{{ submission.language_code  }}",
                    "betrokkenen": [
                        {
                            "inpBsn" : "{{ variables.auth_bsn }}",
                            "rolOmschrijvingGeneriek" : "initiator"
                        }
                    ],
                    "pdf": "{{ submission.pdf_url }}",
                    "csv": "{{ submission.csv_url }}",
                    "bijlagen": {% uploaded_attachment_urls %},
                    "payment": {
                        "completed": {% if payment.completed %}true{% else %}false{% endif %},
                        "amount": {{ payment.amount }},
                        "public_order_ids": {{ payment.public_order_ids }}
                    }
                }"""
            ),
        )

        config_patcher = patch(
            "openforms.registrations.contrib.objects_api.models.ObjectsAPIConfig.get_solo",
            return_value=config,
        )
        self.mock_get_config = config_patcher.start()
        self.addCleanup(config_patcher.stop)

        self.objects_api_group = ObjectsAPIGroupConfigFactory.create(
            objects_service__api_root="https://objecten.nl/api/v1/",
            objecttypes_service__api_root="https://objecttypen.nl/api/v1/",
            drc_service__api_root="https://documenten.nl/api/v1/",
            informatieobjecttype_submission_report="https://catalogi.nl/api/v1/informatieobjecttypen/1",
            informatieobjecttype_submission_csv="https://catalogi.nl/api/v1/informatieobjecttypen/4",
            informatieobjecttype_attachment="https://catalogi.nl/api/v1/informatieobjecttypen/3",
            organisatie_rsin="000000000",
        )

    def test_submission_with_objects_api_backend_override_defaults(self, m):
        submission = SubmissionFactory.from_components(
            [
                {
                    "key": "voornaam",
                    "type": "textfield",
                    "registration": {
                        "attribute": RegistrationAttribute.initiator_voornamen,
                    },
                },
                {
                    "key": "achternaam",
                    "type": "textfield",
                    "registration": {
                        "attribute": RegistrationAttribute.initiator_geslachtsnaam,
                    },
                },
                {
                    "key": "tussenvoegsel",
                    "type": "textfield",
                    "registration": {
                        "attribute": RegistrationAttribute.initiator_tussenvoegsel,
                    },
                },
                {
                    "key": "geboortedatum",
                    "type": "date",
                    "registration": {
                        "attribute": RegistrationAttribute.initiator_geboortedatum,
                    },
                },
                {
                    "key": "coordinaat",
                    "type": "map",
                    "registration": {
                        "attribute": RegistrationAttribute.locatie_coordinaat,
                    },
                },
            ],
            submitted_data={
                "voornaam": "Foo",
                "achternaam": "Bar",
                "tussenvoegsel": "de",
                "geboortedatum": "2000-12-31",
                "coordinaat": [52.36673378967122, 4.893164274470299],
            },
            language_code="en",
        )
        submission_step = submission.steps[0]
        assert submission_step.form_step
        step_slug = submission_step.form_step.slug

        objects_form_options = dict(
            version=1,
            objects_api_group=self.objects_api_group,
            objecttype=UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
            objecttype_version=2,
            productaanvraag_type="testproduct",
            informatieobjecttype_submission_report="https://catalogi.nl/api/v1/informatieobjecttypen/2",
            upload_submission_csv=True,
            informatieobjecttype_submission_csv="https://catalogi.nl/api/v1/informatieobjecttypen/5",
            organisatie_rsin="123456782",
            zaak_vertrouwelijkheidaanduiding="geheim",
            doc_vertrouwelijkheidaanduiding="geheim",
        )

        # Set up API mocks
        expected_document_result = generate_oas_component(
            "documenten",
            "schemas/EnkelvoudigInformatieObject",
            url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/1",
        )
        expected_csv_document_result = generate_oas_component(
            "documenten",
            "schemas/EnkelvoudigInformatieObject",
            url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/2",
        )
        m.post(
            "https://objecten.nl/api/v1/objects",
            status_code=201,
            json=get_create_json,
        )
        m.get(
            "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
            json={
                "url": "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377"
            },
            status_code=200,
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=expected_document_result,
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=expected_csv_document_result,
            additional_matcher=lambda req: "csv" in req.json()["bestandsnaam"],
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        # Run the registration
        result = plugin.register_submission(submission, objects_form_options)

        # check the requests made
        self.assertEqual(len(m.request_history), 4)
        document_create, csv_document_create, _, object_create = m.request_history

        with self.subTest("object create call and registration result"):
            submitted_object_data = object_create.json()
            expected_object_body = {
                "type": "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
                "record": {
                    "typeVersion": 2,
                    "data": {
                        "bron": {
                            "naam": "Open Formulieren",
                            "kenmerk": str(submission.uuid),
                        },
                        "type": "testproduct",
                        "aanvraaggegevens": {
                            step_slug: {
                                "voornaam": "Foo",
                                "achternaam": "Bar",
                                "tussenvoegsel": "de",
                                "geboortedatum": "2000-12-31",
                                "coordinaat": [52.36673378967122, 4.893164274470299],
                            }
                        },
                        "taal": "en",
                        "betrokkenen": [
                            {"inpBsn": "", "rolOmschrijvingGeneriek": "initiator"}
                        ],
                        "pdf": expected_document_result["url"],
                        "csv": expected_csv_document_result["url"],
                        "bijlagen": [],
                        "payment": {
                            "completed": False,
                            "amount": 0,
                            "public_order_ids": [],
                        },
                    },
                    "startAt": date.today().isoformat(),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [52.36673378967122, 4.893164274470299],
                    },
                },
            }
            self.assertEqual(object_create.method, "POST")
            self.assertEqual(object_create.url, "https://objecten.nl/api/v1/objects")
            self.assertEqual(submitted_object_data, expected_object_body)

            # NOTE: the backend adds additional metadata that is not in the request body.
            expected_result = {
                "url": "https://objecten.nl/api/v1/objects/1",
                "uuid": "095be615-a8ad-4c33-8e9c-c7612fbf6c9f",
                "type": f"https://objecttypen.nl/api/v1/objecttypes/{objects_form_options['objecttype']}",
                "record": {
                    "index": 0,
                    "typeVersion": objects_form_options["objecttype_version"],
                    "data": submitted_object_data["record"]["data"],
                    "geometry": {
                        "type": "Point",
                        "coordinates": [52.36673378967122, 4.893164274470299],
                    },
                    "startAt": date.today().isoformat(),
                    "endAt": None,
                    "registrationAt": date.today().isoformat(),
                    "correctionFor": 0,
                    "correctedBy": "",
                },
            }
            # Result is simply the created object
            self.assertEqual(result, expected_result)

        with self.subTest("Document create (PDF summary)"):
            document_create_body = document_create.json()

            self.assertEqual(document_create.method, "POST")
            self.assertEqual(
                document_create.url,
                "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            )
            self.assertEqual(document_create_body["bronorganisatie"], "123456782")
            self.assertEqual(
                document_create_body["informatieobjecttype"],
                "https://catalogi.nl/api/v1/informatieobjecttypen/2",
            )
            self.assertEqual(
                document_create_body["vertrouwelijkheidaanduiding"],
                "geheim",
            )

        with self.subTest("Document create (CSV export)"):
            csv_document_create_body = csv_document_create.json()

            self.assertEqual(csv_document_create.method, "POST")
            self.assertEqual(
                csv_document_create.url,
                "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            )
            # Overridden informatieobjecttype used
            self.assertEqual(
                csv_document_create_body["informatieobjecttype"],
                "https://catalogi.nl/api/v1/informatieobjecttypen/5",
            )

    def test_submission_with_objects_api_backend_override_defaults_upload_csv_default_type(
        self, m
    ):
        submission = SubmissionFactory.from_components(
            [
                {
                    "key": "voornaam",
                    "registration": {
                        "attribute": RegistrationAttribute.initiator_voornamen,
                    },
                },
            ],
            submitted_data={"voornaam": "Foo"},
        )
        objects_form_options = dict(
            version=1,
            objects_api_group=self.objects_api_group,
            objecttype=UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
            objecttype_version=2,
            productaanvraag_type="testproduct",
            informatieobjecttype_submission_report="https://catalogi.nl/api/v1/informatieobjecttypen/2",
            upload_submission_csv=True,
            organisatie_rsin="123456782",
            zaak_vertrouwelijkheidaanduiding="geheim",
            doc_vertrouwelijkheidaanduiding="geheim",
        )

        # Set up API mocks
        expected_document_result = generate_oas_component(
            "documenten",
            "schemas/EnkelvoudigInformatieObject",
            url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/1",
        )
        expected_csv_document_result = generate_oas_component(
            "documenten",
            "schemas/EnkelvoudigInformatieObject",
            url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/2",
        )
        m.post(
            "https://objecten.nl/api/v1/objects",
            status_code=201,
            json=get_create_json,
        )
        m.get(
            "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
            json={
                "url": "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377"
            },
            status_code=200,
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=expected_document_result,
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=expected_csv_document_result,
            additional_matcher=lambda req: "csv" in req.json()["bestandsnaam"],
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        # Run the registration
        plugin.register_submission(submission, objects_form_options)

        # check the requests made
        self.assertEqual(len(m.request_history), 4)
        document_create, csv_document_create, _, object_create = m.request_history

        with self.subTest("object create call and registration result"):
            submitted_object_data = object_create.json()

            self.assertEqual(
                submitted_object_data["type"],
                "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
            )
            self.assertEqual(submitted_object_data["record"]["typeVersion"], 2)
            self.assertEqual(
                submitted_object_data["record"]["data"]["type"], "testproduct"
            )

        with self.subTest("Document create (PDF summary)"):
            document_create_body = document_create.json()

            self.assertEqual(document_create_body["bronorganisatie"], "123456782")
            self.assertEqual(
                document_create_body["informatieobjecttype"],
                "https://catalogi.nl/api/v1/informatieobjecttypen/2",
            )
            self.assertEqual(
                document_create_body["vertrouwelijkheidaanduiding"],
                "geheim",
            )

        with self.subTest("Document create (CSV export)"):
            csv_document_create_body = csv_document_create.json()

            self.assertEqual(
                csv_document_create.url,
                "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            )
            # Default informatieobjecttype used
            self.assertEqual(
                csv_document_create_body["informatieobjecttype"],
                "https://catalogi.nl/api/v1/informatieobjecttypen/4",
            )

    def test_submission_with_objects_api_backend_override_defaults_do_not_upload_csv(
        self, m
    ):
        submission = SubmissionFactory.from_components(
            [
                {
                    "key": "voornaam",
                    "registration": {
                        "attribute": RegistrationAttribute.initiator_voornamen,
                    },
                },
            ],
            submitted_data={"voornaam": "Foo"},
        )
        # Set up API mocks
        expected_document_result = generate_oas_component(
            "documenten",
            "schemas/EnkelvoudigInformatieObject",
            url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/1",
        )
        m.post(
            "https://objecten.nl/api/v1/objects",
            status_code=201,
            json=get_create_json,
        )
        m.get(
            "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
            json={
                "url": "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377"
            },
            status_code=200,
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=expected_document_result,
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        # Run the registration
        plugin.register_submission(
            submission,
            {
                "version": 1,
                "objecttype": UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
                "objecttype_version": 1,
                "objects_api_group": self.objects_api_group,
                "upload_submission_csv": False,
            },
        )

        # check the requests made
        self.assertEqual(len(m.request_history), 3)
        object_create = m.last_request

        with self.subTest("object create call and registration result"):
            submitted_object_data = object_create.json()

            self.assertEqual(submitted_object_data["record"]["data"]["csv"], "")
            self.assertEqual(
                submitted_object_data["record"]["data"]["pdf"],
                expected_document_result["url"],
            )

    def test_submission_with_objects_api_backend_missing_csv_iotype(self, m):
        submission = SubmissionFactory.create(with_report=True, completed=True)
        # Set up API mocks
        expected_document_result = generate_oas_component(
            "documenten",
            "schemas/EnkelvoudigInformatieObject",
            url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/1",
        )
        m.post(
            "https://objecten.nl/api/v1/objects",
            status_code=201,
            json=get_create_json,
        )
        m.get(
            "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
            json={
                "url": "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377"
            },
            status_code=200,
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=expected_document_result,
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        # Run the registration
        plugin.register_submission(
            submission,
            {
                "version": 1,
                "objecttype": UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
                "objecttype_version": 1,
                "objects_api_group": self.objects_api_group,
                "upload_submission_csv": True,
                "informatieobjecttype_submission_csv": "",
            },
        )

        # check the requests made
        self.assertEqual(len(m.request_history), 3)
        object_create = m.last_request

        with self.subTest("object create call and registration result"):
            submitted_object_data = object_create.json()

            self.assertEqual(submitted_object_data["record"]["data"]["csv"], "")
            self.assertEqual(
                submitted_object_data["record"]["data"]["pdf"],
                expected_document_result["url"],
            )

    def test_submission_with_objects_api_backend_override_content_json(self, m):
        submission = SubmissionFactory.from_components(
            [
                {
                    "key": "voornaam",
                    "type": "textfield",
                    "registration": {
                        "attribute": RegistrationAttribute.initiator_voornamen,
                    },
                },
            ],
            submitted_data={"voornaam": "Foo"},
            language_code="en",
        )
        submission_step = submission.steps[0]
        assert submission_step.form_step
        step_slug = submission_step.form_step.slug
        objects_form_options = dict(
            version=1,
            objecttype=UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
            objecttype_version=1,
            objects_api_group=self.objects_api_group,
            upload_submission_csv=False,
            content_json=textwrap.dedent(
                """
                {
                    "bron": {
                        "naam": "Open Formulieren",
                        "kenmerk": "{{ submission.kenmerk }}"
                    },
                    "type": "{{ productaanvraag_type }}",
                    "aanvraaggegevens": {% json_summary %},
                    "taal": "{{ submission.language_code  }}"
                }
            """
            ),
        )
        # Set up API mocks
        expected_document_result = generate_oas_component(
            "documenten",
            "schemas/EnkelvoudigInformatieObject",
            url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/1",
        )
        m.post(
            "https://objecten.nl/api/v1/objects",
            status_code=201,
            json=get_create_json,
        )
        m.get(
            "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
            json={
                "url": "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377"
            },
            status_code=200,
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=expected_document_result,
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        # Run the registration
        plugin.register_submission(submission, objects_form_options)

        # check the requests made
        self.assertEqual(len(m.request_history), 3)

        with self.subTest("object create call"):
            object_create = m.last_request
            expected_record_data = {
                "bron": {
                    "naam": "Open Formulieren",
                    "kenmerk": str(submission.uuid),
                },
                "type": "terugbelnotitie",
                "aanvraaggegevens": {step_slug: {"voornaam": "Foo"}},
                "taal": "en",
            }

            self.assertEqual(object_create.url, "https://objecten.nl/api/v1/objects")
            object_create_body = object_create.json()
            self.assertEqual(object_create_body["record"]["data"], expected_record_data)

    def test_submission_with_objects_api_backend_use_config_defaults(self, m):
        submission = SubmissionFactory.from_components(
            [
                {
                    "key": "voornaam",
                    "registration": {
                        "attribute": RegistrationAttribute.initiator_voornamen,
                    },
                }
            ],
            submitted_data={"voornaam": "Foo"},
            language_code="en",
        )
        submission_step = submission.steps[0]
        assert submission_step.form_step
        step_slug = submission_step.form_step.slug

        # Set up API mocks
        expected_document_result = generate_oas_component(
            "documenten",
            "schemas/EnkelvoudigInformatieObject",
            url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/1",
        )
        expected_csv_document_result = generate_oas_component(
            "documenten",
            "schemas/EnkelvoudigInformatieObject",
            url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/2",
        )
        m.post(
            "https://objecten.nl/api/v1/objects",
            status_code=201,
            json=get_create_json,
        )
        m.get(
            "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
            json={
                "url": "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377"
            },
            status_code=200,
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=expected_document_result,
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=expected_csv_document_result,
            additional_matcher=lambda req: "csv" in req.json()["bestandsnaam"],
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        # Run the registration, applying default options from the config
        # (while still specifying the required fields):
        plugin.register_submission(
            submission,
            {
                "version": 1,
                "objects_api_group": self.objects_api_group,
                "objecttype": UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
                "objecttype_version": 1,
            },
        )

        # check the requests made
        self.assertEqual(len(m.request_history), 3)
        document_create, _, object_create = m.request_history

        with self.subTest("Document create (PDF summary)"):
            document_create_body = document_create.json()

            self.assertEqual(
                document_create.url,
                "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            )
            self.assertEqual(document_create_body["taal"], "eng")
            self.assertEqual(document_create_body["bronorganisatie"], "000000000")
            self.assertEqual(
                document_create_body["informatieobjecttype"],
                "https://catalogi.nl/api/v1/informatieobjecttypen/1",
            )
            self.assertNotIn("vertrouwelijkheidaanduiding", document_create_body)

        with self.subTest("object create call"):
            object_create_body = object_create.json()

            expected_record_data = {
                "typeVersion": 1,
                "data": {
                    "aanvraaggegevens": {step_slug: {"voornaam": "Foo"}},
                    "betrokkenen": [
                        {"inpBsn": "", "rolOmschrijvingGeneriek": "initiator"}
                    ],
                    "bijlagen": [],
                    "bron": {
                        "kenmerk": str(submission.uuid),
                        "naam": "Open Formulieren",
                    },
                    "csv": "",
                    "pdf": expected_document_result["url"],
                    "taal": "en",
                    "type": "terugbelnotitie",
                    "payment": {
                        "completed": False,
                        "amount": 0,
                        "public_order_ids": [],
                    },
                },
                "startAt": date.today().isoformat(),
            }
            self.assertEqual(object_create.url, "https://objecten.nl/api/v1/objects")
            self.assertEqual(object_create_body["record"], expected_record_data)

    def test_submission_with_objects_api_backend_attachments(self, m):
        # Form.io configuration is irrelevant for this test, but normally you'd have
        # set up some file upload components.
        submission = SubmissionFactory.from_components(
            [],
            submitted_data={},
            language_code="en",
            completed=True,
        )
        submission_step = submission.steps[0]
        # Set up two attachments to upload to the documents API
        SubmissionFileAttachmentFactory.create(
            submission_step=submission_step, file_name="attachment1.jpg"
        )
        SubmissionFileAttachmentFactory.create(
            submission_step=submission_step, file_name="attachment2.jpg"
        )

        # Set up API mocks
        pdf, attachment1, attachment2 = [
            generate_oas_component(
                "documenten",
                "schemas/EnkelvoudigInformatieObject",
                url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/1",
            ),
            generate_oas_component(
                "documenten",
                "schemas/EnkelvoudigInformatieObject",
                url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/2",
            ),
            generate_oas_component(
                "documenten",
                "schemas/EnkelvoudigInformatieObject",
                url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/3",
            ),
        ]
        m.post(
            "https://objecten.nl/api/v1/objects",
            status_code=201,
            json=get_create_json,
        )
        m.get(
            "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
            json={
                "url": "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377"
            },
            status_code=200,
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=pdf,
            additional_matcher=lambda req: req.json()["bestandsnaam"].endswith(".pdf"),
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=attachment1,
            additional_matcher=lambda req: req.json()["bestandsnaam"]
            == "attachment1.jpg",
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=attachment2,
            additional_matcher=lambda req: req.json()["bestandsnaam"]
            == "attachment2.jpg",
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        # Run the registration
        plugin.register_submission(
            submission,
            {
                "version": 1,
                "objects_api_group": self.objects_api_group,
                "objecttype": UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
                "objecttype_version": 1,
            },
        )

        # check the requests made
        self.assertEqual(len(m.request_history), 5)
        (
            pdf_create,
            attachment1_create,
            attachment2_create,
            _,
            object_create,
        ) = m.request_history

        with self.subTest("object create call"):
            record_data = object_create.json()["record"]["data"]

            self.assertEqual(object_create.url, "https://objecten.nl/api/v1/objects")
            self.assertEqual(
                record_data["pdf"],
                "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/1",
            )
            self.assertEqual(
                record_data["bijlagen"],
                [
                    "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/2",
                    "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/3",
                ],
            )

        with self.subTest("Document create (PDF summary)"):
            pdf_create_data = pdf_create.json()

            self.assertEqual(
                pdf_create.url,
                "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            )
            self.assertEqual(pdf_create_data["bronorganisatie"], "000000000")
            self.assertEqual(
                pdf_create_data["informatieobjecttype"],
                "https://catalogi.nl/api/v1/informatieobjecttypen/1",
            )
            self.assertNotIn("vertrouwelijkheidaanduiding", pdf_create_data)

        with self.subTest("Document create (attachment 1)"):
            attachment1_create_data = attachment1_create.json()

            self.assertEqual(
                attachment1_create.url,
                "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            )
            self.assertEqual(attachment1_create_data["bronorganisatie"], "000000000")
            self.assertEqual(attachment1_create_data["taal"], "eng")
            self.assertEqual(
                attachment1_create_data["informatieobjecttype"],
                "https://catalogi.nl/api/v1/informatieobjecttypen/3",
            )
            self.assertNotIn("vertrouwelijkheidaanduiding", attachment1_create_data)

        with self.subTest("Document create (attachment 2)"):
            attachment2_create_data = attachment2_create.json()

            self.assertEqual(
                attachment1_create.url,
                "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            )
            self.assertEqual(attachment2_create_data["bronorganisatie"], "000000000")
            self.assertEqual(attachment2_create_data["taal"], "eng")
            self.assertEqual(
                attachment2_create_data["informatieobjecttype"],
                "https://catalogi.nl/api/v1/informatieobjecttypen/3",
            )
            self.assertNotIn("vertrouwelijkheidaanduiding", attachment2_create_data)

    def test_submission_with_objects_api_backend_attachments_specific_iotypen(self, m):
        submission = SubmissionFactory.from_components(
            [
                {
                    "key": "field1",
                    "type": "file",
                    "registration": {
                        "informatieobjecttype": "https://catalogi.nl/api/v1/informatieobjecttypen/10",
                    },
                },
                {
                    "key": "field2",
                    "type": "file",
                    "registration": {
                        "informatieobjecttype": "",
                    },
                },
            ],
            language_code="en",
        )
        submission_step = submission.steps[0]
        SubmissionFileAttachmentFactory.create(
            submission_step=submission_step,
            file_name="attachment1.jpg",
            form_key="field1",
            _component_configuration_path="components.0",
        )
        SubmissionFileAttachmentFactory.create(
            submission_step=submission_step,
            file_name="attachment2.jpg",
            form_key="field2",
            _component_configuration_path="component.1",
        )

        # Set up API mocks
        pdf, attachment1, attachment2 = [
            generate_oas_component(
                "documenten",
                "schemas/EnkelvoudigInformatieObject",
                url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/1",
            ),
            generate_oas_component(
                "documenten",
                "schemas/EnkelvoudigInformatieObject",
                url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/2",
            ),
            generate_oas_component(
                "documenten",
                "schemas/EnkelvoudigInformatieObject",
                url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/3",
            ),
        ]
        m.post(
            "https://objecten.nl/api/v1/objects",
            status_code=201,
            json=get_create_json,
        )
        m.get(
            "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
            json={
                "url": "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377"
            },
            status_code=200,
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=pdf,
            additional_matcher=lambda req: req.json()["bestandsnaam"].endswith(".pdf"),
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=attachment1,
            additional_matcher=lambda req: req.json()["bestandsnaam"]
            == "attachment1.jpg",
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=attachment2,
            additional_matcher=lambda req: req.json()["bestandsnaam"]
            == "attachment2.jpg",
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        # Run the registration
        plugin.register_submission(
            submission,
            {
                "version": 1,
                "objects_api_group": self.objects_api_group,
                "objecttype": UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
                "objecttype_version": 1,
            },
        )

        # check the requests made
        self.assertEqual(len(m.request_history), 5)
        attachment1_create = m.request_history[1]
        attachment2_create = m.request_history[2]

        with self.subTest("Document create (attachment 1)"):
            attachment1_create_data = attachment1_create.json()

            self.assertEqual(
                attachment1_create.url,
                "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            )
            self.assertEqual(attachment1_create_data["bronorganisatie"], "000000000")
            self.assertEqual(attachment1_create_data["taal"], "eng")
            # Use override IOType
            self.assertEqual(
                attachment1_create_data["informatieobjecttype"],
                "https://catalogi.nl/api/v1/informatieobjecttypen/10",
            )
            self.assertNotIn("vertrouwelijkheidaanduiding", attachment1_create_data)

        with self.subTest("Document create (attachment 2)"):
            attachment2_create_data = attachment2_create.json()

            self.assertEqual(
                attachment1_create.url,
                "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            )
            self.assertEqual(attachment2_create_data["bronorganisatie"], "000000000")
            self.assertEqual(attachment2_create_data["taal"], "eng")
            # Fallback to default IOType
            self.assertEqual(
                attachment2_create_data["informatieobjecttype"],
                "https://catalogi.nl/api/v1/informatieobjecttypen/3",
            )
            self.assertNotIn("vertrouwelijkheidaanduiding", attachment2_create_data)

    def test_submission_with_objects_api_backend_attachments_component_overwrites(
        self, m
    ):
        submission = SubmissionFactory.from_components(
            [
                {
                    "key": "fileUpload",
                    "type": "file",
                    "registration": {
                        "informatieobjecttype": "https://catalogi.nl/api/v1/informatieobjecttypen/10",
                        "bronorganisatie": "123123123",
                        "docVertrouwelijkheidaanduiding": "geheim",
                        "titel": "A Custom Title",
                    },
                },
            ],
            submitted_data={
                "fileUpload": [
                    {
                        "url": "http://server/api/v2/submissions/files/62f2ec22-da7d-4385-b719-b8637c1cd483",
                        "data": {
                            "url": "http://server/api/v2/submissions/files/62f2ec22-da7d-4385-b719-b8637c1cd483",
                            "form": "",
                            "name": "some-attachment.jpg",
                            "size": 46114,
                            "baseUrl": "http://server/form",
                            "project": "",
                        },
                        "name": "my-image-12305610-2da4-4694-a341-ccb919c3d543.jpg",
                        "size": 46114,
                        "type": "image/jpg",
                        "storage": "url",
                        "originalName": "some-attachment.jpg",
                    }
                ],
            },
            language_code="en",
        )
        submission_step = submission.steps[0]
        SubmissionFileAttachmentFactory.create(
            submission_step=submission_step,
            file_name="some-attachment.jpg",
            form_key="fileUpload",
            _component_configuration_path="components.0",
        )

        # Set up API mocks
        pdf, attachment = [
            generate_oas_component(
                "documenten",
                "schemas/EnkelvoudigInformatieObject",
                url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/1",
            ),
            generate_oas_component(
                "documenten",
                "schemas/EnkelvoudigInformatieObject",
                url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/2",
            ),
        ]
        m.post(
            "https://objecten.nl/api/v1/objects",
            status_code=201,
            json=get_create_json,
        )
        m.get(
            "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
            json={
                "url": "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377"
            },
            status_code=200,
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=pdf,
            additional_matcher=lambda req: req.json()["bestandsnaam"].endswith(".pdf"),
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=attachment,
            additional_matcher=lambda req: req.json()["bestandsnaam"]
            == "some-attachment.jpg",
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        # Run the registration
        plugin.register_submission(
            submission,
            {
                "version": 1,
                "objects_api_group": self.objects_api_group,
                "objecttype": UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
                "objecttype_version": 1,
            },
        )

        # check the requests made
        self.assertEqual(len(m.request_history), 4)
        document_create_attachment = m.request_history[1]

        document_create_attachment_body = document_create_attachment.json()
        self.assertEqual(document_create_attachment.method, "POST")
        self.assertEqual(
            document_create_attachment.url,
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
        )
        # Check use of override settings
        self.assertEqual(
            document_create_attachment_body["informatieobjecttype"],
            "https://catalogi.nl/api/v1/informatieobjecttypen/10",
        )
        self.assertEqual(
            document_create_attachment_body["bronorganisatie"], "123123123"
        )
        self.assertEqual(
            document_create_attachment_body["vertrouwelijkheidaanduiding"], "geheim"
        )
        self.assertEqual(document_create_attachment_body["titel"], "A Custom Title")

    def test_submission_with_objects_api_backend_attachments_component_inside_fieldset_overwrites(
        self, m
    ):
        submission = SubmissionFactory.from_components(
            [
                {
                    "key": "fieldset",
                    "type": "fieldset",
                    "label": "A fieldset",
                    "components": [
                        {
                            "key": "fileUpload",
                            "type": "file",
                            "registration": {
                                "informatieobjecttype": "https://catalogi.nl/api/v1/informatieobjecttypen/10",
                                "bronorganisatie": "123123123",
                                "docVertrouwelijkheidaanduiding": "geheim",
                                "titel": "A Custom Title",
                            },
                        },
                    ],
                },
            ],
            submitted_data={
                "fileUpload": [
                    {
                        "url": "http://server/api/v2/submissions/files/62f2ec22-da7d-4385-b719-b8637c1cd483",
                        "data": {
                            "url": "http://server/api/v2/submissions/files/62f2ec22-da7d-4385-b719-b8637c1cd483",
                            "form": "",
                            "name": "some-attachment.jpg",
                            "size": 46114,
                            "baseUrl": "http://server/form",
                            "project": "",
                        },
                        "name": "my-image-12305610-2da4-4694-a341-ccb919c3d543.jpg",
                        "size": 46114,
                        "type": "image/jpg",
                        "storage": "url",
                        "originalName": "some-attachment.jpg",
                    }
                ],
            },
            language_code="en",
        )
        submission_step = submission.steps[0]
        SubmissionFileAttachmentFactory.create(
            submission_step=submission_step,
            file_name="some-attachment.jpg",
            form_key="fileUpload",
            _component_configuration_path="components.0.components.0",
        )
        # Set up API mocks
        pdf, attachment = [
            generate_oas_component(
                "documenten",
                "schemas/EnkelvoudigInformatieObject",
                url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/1",
            ),
            generate_oas_component(
                "documenten",
                "schemas/EnkelvoudigInformatieObject",
                url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/2",
            ),
        ]
        m.post(
            "https://objecten.nl/api/v1/objects",
            status_code=201,
            json=get_create_json,
        )
        m.get(
            "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
            json={
                "url": "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377"
            },
            status_code=200,
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=pdf,
            additional_matcher=lambda req: req.json()["bestandsnaam"].endswith(".pdf"),
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=attachment,
            additional_matcher=lambda req: req.json()["bestandsnaam"]
            == "some-attachment.jpg",
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        # Run the registration
        plugin.register_submission(
            submission,
            {
                "version": 1,
                "objects_api_group": self.objects_api_group,
                "objecttype": UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
                "objecttype_version": 1,
            },
        )

        # check the requests made
        self.assertEqual(len(m.request_history), 4)
        document_create_attachment = m.request_history[1]

        document_create_attachment_body = document_create_attachment.json()
        self.assertEqual(document_create_attachment.method, "POST")
        self.assertEqual(
            document_create_attachment.url,
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
        )
        # Check use of override settings
        self.assertEqual(
            document_create_attachment_body["informatieobjecttype"],
            "https://catalogi.nl/api/v1/informatieobjecttypen/10",
        )
        self.assertEqual(
            document_create_attachment_body["bronorganisatie"], "123123123"
        )
        self.assertEqual(
            document_create_attachment_body["vertrouwelijkheidaanduiding"], "geheim"
        )
        self.assertEqual(document_create_attachment_body["titel"], "A Custom Title")

    @override_settings(ESCAPE_REGISTRATION_OUTPUT=True)
    def test_submission_with_objects_api_escapes_html(self, m):
        content_template = textwrap.dedent(
            """
            {
                "summary": {% json_summary %},
                "manual_variable": "{{ variables.voornaam }}"
            }
            """
        )
        submission = SubmissionFactory.from_components(
            [
                {
                    "key": "voornaam",
                    "type": "textfield",
                    "registration": {
                        "attribute": RegistrationAttribute.initiator_voornamen,
                    },
                },
            ],
            submitted_data={"voornaam": "<script>alert();</script>"},
            language_code="en",
        )

        submission_step = submission.steps[0]
        assert submission_step.form_step
        step_slug = submission_step.form_step.slug
        # Set up API mocks
        expected_document_result = generate_oas_component(
            "documenten",
            "schemas/EnkelvoudigInformatieObject",
            url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/1",
        )
        m.post(
            "https://objecten.nl/api/v1/objects",
            status_code=201,
            json=get_create_json,
        )
        m.get(
            "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
            json={
                "url": "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377"
            },
            status_code=200,
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=expected_document_result,
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)

        # Run the registration
        plugin.register_submission(
            submission,
            {
                "version": 1,
                "objects_api_group": self.objects_api_group,
                "objecttype": UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
                "objecttype_version": 1,
                "content_json": content_template,
                "upload_submission_csv": False,
            },
        )

        self.assertEqual(len(m.request_history), 3)

        object_create = m.last_request
        expected_record_data = {
            "summary": {
                step_slug: {
                    "voornaam": "&lt;script&gt;alert();&lt;/script&gt;",
                },
            },
            "manual_variable": "&lt;script&gt;alert();&lt;/script&gt;",
        }
        object_create_body = object_create.json()
        posted_record_data = object_create_body["record"]["data"]
        self.assertEqual(object_create.method, "POST")
        self.assertEqual(object_create.url, "https://objecten.nl/api/v1/objects")
        self.assertEqual(posted_record_data, expected_record_data)

    def test_submission_with_payment(self, m):
        submission = SubmissionFactory.from_components(
            [
                {
                    "key": "test",
                    "type": "textfield",
                },
            ],
            registration_success=True,
            submitted_data={"test": "some test data"},
            language_code="en",
            registration_result={
                "url": "https://objecten.nl/api/v1/objects/111-222-333"
            },
            form__payment_backend="demo",
            form__product__price=10,
        )
        SubmissionPaymentFactory.for_submission(
            submission=submission,
            status=PaymentStatus.started,
            public_order_id="",
        )

        m.post(
            "https://objecten.nl/api/v1/objects",
            status_code=201,
            json=get_create_json,
        )
        m.get(
            "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
            json={
                "url": "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377"
            },
            status_code=200,
        )
        m.post(
            "https://documenten.nl/api/v1/enkelvoudiginformatieobjecten",
            status_code=201,
            json=generate_oas_component(
                "documenten",
                "schemas/EnkelvoudigInformatieObject",
                url="https://documenten.nl/api/v1/enkelvoudiginformatieobjecten/1",
            ),
        )

        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)
        plugin.register_submission(
            submission,
            {
                "version": 1,
                "objects_api_group": self.objects_api_group,
                "objecttype": UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
                "objecttype_version": 1,
            },
        )

        self.assertEqual(len(m.request_history), 3)

        object_create = m.last_request
        body = object_create.json()

        self.assertEqual(
            body["record"]["data"]["payment"],
            {
                "completed": False,
                "amount": 10.00,
                "public_order_ids": [],
            },
        )

    def test_submission_with_auth_context_data(self, m):
        # skip document uploads
        self.objects_api_group.informatieobjecttype_submission_report = ""
        self.objects_api_group.save()
        submission = SubmissionFactory.create(
            completed=True,
            form__generate_minimal_setup=True,
            # simulate eherkenning bewindvoering, as that is most complex
            form__authentication_backends=["demo"],
            auth_info__plugin="demo",
            auth_info__is_eh_bewindvoering=True,
        )
        m.post(
            "https://objecten.nl/api/v1/objects", status_code=201, json=get_create_json
        )
        m.get(
            "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
            json={
                "url": "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377"
            },
            status_code=200,
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)
        plugin.register_submission(
            submission,
            {
                "version": 1,
                "objects_api_group": self.objects_api_group,
                "objecttype": UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
                "objecttype_version": 1,
                "informatieobjecttype_submission_report": "",
                "upload_submission_csv": False,
                "content_json": r"""{"auth": {% as_json variables.auth_context %}}""",
            },
        )

        object_create = m.last_request
        body = object_create.json()
        # for the values, see openforms.authentication.tests.factories.AuthInfoFactory
        expected = {
            "source": "eherkenning",
            # from auth info factory
            "levelOfAssurance": "urn:etoegang:core:assurance-class:loa3",
            "representee": {
                "identifierType": "bsn",
                "identifier": "999991607",
            },
            "authorizee": {
                "legalSubject": {
                    "identifierType": "kvkNummer",
                    "identifier": "90002768",
                },
                "actingSubject": {
                    "identifierType": "opaque",
                    "identifier": (
                        "4B75A0EA107B3D36C82FD675B5B78CC2F181B22E33D85F2D4A5DA6345"
                        "2EE3018@2D8FF1EF10279BC2643F376D89835151"
                    ),
                },
            },
            "mandate": {
                "role": "bewindvoerder",
                "services": [
                    {
                        "id": "urn:etoegang:DV:00000001002308836000:services:9113",
                        "uuid": "34085d78-21aa-4481-a219-b28d7f3282fc",
                    }
                ],
            },
        }
        self.assertEqual(body["record"]["data"]["auth"], expected)

    def test_submission_with_auth_context_data_not_authenticated(self, m):
        # skip document uploads
        self.objects_api_group.informatieobjecttype_submission_report = ""
        self.objects_api_group.save()
        submission = SubmissionFactory.create(
            completed=True,
            form__generate_minimal_setup=True,
        )
        assert not submission.is_authenticated
        m.post(
            "https://objecten.nl/api/v1/objects", status_code=201, json=get_create_json
        )
        m.get(
            "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377",
            json={
                "url": "https://objecttypen.nl/api/v1/objecttypes/f3f1b370-97ed-4730-bc7e-ebb20c230377"
            },
            status_code=200,
        )
        plugin = ObjectsAPIRegistration(PLUGIN_IDENTIFIER)
        plugin.register_submission(
            submission,
            {
                "version": 1,
                "objects_api_group": self.objects_api_group,
                "objecttype": UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
                "objecttype_version": 1,
                "informatieobjecttype_submission_report": "",
                "upload_submission_csv": False,
                "content_json": r"""{"auth": {% as_json variables.auth_context %}}""",
            },
        )

        object_create = m.last_request
        body = object_create.json()
        self.assertEqual(body["record"]["data"]["auth"], None)


class V1HandlerTests(TestCase):
    """
    Test V1 registration backend without actual HTTP calls.

    Test the behaviour of the V1 registration handler for producing record data to send
    to the Objects API.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        cls.group = ObjectsAPIGroupConfigFactory(
            objecttypes_service__api_root="https://objecttypen.nl/api/v2/",
        )

    def test_cosign_info_available(self):
        now = timezone.now().isoformat()

        submission = SubmissionFactory.from_components(
            [
                {
                    "key": "cosign",
                    "type": "cosign",
                    "validate": {"required": False},
                },
            ],
            completed=True,
            submitted_data={
                "cosign": "example@localhost",
            },
            cosign_complete=True,
            co_sign_data={
                "value": "123456789",
                "attribute": AuthAttribute.bsn,
                "cosign_date": now,
            },
        )

        ObjectsAPIRegistrationData.objects.create(submission=submission)
        v1_options: RegistrationOptionsV1 = {
            "objects_api_group": self.group,
            "version": 1,
            "objecttype": UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
            "objecttype_version": 1,
            "productaanvraag_type": "-dummy-",
            "content_json": textwrap.dedent(
                """
                {
                    "cosign_date": "{{ cosign_data.date.isoformat }}",
                    "cosign_bsn": "{{ cosign_data.bsn }}",
                    "cosign_kvk": "{{ cosign_data.kvk }}",
                    "cosign_pseudo": "{{ cosign_data.pseudo }}"
                }
                """
            ),
        }
        handler = ObjectsAPIV1Handler()

        record_data = handler.get_record_data(submission=submission, options=v1_options)

        data = record_data["data"]

        self.assertEqual(data["cosign_date"], now)
        self.assertEqual(data["cosign_bsn"], "123456789")
        self.assertEqual(data["cosign_kvk"], "")
        self.assertEqual(data["cosign_pseudo"], "")

    def test_cosign_info_not_available(self):
        submission = SubmissionFactory.from_components(
            [
                {
                    "key": "cosign",
                    "type": "cosign",
                    "validate": {"required": False},
                },
            ],
            completed=True,
            submitted_data={
                "cosign": "example@localhost",
            },
            cosign_complete=False,
        )

        ObjectsAPIRegistrationData.objects.create(submission=submission)
        v1_options: RegistrationOptionsV1 = {
            "objects_api_group": self.group,
            "version": 1,
            "objecttype": UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
            "objecttype_version": 1,
            "productaanvraag_type": "-dummy-",
            "content_json": textwrap.dedent(
                """
                {
                    {% if cosign_data %}
                    "cosign_date": "{{ cosign_data.date }}",
                    "cosign_bsn": "{{ cosign_data.bsn }}",
                    "cosign_kvk": "{{ cosign_data.kvk }}",
                    "cosign_pseudo": "{{ cosign_data.pseudo }}"
                    {% endif %}
                }
                """
            ),
        }
        handler = ObjectsAPIV1Handler()

        record_data = handler.get_record_data(submission=submission, options=v1_options)

        self.assertEqual(record_data["data"], {})

    def test_cosign_info_no_cosign_date(self):
        """The cosign date might not be available on existing submissions."""

        submission = SubmissionFactory.from_components(
            [
                {
                    "key": "cosign",
                    "type": "cosign",
                    "validate": {"required": False},
                },
            ],
            completed=True,
            submitted_data={
                "cosign": "example@localhost",
            },
            cosign_complete=True,
            co_sign_data={
                "value": "123456789",
                "attribute": AuthAttribute.bsn,
            },
        )

        ObjectsAPIRegistrationData.objects.create(submission=submission)
        v1_options: RegistrationOptionsV1 = {
            "objects_api_group": self.group,
            "version": 1,
            "objecttype": UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
            "objecttype_version": 1,
            "productaanvraag_type": "-dummy-",
            "content_json": textwrap.dedent(
                """
                {
                    "cosign_date": "{{ cosign_data.date }}"
                }
                """
            ),
        }
        handler = ObjectsAPIV1Handler()

        record_data = handler.get_record_data(submission=submission, options=v1_options)
        data = record_data["data"]

        self.assertEqual(data["cosign_date"], "")

    @tag("utrecht-243", "gh-4425")
    def test_payment_context_without_any_payment_attempts(self):
        submission = SubmissionFactory.create(
            completed=True,
            form__payment_backend="demo",
            form__product__price=10,
        )
        assert not submission.payments.exists()
        assert submission.price == 10
        ObjectsAPIRegistrationData.objects.create(submission=submission)
        options: RegistrationOptionsV1 = {
            "objects_api_group": self.group,
            "version": 1,
            "objecttype": UUID("f3f1b370-97ed-4730-bc7e-ebb20c230377"),
            "objecttype_version": 1,
            "productaanvraag_type": "-dummy-",
            "content_json": """{"amount": {{ payment.amount }}}""",
        }
        handler = ObjectsAPIV1Handler()

        record_data = handler.get_record_data(submission=submission, options=options)

        self.assertEqual(record_data["data"]["amount"], 10)

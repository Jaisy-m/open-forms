"""
Assert that the hijack funtionality works even with 2FA.
"""

from django.contrib.auth import SESSION_KEY
from django.test import TestCase, override_settings, tag
from django.urls import reverse

from django_webtest import WebTest

from openforms.logging.models import TimelineLogProxy

from .factories import StaffUserFactory, SuperUserFactory


@override_settings(
    TWO_FACTOR_PATCH_ADMIN=True,
    TWO_FACTOR_FORCE_OTP_ADMIN=True,
)
class HijackTests(WebTest):
    csrf_checks = False

    def _hijack_user(self, hijacked):
        url = reverse("hijack:acquire")
        response = self.app.post(
            url, {"user_pk": hijacked.pk, "next": reverse("admin:index")}
        )
        return response

    def test_can_hijack_and_release_with_2fa(self):
        staff_user = StaffUserFactory.create(app=self.app)
        superuser = SuperUserFactory.create(app=self.app)
        admin_dashboard_url = reverse("admin:index")

        with self.subTest("superuser admin index page"):
            admin_dashboard = self.app.get(admin_dashboard_url, user=superuser)

            self.assertEqual(admin_dashboard.status_code, 200)
            user_tools = admin_dashboard.pyquery("#user-tools").text()
            self.assertIn(superuser.username, user_tools)

        with self.subTest("superuser hijacks other user"):
            user_list = self.app.get(
                reverse("admin:accounts_user_changelist"), user=superuser
            )

            self.assertEqual(user_list.status_code, 200)

            hijack_buttons = user_list.pyquery(".field-hijack_field button")
            self.assertEqual(len(hijack_buttons), 2)  # one for each user
            # webtest button clicks are not possible, since they are handled by JS
            admin_dashboard = self._hijack_user(staff_user).follow()

            self.assertEqual(admin_dashboard.status_code, 200)
            user_tools = admin_dashboard.pyquery("#user-tools").text()
            self.assertIn(staff_user.username, user_tools)

        with self.subTest("release hijacked staff user"):
            djhj_message = admin_dashboard.pyquery(".djhj")
            self.assertEqual(len(djhj_message), 1)

            release_form = admin_dashboard.form

            response = release_form.submit()
            self.assertRedirects(
                response, reverse("admin:index"), fetch_redirect_response=False
            )
            # webtest has its own injected auth backend, and hijack trips on that for
            # follow-up requests. This is a robust way to check the hijacked user is released.
            self.assertEqual(
                self.app.session[SESSION_KEY],
                str(superuser.id),
                "Superuser is not restored after release",
            )

    def test_auditlog_entries_on_hijack_and_release(self):
        staff_user = StaffUserFactory.create(app=self.app)
        superuser = SuperUserFactory.create(app=self.app)

        with self.subTest("hijack user"):
            self.app.get(reverse("admin:index"), user=superuser)

            admin_dashboard = self._hijack_user(staff_user).follow()

            self.assertEqual(TimelineLogProxy.objects.count(), 1)
            log_hijack = TimelineLogProxy.objects.get()
            self.assertEqual(
                log_hijack.extra_data["hijacker"],
                {
                    "id": superuser.id,
                    "full_name": superuser.get_full_name(),
                    "username": superuser.username,
                },
            )
            self.assertEqual(
                log_hijack.extra_data["hijacked"],
                {
                    "id": staff_user.id,
                    "full_name": staff_user.get_full_name(),
                    "username": staff_user.username,
                },
            )

        with self.subTest("release user"):
            release_form = admin_dashboard.form
            release_form.submit()

            self.assertEqual(TimelineLogProxy.objects.count(), 2)
            log_release = TimelineLogProxy.objects.order_by("-id").first()
            self.assertEqual(
                log_release.extra_data["hijacker"],
                {
                    "id": superuser.id,
                    "full_name": superuser.get_full_name(),
                    "username": superuser.username,
                },
            )
            self.assertEqual(
                log_release.extra_data["hijacked"],
                {
                    "id": staff_user.id,
                    "full_name": staff_user.get_full_name(),
                    "username": staff_user.username,
                },
            )


@override_settings(
    TWO_FACTOR_PATCH_ADMIN=True,
    TWO_FACTOR_FORCE_OTP_ADMIN=True,
)
class HijackSecurityTests(TestCase):

    @tag("security-28", "CVE-2024-24771")
    def test_cannot_hijack_without_second_factor(self):
        staff_user = StaffUserFactory.create()
        superuser = SuperUserFactory.create()
        superuser.totpdevice_set.create()
        self.client.force_login(superuser)

        # sanity check - MFA is being enforced
        admin_index_response = self.client.get(reverse("admin:index"))
        assert (
            admin_index_response.status_code == 302
        ), "Non-verified user unexpected has access to the admin"

        # try the hijack
        acquire = self.client.post(
            reverse("hijack:acquire"),
            data={"user_pk": staff_user.pk},
        )

        with self.subTest("hijack blocked"):
            # bad request due to SuspiciousOperation or 403 from PermissionDenied
            self.assertIn(acquire.status_code, [400, 403])

        with self.subTest("release does not allow gaining verified state"):
            # release the user
            release = self.client.post(reverse("hijack:release"))

            with self.subTest("release blocked due to hijack not being acquired"):
                self.assertEqual(release.status_code, 403)

            with self.subTest("no access to admin gained"):
                # due to bypass via release action which sets up a device
                admin_response = self.client.get(reverse("admin:index"))

                self.assertNotEqual(admin_response.status_code, 200)

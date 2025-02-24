=========
Changelog
=========

2.7.0 "TBD" (2024-07-??)
========================

This release is in development, meaning it is not finished yet or suitable for
production use.

Upgrade notes
-------------

* ⚠️ The feature flag to disable backend validation is now removed, instances relying
  on it should verify that their existing forms works with the validation enforced.

* We're consolidating the OpenID Connect *Redirect URI* endpoints into a single
  endpoint: ``/auth/oidc/callback/``. The legacy endpoints are still enabled (by default),
  but scheduled for removal in Open Forms 3.0.

  You can already opt-in to the new behaviour through three environment variables:

  - ``USE_LEGACY_OIDC_ENDPOINTS=false``: admin login
  - ``USE_LEGACY_DIGID_EH_OIDC_ENDPOINTS=false``: DigiD/eHerkenning plugins
  - ``USE_LEGACY_ORG_OIDC_ENDPOINTS=false``: Organization OIDC plugin

  Note that the OpenID applications need to be updated on the identity provider,
  specifically the allowed "Redirect URIs" setting needs to be updated with the
  following path replacements:

  - ``/oidc/callback/`` -> ``/auth/oidc/callback/``
  - ``/digid-oidc/callback/`` -> ``/auth/oidc/callback/``
  - ``/eherkenning-oidc/callback/`` -> ``/auth/oidc/callback/``
  - ``/digid-machtigen-oidc/callback/`` -> ``/auth/oidc/callback/``
  - ``/eherkenning-bewindvoering-oidc/callback/`` -> ``/auth/oidc/callback/``
  - ``/org-oidc/callback/`` -> ``/auth/oidc/callback/``

2.6.11 (2024-06-20)
===================

Hotfix for payment integration in Objects API

* [#4425] Fixed the wrong price being sent to the Objects API when multiple payment
  attempts are made.
* [#4425] Fixed incorrectly marking failed/non-completed payment attempts as registered
  in the registration backend.
* [#4425] Added missing (audit) logging for payments started from the confirmation
  email link.

2.5.11 (2024-06-20)
===================

Hotfix for payment integration in Objects API

* [#4425] Fixed the wrong price being sent to the Objects API when multiple payment
  attempts are made.
* [#4425] Fixed incorrectly marking failed/non-completed payment attempts as registered
  in the registration backend.
* [#4425] Added missing (audit) logging for payments started from the confirmation
  email link.

2.6.10 (2024-06-19)
===================

Hotfix fixing a regression in the PDF generation.

* [#4403] Fixed broken submission PDF layout when empty values are present.
* [#4409] Updated language used for payment amount in submission PDF.

2.5.10 (2024-06-19)
===================

Hotfix fixing a regression in the PDF generation.

* [#4403] Fixed broken submission PDF layout when empty values are present.
* [#4409] Updated language used for payment amount in submission PDF.

2.4.10 (2024-06-19)
===================

Final bugfix release in the ``2.4.x`` series.

* [#4403] Fixed broken submission PDF layout when empty values are present.

2.6.9 (2024-06-14)
==================

Bugfix release fixing some issues (still) in 2.6.8

* [#4338] Fixed prefill for StUF-BG with SOAP 1.2 not properly extracting attributes.
* [#4390] Fixed regression introduced by #4368 that would break template variables in
  hyperlinks inside WYSIWYG content.

2.6.8 (2024-06-14)
==================

Bugfix release

* [#4255] Fixed a performance issue in the confirmation PDF generation when large
  blocks of text are rendered.
* [#4241] Fixed some backend validation being skipped when there is component key
  overlap with layout components (like fieldsets and columns).
* [#4368] Fixed URLs to the same domain being broken in the WYSIWYG editors.
* [#4377] Added support for pre-request context/extensions in BRK client
  implementation.
* [#4363] Fixed option descriptions not being translated for radio and selectboxes
  components.
* [#4362] Fixed a crash in the form designer when a textfield/textarea allows multiple
  values in forms with translations enabled.

2.5.9 (2024-06-14)
==================

Bugfix release fixing some issues (still) in 2.5.8

Note that 2.5.8 was never published to Docker Hub.

* [#4338] Fixed prefill for StUF-BG with SOAP 1.2 not properly extracting attributes.
* [#4390] Fixed regression introduced by #4368 that would break template variables in
  hyperlinks inside WYSIWYG content.

2.5.8 (2024-06-14)
==================

Bugfix release

* [#4255] Fixed a performance issue in the confirmation PDF generation when large
  blocks of text are rendered.
* [#4368] Fixed URLs to the same domain being broken in the WYSIWYG editors.
* [#4362] Fixed a crash in the form designer when a textfield/textarea allows multiple
  values in forms with translations enabled.

2.4.9 (2024-06-14)
==================

Bugfix release fixing some issues (still) in 2.4.8

Note that 2.4.8 was never published to Docker Hub.

* [#4338] Fixed prefill for StUF-BG with SOAP 1.2 not properly extracting attributes.
* [#4390] Fixed regression introduced by #4368 that would break template variables in
  hyperlinks inside WYSIWYG content.

2.4.8 (2024-06-14)
==================

Bugfix release

* [#4255] Fixed a performance issue in the confirmation PDF generation when large
  blocks of text are rendered.
* [#4368] Fixed URLs to the same domain being broken in the WYSIWYG editors.
* [#4362] Fixed a crash in the form designer when a textfield/textarea allows multiple
  values in forms with translations enabled.

2.6.7 (2024-05-22)
==================

Bugfix release

* [:backend:`3807`] Made the co-sign request email template configurable.
* [:backend:`4302`] Made co-sign data (date and co-sign attribute) available in the Objects API registration.

2.6.6 (2024-05-13)
==================

Bugfix release

* [:backend:`4146`] Fixed SOAP timeout not being used for Stuf-ZDS client.
* [:backend:`4205`] The CSP ``form-action`` directive now allows any ``https:`` target,
  to avoid errors on eHerkenning login redirects.
* [:backend:`4269`] Fixed DMN integration for real-world decision definitions.

2.5.7 (2024-05-13)
==================

Bugfix release

* [:backend:`4052`] Fixed payment (reminder) emails being sent more often than intended.
* [:backend:`4124`] Fixed forms being shown multiple times in the admin list overview.
* [:backend:`3964`] Toggling visibility with frontend logic and number/currency components leads to fields being emptied.
* [:backend:`4205`] The CSP ``form-action`` directive now allows any ``https:`` target,
  to avoid errors on eHerkenning login redirects.

2.4.7 (2024-05-13)
==================

Bugfix release

* [:backend:`4079`] Fixed metadata retrieval for DigiD failing when certificates signed by the G1 root are used.
* [:backend:`4103`] Fixed incorrect appointment details being included in the submission PDF.
* [:backend:`4145`] Fixed the payment status not being registered correctly for StUF-ZDS.
* [:backend:`3964`] Toggling visibility with frontend logic and number/currency components leads to fields being emptied.
* [:backend:`4205`] The CSP ``form-action`` directive now allows any ``https:`` target,
  to avoid errors on eHerkenning login redirects.

2.7.0-alpha.0 (2024-05-06)
==========================

This is an alpha release, meaning it is not finished yet or suitable for production use.

Detailed changes
----------------

**New features**

* Improved backend validation robustness, mainly by validating new components:

   - [:backend:`72`] Improved validation for the following components: time, selectboxes, textarea, postcode, bsn, select, checkbox,
     currency, signature, map, cosign, password, iban and licenseplate.


* Submission registration:

   - [:backend:`4031`] Added a warning for the Objects API registration configuration when switching back to the legacy configuration.
   - [:backend:`4041`] Improved robustness of document registration in the Documents API.

Other features:

* [:backend:`3969`] For eHerkenning/eIDAS authentication, the level of assurance can no longer be overridden (as brokers do not support this).
* [:backend:`4009`] Improved the representation of submission data in the admin interface.
* [:backend:`4005`] Added the ability to search submission reports by public registration reference and submission in the admin.
* [:backend:`4005`] Updated title of the PDF submission report to include the public registration reference.
* [:backend:`3725`] Expanded email digest by detecting more problems in features actively used, such as:

   - Submissions with failed registration status.
   - Prefill plugins failures.
   - Missing or wrong BRK client configuration.
   - Address autofill (based on postal code and house numer) misconfiguration.
   - Form logic rules referring to non-existent fields.
   - Invalid registration backends configuration.
   - ZGW services: Mutual TLS certificates/certificate pairs and (nearly) expired certificates.

* [:backend:`3889`] You can now export the audit trails and GDPR log entries.
* [:backend:`3889`] Viewing an outgoing request log entry in the admin will now create a GDPR log entry.
* [:backend:`4101`] The "Show form" button in the admin is now only displayed for active forms.
* [:backend:`4080`] Added generation timestamp to PDF submission report.
* [:backend:`4215`] Email logs older than 90 days are now periodically deleted.
* [:backend:`4229`] Improved performance of KVK number validation.

**Bugfixes**

* Fixed more backend validation issues:

   - [:backend:`4065`] Hidden fields/components are not longer taken into account during backend validation.
   - [:backend:`4068`] Fixed various backend validation issues:

      * Allow empty string as empty value for date field.
      * Don't reject textfield (and derivatives) with multiple=True when
        items inside are null (treat them as empty value/string).
      * Allow empty lists for edit grid/repeating group when field is
        not required.
      * Skip validation for layout components, they never get data.
      * Ensure that empty string values for optional text fields are
        allowed (also covers derived fields).
      * Fixed validation error being returned that doesn't point to
        a particular component.
      * Fixed validation being run for form steps that are (conditionally) marked as
        "not applicable".

   - [:backend:`4126`] Fixed incorrect validation of components inside repeating groups that are
     conditionally visible (with frontend logic).
   - [:backend:`4143`] Added additional backend validation: now when form step data is being saved
     (including pausing a form), the values are validated against the component
     configuration too.
   - [:backend:`4151`] Fixed backend validation error being triggered for radio/select/selectboxes
     components that get their values/options from another variable.
   - [:backend:`4172`] Fixed a crash while running input validation on date fields when min/max date
     validations are specified.
   - [DH#671] Fixed conditionally making components required/optional via backend logic.
   - Fixed validation of empty/optional select components.
   - [:backend:`4096`] Fixed validation of hidden (with ``clearOnHide: false``) radio components.
   - [DH#667] Fixed components inside a repeating group causing validation issues when
     they are nested inside a fieldset or columns.



* [:backend:`4069`] Fixed a crash in the form designer when navigating to the variables tab if you
  use any of the following registration backends: email, MS Graph (OneDrive/Sharepoint)
  or StUF-ZDS.
* [:backend:`4061`] Fixed not all form components being visible in the form builder when other
  components can be selected.
* [:backend:`4079`] Fixed metadata retrieval for DigiD failing when certificates signed by the G1
  root are used.
* [:backend:`4099`] Fixed a crash in the form designer when editing (user defined) variables and
  the template-based Objects API registration backend is configured.
* [:backend:`4103`] Fixed incorrect appointment details being included in the submission PDF.
* [:backend:`4073`] Removed unused StUF-ZDS 'gemeentecode'.
* [:backend:`4015`] Fixed possible traversal attack in service fetch service.
* [:backend:`4084`] Fixed default values of select components set to multiple.
* [:backend:`4134`] Fixed form designer admin crashes when component/variable keys are edited.
* [:backend:`4131`] Fixed bug where component validators all had to be valid rather than at least
  one.
* [:backend:`4072`] Fixed recovery token flow redirecting back to login screen, making it impossible to use recovery tokens.
* [:backend:`4145`] Fixed the payment status not being registered correctly for StUF-ZDS.
* [:backend:`4124`] Fixed forms being shown multiple times in the admin list overview.
* [:backend:`4052`] Fixed payment (reminder) emails being sent more often than intended.
* [:backend:`4156`] Fixed the format of order references sent to payment providers. You can now
  provide your own template.
* [:backend:`4141`] Fixed a crash in the Objects API registration when using periods in component
  keys.
* [:backend:`4165`] A cookie consent group for analytics is now required.
* [:backend:`4187`] Selectboxes/radio with dynamic options are considered invalid when submitting the form.
* [:backend:`4202`] Fixed Objects API registration v2 crash with hidden fields.
* [:backend:`4115`] Support different kinds of GovMetric feedback (aborting the form vs. completing the form).
* [:backend:`4197`] Ensured all uploaded images are being resized if necessary.
* [:backend:`4191`] Added missing required ``aoaIdentificatie`` field to ZGW registration.
* [:backend:`4173`] Fixed registration backends not being included when copying a form.
* [:backend:`4146`] Fixed SOAP timeout not being used for Stuf-ZDS client.
* [:backend:`3964`] Toggling visibility with frontend logic and number/currency components leads to fields being emptied.
* [:backend:`4247`] Fixed migration crash because of particular key-structure with repeating groups.
* [:backend:`4174`] Fixed submission pre-registration being stuck in a loop when failing to do so.

**Project maintenance**

* [:backend:`4035`] Added an E2E test for the file component.
* Cleaned up logging config: removed unused performance logging config, added tools to mute logging.
* Cleaned up structure of local setting overrides.
* [:backend:`4057`] Upgraded to ``zgw-consumers`` 0.32.0. This drops the dependency on ``gemma-zds-client``.
* Vendored ``decorator-include``, as it is not maintained anymore.
* Updated dependencies to drop ``setuptools``.
* [:backend:`3878`] Updated some dependencies after the Django 4.2 upgrade.
* Switched to Docker Compose V2 in CI, as V1 was removed from Github Ubuntu images.
* Moved EOL changelog to archive.
* Ordered changelog entries by version instead of date in archive.
* Added feature to log flaky tests in CI.
* Documented versioning policy change.
* Used ``uv`` to install dependencies in Docker build.
* Improved release process documentation.
* [:backend:`3878`] Updated docs dependencies.
* Added PR checklist template.
* [:backend:`4009`, :backend:`979`] Removed the ``get_merged_data`` of the submission model.
* [:backend:`4044`] Improved developer documentation of submission state and component configuration.
* [:backend:`3878`] Updated to the latest version of ``django-yubin``, removed the temporary patch.
* [:backend:`3878`] Updated to the latest version of ``celery``, including related dependencies.
* [:backend:`4247`] Improved robustness of the ``FormioConfigurationWrapper`` with editgrids.
* [:backend:`4236`] Removed form copy API endpoint, as it is not used anymore.

2.6.5 (2024-04-24)
==================

Bugfix release

* [:backend:`4165`] A cookie consent group for analytics is now required.
* [:backend:`4115`] Added new source ID and secure GUID.
* [:backend:`4202`] Fixed Objects API registration v2 crash with hidden fields.

2.6.5-beta.0 (2024-04-17)
=========================

Bugfix beta release

* [:backend:`4186`] Fix for "client-side logic" in the formio-builder cleared existing values.
* [:backend:`4187`] Selectboxes/radio with dynamic options are considered invalid when submitting the form.
* [:backend:`3964`] Toggling visibility with frontend logic and number/currency components leads to fields being emptied.

2.6.4 (2024-04-16)
==================

Bugfix release

* [:backend:`4151`] Fixed backend validation error being triggered for radio/select/selectboxes
  components that get their values/options from another variable.
* [:backend:`4052`] Fixed payment (reminder) emails being sent more often than intended.
* [:backend:`4124`] Fixed forms being shown multiple times in the admin list overview.
* [:backend:`4156`] Fixed the format of order references sent to payment providers. You can now
  provide your own template.
* Fixed some bugs in the form builder:

    - Added missing error message codes (for translations) for the selectboxes component.
    - Fixed the "client-side logic" to take the correct data type into account.
    - Fixed the validation tab not being marked as invalid in some validation error
      situations.

* Upgraded some dependencies with their latest (security) patches.
* [:backend:`4172`] Fixed a crash while running input validation on date fields when min/max date
  validations are specified.
* [:backend:`4141`] Fixed a crash in the Objects API registration when using periods in component
  keys.

2.6.3 (2024-04-10)
==================

Bugfix release following feedback on 2.6.2

* [:backend:`4126`] Fixed incorrect validation of components inside repeating groups that are
  conditionally visible (with frontend logic).
* [:backend:`4134`] Fixed form designer admin crashes when component/variable keys are edited.
* [:backend:`4131`] Fixed bug where component validators all had to be valid rather than at least
  one.
* [:backend:`4140`] Added deploy configuration parameter to not send hidden field values to the
  Objects API during registration, restoring the old behaviour. Note that this is a
  workaround and the correct behaviour (see ticket #3890) will be enforced from Open
  Forms 2.7.0 and newer.
* [:backend:`4072`] Fixed not being able to enter an MFA recovery token.
* [:backend:`4143`] Added additional backend validation: now when form step data is being saved (
  including pausing a form), the values are validated against the component
  configuration too.
* [:backend:`4145`] Fixed the payment status not being registered correctly for StUF-ZDS.

2.5.6 (2024-04-10)
==================

Hotfix release for StUF-ZDS users.

* [:backend:`4145`] Fixed the payment status not being registered correctly for StUF-ZDS.

2.6.2 (2024-04-05)
==================

Bugfix release - not all issues were fixed in 2.6.1.

* Fixed various more mismatches between frontend and backend input validation:

    - [DH#671] Fixed conditionally making components required/optional via backend logic.
    - Fixed validation of empty/optional select components.
    - [:backend:`4096`] Fixed validation of hidden (with ``clearOnHide: false``) radio components.
    - [DH#667] Fixed components inside a repeating group causing validation issues when
      they are nested inside a fieldset or columns.

* [:backend:`4061`] Fixed not all form components being visible in the form builder when other
  components can be selected.
* [:backend:`4079`] Fixed metadata retrieval for DigiD failing when certificates signed by the G1
  root are used.
* [:backend:`4103`] Fixed incorrect appointment details being included in the submission PDF.
* [:backend:`4099`] Fixed a crash in the form designer when editing (user defined) variables and
  the template-based Objects API registration backend is configured.
* Update image processing library with latest security fixes.
* [DH#673] Fixed wrong datatype for field empty value being sent in the Objects API
  registration backend when the field is not visible.
* [DH#673] Fixed fields hidden because the parent fieldset or column is hidden not being
  sent to the Objects API. This is a follow up of :backend:`3980`.

2.5.5 (2023-04-03)
==================

Hotfix release for appointments bug

* [:backend:`4103`] Fixed incorrect appointment details being included in the submission PDF.
* [:backend:`4079`] Fixed metadata retrieval for DigiD failing when certificates signed by the G1
  root are used.
* [:backend:`4061`] Fixed not all form components being visible in the form builder when other
  components can be selected.
* Updated dependencies to their latest security releases.

2.6.1 (2024-03-28)
==================

Hotfix release

A number of issues were discovered in 2.6.0, in particular related to the additional
validation performed on the backend.

* [:backend:`4065`] Fixed validation being run for fields/components that are (conditionally)
  hidden. The behaviour is now consistent with the frontend.
* [:backend:`4068`] Fixed more backend validation issues:

    * Allow empty string as empty value for date field.
    * Don't reject textfield (and derivatives) with multiple=True when
      items inside are null (treat them as empty value/string).
    * Allow empty lists for edit grid/repeating group when field is
      not required.
    * Skip validation for layout components, they never get data.
    * Ensure that empty string values for optional text fields are
      allowed (also covers derived fields).
    * Fixed validation error being returned that doesn't point to
      a particular component.
    * Fixed validation being run for form steps that are (conditionally) marked as
      "not applicable".

* [:backend:`4069`] Fixed a crash in the form designer when navigating to the variables tab if you
  use any of the following registration backends: email, MS Graph (OneDrive/Sharepoint)
  or StUF-ZDS.

2.6.0 "Traiectum" (2024-03-25)
==============================

Open Forms 2.6.0 is a feature release.

.. epigraph::

   Traiectum is the name of a Roman Fort in Germania inferior, what is currently
   modern Utrecht. The remains of the fort are in the center of Utrecht.

Upgrade notes
-------------

* Ensure you upgrade to (at least) Open Forms 2.5.2 before upgrading to 2.6.

* ⚠️ The ``CSRF_TRUSTED_ORIGINS`` setting now requires items to have a scheme. E.g. if
  you specified this as ``example.com,cms.example.com``, then the value needs to be
  updated to ``https://example.com,https://cms.example.com``.

  Check (and update) your infrastructure code/configuration for this setting before
  deploying.

* The Objects API registration backend can now update the payment status after
  registering an object. For this feature to work, the minimum version of the Objects
  API is now ``v2.2`` (raised from ``v2.0``). If you don't make use of payments or don't
  store payment information in the object, you can likely keep using older versions, but
  this is at your own risk.

* The ``TWO_FACTOR_FORCE_OTP_ADMIN`` and ``TWO_FACTOR_PATCH_ADMIN`` environment variables
  are removed, you can remove them from your infrastructure configuration. Disabling MFA
  in the admin is no longer possible. Note that the OpenID Connect login backends do not
  require (additional) MFA in the admin and we've added support for hardware tokens
  (like the YubiKey) which make MFA less of a nuisance.

Major features
--------------

**📄 Objects API contract**

We completely revamped our Objects API registration backend - there is now tight
integration with the "contract" imposed by the selected object type. This makes it
much more user friendly to map form variables to properties defined in the object type.

The existing template-based approach is still available, giving you plenty of time to
convert existing forms. It is not scheduled for removal yet.

**👔 Decision engine (DMN) support**

At times, form logic can become very complex to capture all the business needs. We've
added support for evaluation of "Decision models" defined in a decision evaluation
engine, such as Camunda DMN. This provides a better user experience for the people
modelling the decisions, centralizes the definitions and gives more control to the
business, all while simplifying the form logic configuration.

Currently only Camunda 7 is supported, and using this feature requires you to have
access to a Camunda instance in your infrastructure.

**🔑 Multi-factor rework**

We've improved the login flow for staff users by making it more secure *and* removing
friction:

* users of OIDC authentication never have to provide a second factor in Open Forms
* you can now set up an automatic redirect to the OIDC-provider, saving a couple of
  clicks
* users logging in with username/password can now use hardware tokens (like YubiKey),
  as an alternative one-time-password tokens (via apps like Google/Microsoft
  Authenticator)

**🔓 Added explicit, public API endpoints**

We've explicitly divided up our API into public and private parts, and this is reflected
in the URLs. Public API endpoints can be used by CMS integrations to present lists of
available forms, for example. Public API endpoints are subject to semantic versioning,
i.e. we will not introduce breaking changes without bumping the major version.

Currently there are public endpoints for available form categories and available forms.
The existing, private, API endpoints will continue to work for the foreseeable future
to give integrations time to adapt. The performance of these endpoints is now optimized
too.

The other API endpoints are private unless documented otherwise. They are *not* subject
to our semantic versioning policy anymore, and using these is at your own risk. Changes
will continue to be documented in the release notes.

Detailed changes
----------------

The 2.6.0-alpha.0 changes are included as well, see the earlier changelog entry.

**New features**

* [:backend:`3688`] Objects API registration rework

    - Added support for selecting an available object type/version in a dropdown instead
      of copy-pasting a URL.
    - The objecttype definition (JSON-schema) is processed and will be used for validation.
    - Registration configuration is specified on the "variables" tab for each available
      (built-in or user-defined) variable, where you can select the appropriate object
      type property in a dropdown.
    - Added the ability to explicitly map a file upload variable into a specific object
      property for better data quality.
    - Ensured that the legacy format is still available (100% backwards compatible).

* [:backend:`3855`] Improved user experience of DMN integration

    - The available input/output parameters can now be selected in a dropdown instead of
      entering them manually.
    - Added robustness in case the DMN engine is not available.
    - Added caching of DMN evaluation results.
    - Automatically select the only option if there's only one.

* Added documentation on how to configure Camunda for DMN.
* Tweaked the dark-mode styling of WYSIWYG editors to better fit in the page.
* [:backend:`3164`] Added explicit timeout fields to services so they can be different from the
  global default.
* [:backend:`3695`] Improved login screen and flow

    - Allow opt-in to automatically redirect to OIDC provider.
    - Support WebAuthn (like YubiKey) hardware tokens.

* [:backend:`3885`] The admin form list now keeps track of open/collapsed form categories.
* [:backend:`3957`] Updated the eIDAS logo.
* [:backend:`3825`] Added a well-performing public API endpoint to list available forms, returning
  only minimal information.
* [:backend:`3825`] Added public API endpoint to list available form categories.
* [:backend:`3879`] Added documentation on how to add services for the service fetch feature.
* [:backend:`3823`] Added more extensive documentation for template filters, field regex validation
  and integrated this documentation more into the form builder.
* [:backend:`3950`] Added additional values to the eHerkenning CSP-header configuration.
* [:backend:`3977`] Added additional validation checks on submission completion of the configured
  formio components in form steps.
* [:backend:`4000`] Deleted the 'save and add another' button in the form designer to maintain safe
  blood pressure levels for users who accidentally clicked it.

**Bugfixes**

* [:backend:`3672`] Fixed the handling of object/array variable types in service fetch configuration.
* [:backend:`3890`] Fixed visually hidden fields not being sent to Objects API registration backend.
* [:backend:`1052`] Upgraded DigiD/eHerkenning library.
* [:backend:`3924`] Fixed updating of payment status when the "registration after payment is
  received" option is enabled.
* [:backend:`3909`] Fixed a crash in the form designer when you use the ZGW registration plugin
  and remove a variable that is mapped to a case property ("Zaakeigenschap").
* [:backend:`3921`] Fixed not all (parent/sibling) components being available for selection in the
  form builder.
* [:backend:`3922`] Fixed a crash because of invalid prefill configuration in the form builder.
* [:backend:`3958`] Fixed the preview appearance of read-only components.
* [:backend:`3961`] Reverted the merged KVK API services (basisprofiel, zoeken) back into separate
  configuration fields. API gateways can expose these services on different endpoints.
* [:backend:`3705`] Fixed the representation of timestamps (again).
* [:backend:`3975`, :backend:`3052`] Fixed legacy service fetch configuration being picked over the intended
  format.
* [:backend:`3881`] Fixed updating a re-usable form definition in one form causing issues in other
  forms that also use this same form definition.
* [:backend:`4022`] Fix crash on registration handling of post-payment registration. The patch for
  :backend:`3924` was bugged.
* [:backend:`2827`] Worked around an infinite loop when assigning the variable ``now`` to a field
  via logic.
* [:backend:`2828`] Fixed a crash when assigning the variable ``today`` to a variable via logic.

**Project maintenance**

* Removed the legacy translation handling which became obsolete with the new form builder.
* [:backend:`3049`] Upgraded the Django framework to version 4.2 (LTS) to guarantee future
  security and stability updates.
* Bumped dependencies to pull in their latest security/patch updates.
* Removed stale data migrations, squashed migrations and cleaned up old squashed migrations.
* [:backend:`851`] Cleaned up ``DocumentenClient`` language handling.
* [:backend:`3359`] Cleaned up the registration flow and plugin requirements.
* [:backend:`3735`] Updated developer documentation about pre-request clients.
* [:backend:`3838`] Divided the API into public and private API and their implied versioning
  policies.
* [:backend:`3718`] Removed obsolete translation data store.
* [:backend:`4006`] Added utility to detect KVK integration via API gateway.
* [:backend:`3931`] Remove dependencies on PyOpenSSL.

2.5.4 (2024-03-19)
==================

Hotfix release to address a regression in 2.5.3

* [:backend:`4022`] Fix crash on registration handling of post-payment registration. The patch for
  :backend:`3924` was bugged.

2.5.3 (2024-03-14)
==================

Bugfix release

* [:backend:`3863`] Fixed the generated XML for StUF-BG requests when retrieving partners/children.
* [:backend:`3920`] Fixed not being able to clear some dropdows in the new form builder (advanced
  logic, WYSIWYG content styling).
* [:backend:`3858`] Fixed a race condition that would manifest during parallel file uploads,
  leading to permission errors.
* [:backend:`3864`] Fixed handling of StUF-BG responses where one partner is returned.
* [:backend:`1052`] Upgraded DigiD/eHerkenning library.
* [:backend:`3924`] Fixed updating of payment status when the "registration after payment is
  received" option is enabled.
* [:backend:`3921`] Fixed not all (parent/sibling) components being available for selection in the
  form builder.
* [:backend:`3922`] Fixed a crash because of invalid prefill configuration in the form builder.
* [:backend:`3975`, :backend:`3052`] Fixed legacy service fetch configuration being picked over the intended
  format.
* [:backend:`3881`] Fixed updating a re-usable form definition in one form causing issues in other
  forms that also use this same form definition.

2.4.6 (2024-03-14)
==================

Bugfix release

* [:backend:`3863`] Fixed the generated XML for StUF-BG requests when retrieving partners/children.
* [:backend:`3858`] Fixed a race condition that would manifest during parallel file uploads,
  leading to permission errors.
* [:backend:`3864`] Fixed handling of StUF-BG responses where one partner is returned.
* [:backend:`1052`] Upgraded DigiD/eHerkenning library.
* [:backend:`3975`, :backend:`3052`] Fixed legacy service fetch configuration being picked over the intended
  format.
* [:backend:`3881`] Fixed updating a re-usable form definition in one form causing issues in other
  forms that also use this same form definition.

2.6.0-alpha.0 (2024-02-20)
==========================

This is an alpha release, meaning it is not finished yet or suitable for production use.

Warnings
--------

**Objects API**

The Objects API registration backend can now update the payment status after registering
an object - this depends on a version of the Objects API with the PATCH method fixes. At
the time of writing, such a version has not been released yet.

.. todo:: At release time (2.6.0), check if we need to gate this functionality behind a
   feature flag to prevent issues.

If you would like information about the payment to be sent to the Object API registration
backend when the user submits a form, you can add a ``payment`` field to the
``JSON content template`` field in the settings for the Object API registration backend.
For example, if the ``JSON content template`` was:

.. code-block::

   {
     "data": {% json_summary %},
     "type": "{{ productaanvraag_type }}",
     "bsn": "{{ variables.auth_bsn }}",
     "pdf_url": "{{ submission.pdf_url }}",
     "submission_id": "{{ submission.kenmerk }}",
     "language_code": "{{ submission.language_code }}"
   }

It could become:

.. code-block::

  {
     "data": {% json_summary %},
     "type": "{{ productaanvraag_type }}",
     "bsn": "{{ variables.auth_bsn }}",
     "pdf_url": "{{ submission.pdf_url }}",
     "submission_id": "{{ submission.kenmerk }}",
     "language_code": "{{ submission.language_code }}"
     "payment": {
         "completed": {% if payment.completed %}true{% else %}false{% endif %},
         "amount": {{ payment.amount }},
         "public_order_ids":  {{ payment.public_order_ids }}
     }
  }

**Two factor authentication**

The ``TWO_FACTOR_FORCE_OTP_ADMIN`` and ``TWO_FACTOR_PATCH_ADMIN`` environment variables
are removed. Disabling MFA in the admin is no longer possible. Note that the OpenID
Connect login backends do not require (additional) MFA in the admin and we've added
support for hardware tokens (like the YubiKey) which make MFA less of a nuisance.

Detailed changes
----------------

**New features**

* [:backend:`713`] Added JSON-template support for payment status update in the Objects API.
* [:backend:`3783`] Added minimal statistics for form submissions in the admin.
* [:backend:`3793`] Reworked the payment reference number generation to include the submission
  reference.
* [:backend:`3680`] Removed extraneous authentication plugin configuration on cosign V2 component.
* [:backend:`3688`] Added plumbing for improved objects API configuration to enforce data-constracts
  through json-schema validation. This is very work-in-progress.
* [:backend:`3730`] Added DMN-capabilities to our logic engine. You can now evaluate a Camunda
  decision definition and use the outputs for further form logic control.
* [:backend:`3600`] Added support for mapping form variables to case properties in the ZGW API's
  registration backend.
* [:backend:`3049`] Reworked the two-factor solution. You can now enforce 2FA for username/password
  accounts while not requiring this when authenticating through OpenID Connect.
* Added support for WebAuthn-compatible 2FA hardware tokens.
* [:backend:`2617`] Reworked the payment flow to only enter payment mode if the price is not zero.
* [:backend:`3727`] Added validation for minimum/maximum number of checked options in the selectboxes
  component.
* [:backend:`3853`] Added support for the KVK-Zoeken API v2.0. V1 is deprecated and will be shut
  down this year.

**Bugfixes**

* [:backend:`3809`] Fixed a crash when viewing a non-existing submission via the admin.
* [:backend:`3616`] Fixed broken PDF template for appointment data.
* [:backend:`3774`] Fixed dark-mode support in new form builder.
* [:backend:`3382`] Fixed translation warnings for date and datetime placeholders in the form
  builder.
* [:cve:`CVE-2024-24771`] Fixed (non-exploitable) multi-factor authentication weakness.
* [:backend:`3623`] Fixed some OpenID Connect compatibility issues with certain providers.
* [:backend:`3863`] Fixed the generated XML for StUF-BG requests when retrieving partners/children.
* [:backend:`3864`] Fixed handling of StUF-BG responses where one partner is returned.
* [:backend:`3858`] Fixed a race condition that would manifest during parallel file uploads,
  leading to permission errors.
* [:backend:`3822`] Fixed searching in form versions admin.

**Project maintenance**

* Updated to Python 3.10+ typing syntax.
* Update contributing documentation regarding type annotations.
* [:backend:`3806`] Added email field to customer detail fields for demo appointments plugin.
* Updated CI action versions to use the latest NodeJS version.
* [:backend:`3798`] Removed unused ``get_absolute_url`` in the form definition model.
* Updated to black version 2024.
* [:backend:`3049`] More preparations to upgrade to Django 4.2 LTS.
* [:backend:`3616`] Added docker-compose setup for testing SDK embedding.
* [:backend:`3709`] Improved documentation for embedding forms.
* [:backend:`3239`] Removed logic rule evaluation logging as it was incomplete and not very usable.
* Cleaned up some test helpers after moving them into libraries.
* Upgraded external librariesto their newest (security) releases.

2.5.2 (2024-02-06)
==================

Bugfix release

This release addresses a security weakness. We believe there was no way to actually
exploit it.

* [:cve:`CVE-2024-24771`] Fixed (non-exploitable) multi-factor authentication weakness.
* [:sdk:`642`] Fixed DigiD error message via SDK patch release.
* [:backend:`3774`] Fixed dark-mode support in new form builder.
* Upgraded dependencies to their latest available security releases.

2.4.5 (2024-02-06)
==================

Bugfix release

This release addresses a security weakness. We believe there was no way to actually
exploit it.

* [:cve:`CVE-2024-24771`] Fixed (non-exploitable) multi-factor authentication weakness.
* [:sdk:`642`] Fixed DigiD error message via SDK patch release.
* Upgraded dependencies to their latest available security releases.

2.5.1 (2024-01-30)
==================

Hotfix release to address an upgrade problem.

* Included missing UI code for GovMetric analytics.
* Fixed a broken migration preventing upgrading to 2.4.x and newer.
* [:backend:`3616`] Fixed broken PDF template for appointment data.

2.4.4 (2024-01-30)
==================

Hotfix release to address an upgrade problem.

* Bump packages to their latest security releases
* [:backend:`3616`] Fixed broken PDF template for appointment data.
* Fixed a broken migration preventing upgrading to 2.4.x.

2.5.0 "Noaberschap" (2024-01-24)
================================

Open Forms 2.5.0 is a feature release.

.. epigraph::

   Noaberschap of naoberschap bunt de gezamenleke noabers in ne kleine sociale,
   oaverweagend agrarische samenleaving. Binnen den noaberschap besteet de noaberplicht.
   Dit höldt de verplichting in, dat de noabers mekare bi-j mot stoan in road en doad as
   dat neudig is. Et begrip is veural bekand in den Achterhook, Twente Salland en
   Drenthe, moar i-j kunt et eavenens in et westen van Duutslaand vinden (Graofschap
   Bentheim en umgeaving).

   -- definition in Achterhoeks, Dutch dialect

Upgrade procedure
-----------------

* ⚠️ Ensure you upgrade to Open Forms 2.4.0 before upgrading to the 2.5 release series.

* ⚠️ Please review the instructions in the documentation under **Installation** >
  **Upgrade details to Open Forms 2.5.0** before and during upgrading.

* We recommend running the ``bin/report_component_problems.py`` script to diagnose any
  problems in existing form definitions. These will be patched up during the upgrade,
  but it's good to know which form definitions will be touched in case something looks
  odd.

* Existing instances need to enable the new formio builder feature flag in the admin
  configuration.

Major features
--------------

**🏗️ Form builder rework**

We have taken lessons from the past into account and decided to implement our form
builder from the ground up so that we are not limited anymore by third party limitations.

The new form builder looks visually (mostly) the same, but the interface is a bit snappier
and much more accessible. Most importantly for us, it's now easier to change and extend
functionalities.

There are some further implementation details that have not been fully replaced yet,
but those do not affect the available functionality. We'll keep improving on this topic!

**🌐 Translation improvements**

Doing the form builder rework was crucial to be able to improve on our translation
machinery of form field components. We've resolved the issues with translations in
fieldsets, repeating groups and columns *and* translations are now directly tied to
the component/field they apply too, making everything much more intuitive.

Additionally, in the translations table we are now able to provide more context to help
translators in providing the correct literals.

**💰 Payment flow rework**

Before this version, we would always register the submission in the configured backend
and then send an update when payment is fulfilled. Now, you can configure to only
perform the registration after payment is completed.

On top of that, we've updated the UI to make it more obvious to the end user that payment
is required.

**🏡 BRK integration**

We've added support for the Basiregistratie Kadaster Haal Centraal API. You can now
validate that the authenticated user (DigiD) is "zaakgerechtigd" for the property at
a given address (postcode + number and suffixes).

**🧵 Embedding rework**

We have overhauled our embedding and redirect flows between backend and frontend. This
should now properly support all features when using hash based routing. Please let us
know if you run into any edge cases that don't work as expected yet!

**🧩 More NL Design System components**

We've restructured page-scaffolding to make use of NL Design System components, which
makes your themes more reusable and portable accross different applications.


Detailed changes
----------------

The 2.5.0-alpha.0 changes are included as well, see the earlier changelog entry.

**New features**

* Form designer

    * [:backend:`3712`] Replaced the form builder with our own implementation. The feature flag is
      now on by default for new instances. Existing instances need to toggle this.
    * [:backend:`2958`] Converted component translations to the new format used by the new form
      builder.
    * [:backend:`3607`] Added a new component type ``addressNL`` to integrate with the BRK.
    * [:backend:`2710`] Added "initials" to StufBG prefill options.

* Registration plugins

    * [:backend:`3601`], ZGW plugin: you can now register (part of) the submission data in the
      Objects API, and it will be related to the created Zaak.

      ⚠️ This requires a compatible version of the Objects API, see the
      `upstream issue <https://github.com/maykinmedia/objects-api/issues/355>`_.

* [:backend:`3726`] Reworked the payment flow to make it more obvious that payment is required.
* [:backend:`3707`] group synchronization/mapping can now be disabled with OIDC SSO.
* [:backend:`3201`] Updated more language to be B1-level.
* [:backend:`3702`] Simplified language in co-sign emails.
* [:backend:`180`] Added support for GovMetric analytics.
* [:backend:`3779`] Updated the menu structure following user feedback about the form building
  experience.
* [:backend:`3731`] Added support for "protocollering" headers when using the BRP Personen
  Bevragen API.

**Bugfixes**

* [:backend:`3656`] Fixed incorrect DigiD error messages being shown when using OIDC-based plugins.
* [:backend:`3705`] Fixed the ``__str__`` datetime representation of submissions to take the timezone
  into account.
* [:backend:`3692`] Fixed crash when using OIDC DigiD login while logged into the admin interface.
* [:backend:`3704`] Fixed the family members component not retrieving the partners when using
  StUF-BG as data source.
* Fixed 'none' value in CSP configugration.
* [:backend:`3744`] Fixed conditionally marking a postcode component as required/optional.
* [:backend:`3743`] Fixed a crash in the admin with bad ZGW API configuration.
* [:backend:`3778`] Ensured that the ``content`` component label is consistently *not* displayed
  anywhere.
* [:backend:`3755`] Fixed date/datetime fields clearing invalid values rather than showing a
  validation error.

**Project maintenance**

* [:backend:`3626`] Added end-to-end tests for submission resume flows.
* [:backend:`3694`] Upgraded to React 18.
* Removed some development tooling which was superceded by Storybook.
* Added documentation for a DigiD/eHerkenning LoA error and its solution.
* Refactored the utilities for dealing with JSON templates.
* Removed (EOL) 2.1.x from CI configuration.
* [:backend:`2958`] Added formio component Hypothesis search strategies.
* Upgraded to the latest ``drf-spectacular`` version.
* [:backend:`3049`] Replaced the admin array widget with another library.
* Upgraded libraries to have their latest security fixes.
* Improved documentation for the release process.
* Documented typing philosophy in contributing guidelines.
* Modernized dev-tooling configuration (isort, flake8, coverage).
* Squashed forms and config app migrations.

2.4.3 (2024-01-12)
==================

Periodic bugfix release

* [:backend:`3656`] Fixed incorrect DigiD error messages being shown when using OIDC-based plugins.
* [:backend:`3692`] Fixed crash when using OIDC DigiD login while logged into the admin interface.
* [:backend:`3744`] Fixed conditionally marking a postcode component as required/optional.

  .. note:: We cannot automatically fix existing logic rules. For affected forms, you
     can remove and re-add the logic rule action to modify the 'required' state.

* [:backend:`3704`] Fixed the family members component not retrieving the partners when using
  StUF-BG as data source.
* [:backend:`2710`] Added missing initials (voorletters) prefill option for StUF-BG plugin.
* Fixed failing docs build by disabling/changing some link checks.

2.5.0-alpha.0 (2023-12-15)
==========================

This is an alpha release, meaning it is not finished yet or suitable for production use.

Upgrade procedure
-----------------

⚠️ Ensure you upgrade to Open Forms 2.4.0 before upgrading to the 2.5 release series.

⚠️ Please review the instructions in the documentation under **Installation** >
**Upgrade details to Open Forms 2.5.0** before and during upgrading.

Detailed changes
----------------

**New features**

* [:backend:`3178`] Replaced more custom components with NL Design System components for improved
  themeing. You can now use design tokens for:

  * ``utrecht-document``
  * ``utrecht-page``
  * ``utrecht-page-header``
  * ``utrecht-page-footer``
  * ``utrecht-page-content``

* [:backend:`3573`] Added support for sending geo (Point2D) coordinates as GeoJSON to the Objects API.
* Added CSP ``object-src`` directive to settings (preventing embedding by default).
* Upgraded the version of the new (experimental) form builder.
* [:backend:`3559`] Added support for Piwik PRO Tag Manager as an alternative for Piwik PRO Analytics.
* [:backend:`3403`] Added support for multiple themes. You can now configure a default theme and
  specify form-specific styles to apply.
* [:backend:`3649`] Improved support for different vendors of the Documenten API implementation.
* [:backend:`3651`] The suffix to a field label for optional fields now uses simpler language.
* [:backend:`3005`] Submission processing can now be deferred until payment is completed (when
  relevant).

**Bugfixes**

* [:backend:`3362`] We've reworked and fixed the flow to redirect from the backend back to the
  form in the frontend, fixing the issues with hash-based routing in the process.
  Resuming forms after pausing, cosign flows... should now all work properly when you
  use hash-based routing.
* [:backend:`3548`] Fixed not being able to remove the MS Graph service/registration configuration.
* [:backend:`3604`] Fixed a regression in the Objects API and ZGW API's registration backends. The
  required ``Content-Crs`` request header was no longer sent in outgoing requests after
  the API client refactoring.
* [:backend:`3625`] Fixed crashes during StUF response parsing when certain ``nil`` values are
  present.
* Updated the CSP ``frame-ancestors`` directive to match the ``X-Frame-Options``
  configuration.
* [:backend:`3605`] Fixed unintended number localization in StUF/SOAP messages.
* [:backend:`3613`] Fixed submission resume flow not sending the user through the authentication
  flow again when they authenticated for forms that have optional authentication. This
  unfortunately resulted in hashed BSNs being sent to registration backends, which we
  can not recover/translate back to the plain-text values.
* [:backend:`3641`] Fixed the DigiD/eHerkenning authentication flows aborting when the user
  changes connection/IP address.
* [:backend:`3647`] Fixed a backend (logic check) crash when non-parsable time, date or datetime
  values are passed. The values are now ignored as if nothing was submitted.

**Project maintenance**

* Deleted dead/unused CSS.
* Upgraded dependencies having new patch/security releases.
* [:backend:`3620`] Upgraded storybook to v7.
* Updated the Docker image workflow, OS packages are now upgraded during the build and
  image vulnerability scanning added to the CI pipeline.
* Fixed generic type hinting of registry.
* [:backend:`3558`] Refactored the CSP setting generation from analytics configuration mechanism
  to be more resilient.
* Ensured that we send tracebacks to Sentry on DigiD errors.
* Refactored card component usage to use the component from the SDK.
* Upgraded WeasyPrint for PDF generation.
* [:backend:`3049`] Replaced deprecated calls to ``ugettext*``.
* Fixed a deprecation warning when using new-style middlewares.
* [:backend:`3005`] Simplified/refactored the task orchestration for submission processing.
* Require OF to be minimum of 2.4 before upgrading to 2.5.
* Removed original source migrations that were squashed in Open Forms 2.4.
* Replaced some (vendored) code with their equivalent library versions.
* Upgraded the NodeJS version from v16 to v20.

2.4.2 (2023-12-08)
==================

Periodic bugfix release

* [:backend:`3625`] Fixed crashes during StUF response parsing when certain ``nil`` values are
  present.
* Updated CSP ``frame-ancestors`` directive to be consistent with the ``X-Frame-Options``
  configuration.
* [:backend:`3605`] Fixed unintended number localization in StUF/SOAP messages.
* [:backend:`3613`] Fixed submission resume flow not sending the user through the authentication
  flow again when they authenticated for forms that have optional authentication. This
  unfortunately resulted in hashed BSNs being sent to registration backends, which we
  can not recover/translate back to the plain-text values.
* [:backend:`3647`] Fixed a backend (logic check) crash when non-parsable time, date or datetime
  values are passed. The values are now ignored as if nothing was submitted.

2.4.1 (2023-11-14)
==================

Hotfix release

* [:backend:`3604`] Fixed a regression in the Objects API and ZGW API's registration backends. The
  required ``Content-Crs`` request header was no longer sent in outgoing requests after
  the API client refactoring.

2.4.0 "Miffy" (2023-11-09)
==========================

Open Forms 2.4.0 is a feature release.

.. epigraph::

   **Miffy** (or "Nijntje" in Dutch) is a fictional rabbit appearing in a series of
   picture books authored by Dick Bruna. Both are famous Utrecht citizens. You can find
   Miffy in a number of places, such as the "Nijntje Pleintje" (Miffy Square) and a set
   of pedestrian traffic lights in the shape of the rabbit in the city center.

Upgrade procedure
-----------------

⚠️ Ensure you upgrade to Open Forms 2.3.0 before upgrading to the 2.4 release series.

To keep the codebase maintainable and follow best pratices, we've done some considerable
cleanups in the code that may require some special attention. We've collected the
details for this release in a separate documentation page.

⚠️ Please review the instructions in the documentation under **Installation** >
**Upgrade details to Open Forms 2.4.0** before and during upgrading.

Major features
--------------

***️ (Experimental) Suwinet plugin**

We now support retrieving data for a logged in user (with BSN) through Suwinet. This
feature is in experimental/preview mode, so we rely on your feedback on how to further
develop and improve this.

**📅 Appointments**

Our Qmatic appointments plugin now also supports multiple customer/multiple products
flows, matching the JCC feature set.

**🧩 More NL Design System components**

We continue bridging the gap between our custom UI-components and available NL DS
components. Our buttons and links now no longer require OF-specific tokens and we've
removed a whole bunch of styling code that got in the way when building your own theme.

More will come in the future!

Detailed changes
----------------

The 2.4.0-alpha.0 changes are included as well, see the earlier changelog entry.

**New features**

* Form designer

    * [:backend:`586`] Added support for Suwinet as a prefill plugin.
    * [:backend:`3188`] Added better error feedback when adding form steps to a form with
      duplicate keys.
    * [:backend:`3351`] The family members component can now be used to retrieve partner
      information instead of only the children (you can select children, partners or
      both).
    * [:backend:`2953`] Added support for durations between dates in JSON-logic.
    * [:backend:`2952`] Form steps can now initially be non-applicable and dynamically be made
      applicable.

* [:backend:`3499`] Accepting/declining cookies in the notice now no longer refreshes the page.
* [:backend:`3477`] Added CSP ``form-action`` directives, generated via the DigiD/eHerkenning
  and Ogone configuration.
* [:backend:`3524`] The behaviour when retrieving family members who don't have a BSN is now
  consistent and well-defined.
* [:backend:`3566`] Replaced custom buttons with utrecht-button components.

**Bugfixes**

* [:backend:`3527`] Duplicated form steps in a form are now blocked at the database level.
* [:backend:`3448`] Fixed emails not being sent with a subject line > 70 characters.
* [:backend:`3448`] Fixed a performance issue when upgrading the underlying email sending library
  if you have many (queued) emails.
* [:backend:`2629`] Fixed array variable inputs in the form designer.
* [:backend:`3491`] Fixed slowdown in the form designer when created a new or loading an existing
  form when many reusable form definitions exist.
* [:backend:`3557`] Fixed a bug that would not display the available document types when
  configuring the file upload component.
* [:backend:`3553`] Fixed a crash when validating a ZWG registration backend when no default
  ZGW API group is set.
* [:backend:`3537`] Fixed validator plugin list endpoint to properly converting camelCase params
  into snake_case.
* [:backend:`3467`] Fixed crashes when importing/copying forms with ``null`` in the prefill
  configuration.
* [:backend:`3580`] Fixed incorrect attributes being sent in ZWG registration backend when
  creating the rol/betrokkene.

**Project maintenance**

* Upgraded various dependencies with the most recent (security) releases.
* [:backend:`2958`] Started the rework for form field-level translations, the backend can now
  handle present and future formats.
* [:backend:`3489`] All API client usage is updated to a new library, which should lead to a
  better developer experience and make it easier to get better performance when making
  (multiple) API calls.
* Bumped pip-tools for latest pip compatibility.
* [:backend:`3531`] Added a custom migration operation class for formio component transformations.
* [:backend:`3531`] The time component now stores ``minTime``/``maxTime`` in the ``validate``
  namespace.
* Contributed a number of library extensions back to the library itself.
* Squashed the variables app migrations.
* [:backend:`2958`] Upgraded (experimental) new form builder to 0.8.0, which uses the new
  translations format.
* Fixed test suite which didn't take DST into account.
* [:backend:`3449`] Documented the (new) co-sign flow.

2.4.0-alpha.0 (2023-10-02)
==========================

Upgrade procedure
-----------------

.. warning::

    Ensure you upgrade to Open Forms 2.3.0 before upgrading to the 2.4 release series.


Detailed changes
----------------

**New features**

* [:backend:`3185`] Added Haal Centraal: HR prefill plugin to official extensions build.
* [:backend:`3051`] You can now schedule activation/deactivation of forms.
* [:backend:`1884`] Added more fine-grained custom errors for time field components.
* More fields irrelevant to appointment forms are now hidden in the form designer.
* [:backend:`3456`] Implemented multi-product and multi-customer appointments for Qmatic.
* [:backend:`3413`] Improved UX by including direct hyperlinks to the form in co-sign emails (
  admins can disable this behaviour).
* [:backend:`3328`] Qmatic appointments plugin now support mTLS.
* [:backend:`3481`] JSON-data sent to the Objects API can now optionally be HTML-escaped for when
  downstream systems fail to do so.
* [:backend:`2688`] Service-fetch response data is now cached & timeouts are configurable on the
  configuration.
* [:backend:`3443`] You can now provide custom validation error messages for date fields
* [:backend:`3402`] Added tracing information to outgoing emails so we can report on failures.
* [:backend:`3402`] Added email digest to report (potential) observed problems, like email
  delivery failures.

**Bugfixes**

* [:backend:`3139`] Fixed form designers/admins not being able to start forms in maintenance mode.
* Fixed the version of openapi-generator.
* Bumped to latest Django patch release.
* [:backend:`3447`] Fixed flash of unstyled form visible during DigiD/eHerkenning login flow.
* [:backend:`3445`] Fixed not being able to enter more decimals for latitude/longitude in the map
  component configuration.
* [:backend:`3423`] Fixed import crash with forms using service fetch.
* [:backend:`3420`] Fixed styling of cookie overview page.
* [:backend:`3378`] Fixed copying forms with logic that triggers from a particular step crashing
  the logic tab.
* [:backend:`3470`] Fixed form names with slashes breaking submission generation.
* [:backend:`3437`] Improved robustness of outgoing request logging solution.
* Included latest SDK bugfix release.
* [:backend:`3393`] Fixed duplicated form field label in eHerkenning configuration.
* [:backend:`3375`] Fixed translation warnings being shown for optional empty fields.
* [:backend:`3187`] Fixed UI displaying re-usable form definitions that are already in the form.
* [:backend:`3422`] Fixed logic tab crashes when variables/fields are deleted and added a generic
  error boundary with troubleshooting information.
* [:backend:`3308`] Fixed new installations having all-English default messages for translatable
  default content.
* [:backend:`3492`] Fixed help text referring to old context variable.
* [:backend:`3437`] Made request logging solution more robust to prevent weird crashes.
* [:backend:`3279`] Added robustness to admin pages making requests to external hosts.

**Project maintenance**

* [:backend:`3190`] Added end-to-end tests for DigiD and eHerkenning authentication flows with a
  real broker.
* Mentioned extension requirements file in docs.
* [:backend:`3416`] Refactored rendering of appointment data  in confirmation PDF.
* [:backend:`3389`] Stopped building test images, instead use symlinks or git submodules in your
  (CI) pipeline.
* Updated appointments documentation.
* Moved service factory to more general purpose location.
* [:backend:`3421`] Updated local infrastructure for form exports and clarified language to manage
  import expectations.
* Updated version of internal experimental new formio-builder.
* Prevent upgrades from < 2.3.0 to 2.4.
* Squashed *a lot* of migrations.
* Removed dead/obsolete "default BSN/KVK" configuration - no code used this anymore since
  a while.
* [:backend:`3328`] Initial rework of API clients to generically support mTLS and other
  connection parameters.
* Fixed test cleanup for self-signed certs support, causing flaky tests.
* Moved around a bunch of testing utilities to more appropriate directories.
* [:backend:`3489`] Refactored all API-client usage into common interface.
* Fixed tests failing with dev-settings.
* Bumped dependencies with security releases.

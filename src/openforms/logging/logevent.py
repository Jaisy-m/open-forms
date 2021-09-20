import logging
from typing import TYPE_CHECKING

from django.db.models import Model

if TYPE_CHECKING:
    from openforms.submissions.models import Submission, SubmissionStep

logger = logging.getLogger(__name__)


def _create_log(
    object: Model,
    event: str,
    extra_data: dict = None,
    plugin=None,
    error: Exception = None,
    tag_avg: bool = False,
):
    if extra_data is None:
        extra_data = dict()
    extra_data["log_event"] = event

    if plugin:
        extra_data["plugin"] = str(plugin.verbose_name)
        extra_data["plugin_id"] = plugin.identifier

    if error:
        extra_data["error"] = str(error)

    # import locally or we'll get "AppRegistryNotReady: Apps aren't loaded yet."
    from openforms.logging.models import TimelineLogProxy

    TimelineLogProxy.objects.create(
        content_object=object,
        template=f"logging/events/{event}.txt",
        extra_data=extra_data,
    )
    # logger.debug('Logged event in %s %s %s', event, object._meta.object_name, object.pk)


def submission_start(submission: "Submission"):
    _create_log(submission, "submission_start")


def submission_step_fill(step: "SubmissionStep"):
    _create_log(
        step.submission,
        "submission_step_fill",
        extra_data={
            "step": str(step.form_step.form_definition.name),
            "step_id": step.id,
        },
    )


def form_submit_success(submission: "Submission"):
    _create_log(submission, "form_submit_success")


def pdf_generate_start(submission: "Submission"):
    _create_log(submission, "pdf_generate_start")


def pdf_generate_success(submission: "Submission", submission_report):
    _create_log(
        submission,
        "pdf_generate_success",
        extra_data={
            "report_id": submission_report.id,
        },
    )


def pdf_generate_failure(submission: "Submission", submission_report, error: Exception):
    _create_log(
        submission,
        "pdf_generate_failure",
        error=error,
        extra_data={"report_id": submission_report.id},
    )


def pdf_generate_skip(submission: "Submission", submission_report):
    _create_log(
        submission, "pdf_generate_skip", extra_data={"report_id": submission_report.id}
    )


# - - -


def prefill_retrieve_success(submission: "Submission", plugin):
    _create_log(
        submission,
        "prefill_retrieve_success",
        plugin=plugin,
    )


def prefill_retrieve_failure(submission: "Submission", plugin, error: Exception):
    _create_log(
        submission,
        "prefill_retrieve_failure",
        plugin=plugin,
        error=error,
    )


# - - - - - - ------------------------


def registration_start(submission: "Submission"):
    _create_log(submission, "registration_start")


def registration_success(submission: "Submission", plugin):
    _create_log(
        submission,
        "registration_success",
        plugin=plugin,
    )


def registration_failure(submission: "Submission", error: Exception, plugin=None):
    _create_log(
        submission,
        "registration_failure",
        plugin=plugin,
        error=error,
    )


def registration_skip(submission: "Submission"):
    _create_log(
        submission,
        "registration_skip",
    )


# - - -


def confirmation_email_start(submission: "Submission"):
    _create_log(submission, "confirmation_email_start")


def confirmation_email_success(submission: "Submission"):
    _create_log(submission, "confirmation_email_success")


def confirmation_email_failure(submission: "Submission", error: Exception):
    _create_log(
        submission,
        "confirmation_email_failure",
        error=error,
    )


def confirmation_email_skip(submission: "Submission"):
    _create_log(submission, "confirmation_email_skip")

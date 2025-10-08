from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_email_notification(subject: str, template: str, context: dict, to_email: str):
    if not to_email:
        return
    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        html_message=html_message,
    )

def notify_task_assigned(task):
    user = task.assigned_to
    if user and user.email:
        context = {"task": task}
        send_email_notification(
            subject=f"You have been assigned a task {task.title}",
            template="emails/task_assigned.html",
            context=context,
            to_email=user.email,
        )

def notify_report_verified(report):
    user = report.author
    if user and user.email:
        context = {"report": report}
        send_email_notification(
            subject=f"Your report has been approved {report.task.title}",
            template="emails/report_verified.html",
            context=context,
            to_email=user.email,
        )

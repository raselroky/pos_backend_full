from django.core.mail import EmailMessage, get_connection,EmailMultiAlternatives
from setting.models import GeneralSetting
from django.template.loader import render_to_string

def sending_email(subject, to_emails, body=None, html_template=None, context=None, attachments=None):

    email_config = GeneralSetting.objects.filter(email_active=True).first()
    if not email_config:
        raise Exception("Email settings not configured.")

    connection = get_connection(
        backend=email_config.email_backend,
        host=email_config.email_host,
        port=email_config.email_port,
        username=email_config.email_host_user,
        password=email_config.email_host_password,
        use_tls=email_config.email_use_tls,
        fail_silently=False,
    )

    from_email = email_config.email_host_user

    if html_template:
        html_content = render_to_string(html_template, context or {})
        text_content = "This is an HTML email. Please use an email client that supports HTML."
    else:
        html_content = None
        text_content = body or ""
    # email = EmailMessage(
    #     subject=subject,
    #     body=body,
    #     from_email=email_config.email_host_user,
    #     to=to_emails,
    #     connection=connection
    # )

    email = EmailMultiAlternatives(subject, text_content, from_email, to_emails, connection=connection)
    if html_content:
        email.attach_alternative(html_content, "text/html")

    if attachments:
        for file in attachments:
            email.attach(file.name, file.read(), file.content_type)

    email.send()
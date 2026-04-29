# Python Standard Library

# Third-party Libraries
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string


# Local Modules
from users.models import UserVerificationCode, User


# Create your views here.
def send_email_user_verification_code(
        user_id: User, subject: str, template_name: str):

    try:
        user = User.objects.get(id=user_id)
        user_verification_code, _ = UserVerificationCode.\
            objects.get_or_create(
                user=user,
                created_by_user_id=user_id
            )
        user_verification_code.generate_code_and_set_valid_until()

        context = {
            'user': user,
            'code': user_verification_code.code,
        }

        body = render_to_string(
            template_name,
            context
        )

        email_msg = EmailMessage(
            subject=subject, body=body, to=[user.email]
        )
        email_msg.content_subtype = 'html'
        email_msg.mixed_subtype = 'related'
        email_msg.encoding = "utf-8"
        email_msg.send()
        return "Email sent successfully"

    except Exception as e:
        return str(e)


def hello_world(request):
    return HttpResponse(
        "This is PonteGlam Backend"
    )

from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import authenticate, tokens
from django.utils.encoding import smart_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.urls import reverse



class Util:

    @staticmethod
    def send(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']])
        email.send()
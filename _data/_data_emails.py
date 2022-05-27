# -*- coding: utf-8 -*-
import smtplib

from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django_thread import Thread


class email(models.Model):
    email_id = models.BigAutoField(primary_key=True, verbose_name="Email ID")
    email_sender = models.CharField(max_length=250, verbose_name="Email Sender", default=settings.EMAIL_HOST_USER)
    email_receiver = models.CharField(max_length=250, verbose_name="Email Receiver", null=True, blank=True)
    email_title = models.CharField(max_length=512, verbose_name="Email Title", null=True, blank=True)
    email_message = models.CharField(max_length=4096, verbose_name="Email Message", null=False, blank=False)
    sending_time = models.DateTimeField(auto_now=True, verbose_name="Sending time")
    sending_state = models.CharField(max_length=64, verbose_name="Email Status", default='Created')

    def __str__(self):
        return f'{self.email_sender} to - {self.email_receiver}- at {self.sending_time}'

    def send(self):
        thread = ExampleThread()
        thread.setEmail(self)
        thread.start()

    class Meta:
        ordering = ['email_receiver', 'sending_time']
        verbose_name_plural = "Emails"
        verbose_name = "Email"
        indexes = [
            models.Index(fields=['email_sender', ]),
            models.Index(fields=['email_receiver', ]),
            models.Index(fields=['sending_state', ])
        ]


class ExampleThread(Thread):
    def __int__(self):
        self.email_obj = None

    def setEmail(self, obj):
        self.email_obj = obj

    def run(self):
        from datetime import datetime
        if self.email_obj.email_receiver != '':
            try:
                start_time = datetime.now()
                res = send_mail(subject=self.email_obj.email_title, message=self.email_obj.email_message,
                                from_email=self.email_obj.email_sender,
                                recipient_list=[self.email_obj.email_receiver, ], fail_silently=False)
                time_elapsed = datetime.now() - start_time
                self.email_obj.sending_state = f'{res} emails sent in {time_elapsed}'
            except smtplib.SMTPException:
                self.email_obj.sending_state = f'Email not sent due to a SMTP error.'
        else:
            self.email_obj.sending_state = f'The receiver has no email address !'
        self.email_obj.save()

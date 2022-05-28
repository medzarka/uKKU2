from django.contrib import admin
from ._data_emails import email


class emailtAdmin(admin.ModelAdmin):
    list_display = ('email_id', 'email_sender', 'email_receiver', 'email_title', 'sending_time', 'sending_state','email_is_sent')
    search_fields = ('email_sender', 'email_receiver', 'email_title', 'sending_time', 'email_message')


admin.site.register(email, emailtAdmin)

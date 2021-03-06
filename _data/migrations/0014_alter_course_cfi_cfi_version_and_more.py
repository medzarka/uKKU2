# Generated by Django 4.0.5 on 2022-06-22 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('_data', '0013_email_email_is_sent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course_cfi',
            name='cfi_version',
            field=models.IntegerField(default=1, verbose_name='Version'),
        ),
        migrations.AlterField(
            model_name='email',
            name='email_sender',
            field=models.CharField(default='quality@bluewaves.online', max_length=250, verbose_name='Email Sender'),
        ),
        migrations.AlterField(
            model_name='gradesfile',
            name='version',
            field=models.IntegerField(default=1, verbose_name='Version'),
        ),
    ]

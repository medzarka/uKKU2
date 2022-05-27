from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Competence(models.Model):
    competence_id = models.BigAutoField(primary_key=True, editable=False, verbose_name='Competence Id')
    competence_name = models.CharField(max_length=128, blank=False, verbose_name='Competence Name')

    def __str__(self):
        return self.competence_name

    class Meta:
        ordering = ['competence_name', ]
        verbose_name_plural = "Competences"
        verbose_name = "Competence"
        indexes = [
            models.Index(fields=['competence_name', ]),
        ]


class myUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ar_name = models.TextField(max_length=1024, blank=False, null=False, verbose_name='Arabic Name')
    ar_surname = models.TextField(max_length=1024, blank=False, null=False, verbose_name='Arabic Surname')
    employee_code = models.IntegerField(blank=False, null=False, verbose_name='Employee Code')
    bio = models.TextField(max_length=1024, blank=True, null=True, verbose_name='Biography')
    phone1 = models.CharField(max_length=50, blank=True, null=True, verbose_name='Internal Phone')
    phone2 = models.CharField(max_length=50, blank=True, null=True, verbose_name='Personal Phone')
    phone3 = models.CharField(max_length=50, blank=True, null=True, verbose_name='Personal Phone (2)')
    office = models.CharField(max_length=30, blank=True, null=True, verbose_name='Office Location')
    competence = models.ManyToManyField(Competence, on_delete=models.PROTECT, verbose_name='Main Competences',
                                        related_name='user_competences')

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    class Meta:
        ordering = ['employee_code', ]
        verbose_name_plural = "Users"
        verbose_name = "User"
        indexes = [
            models.Index(fields=['ar_name', ]),
            models.Index(fields=['ar_surname', ]),
            models.Index(fields=['employee_code', ]),
            models.Index(fields=['phone1', ]),
            models.Index(fields=['office', ]),
        ]


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        myUser.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



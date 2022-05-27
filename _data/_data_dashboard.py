from django.db import models

from _data._data_periods import Semester


class Link(models.Model):
    link_id = models.BigAutoField(primary_key=True, verbose_name='Link ID')
    link_description = models.CharField(max_length=2048, unique=True, verbose_name='Link Description', blank=False,
                                        null=False)
    link_url = models.CharField(max_length=2048, unique=True, verbose_name='Link URL', blank=False,
                                        null=False)
    link_time = models.DateTimeField(auto_now=True, verbose_name="Link Submission time")
    link_semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['link_time']
        verbose_name_plural = 'Links'
        verbose_name = 'Link'
        indexes = [
            models.Index(fields=['link_time', ]),
            models.Index(fields=['link_semester', ]),
        ]

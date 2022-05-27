from django.db import models

from django.contrib.auth.models import User, Group

from enum import unique, Enum
import uuid

from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User

#########################################################################################################
from _control._Measurement.Measurement_FS import Measurement_FS
from _data._data_academic_program import Course
from _data._data_periods import Semester


@unique
class Document_FS(Enum):
    TMP = 'Documents/tmp/'
    DOCS = 'Documents/docs/'


def get_measurement_export_file_name(instance, filename):
    _tmp = f'{Document_FS.DOCS.value}'
    _tmp += f'{instance.semester.semester_academic_year.academic_year_name}/'
    _tmp += f'{instance.semester.semester_name}/export/'
    _tmp += f'Measurement_export_{instance.semester.semester_academic_year.academic_year_name}'
    _tmp += f'_{instance.semester.semester_name}_{instance.submission_time}.zip'
    return _tmp


class ManagementComponent(models.Model):
    component_id = models.BigAutoField(primary_key=True, editable=False, verbose_name='Component ID')
    component_name = models.CharField(max_length=512, verbose_name='Component Name', null=False, blank=False)
    public_groups = models.ForeignKey(Groups)
    head_groups =
    members_groups =


    def __str__(self):
        return self.component_name

    class Meta:
        ordering = ['component_name', ]
        verbose_name_plural = "Management Components"
        verbose_name = "Management Component"
        indexes = [
            models.Index(fields=['component_id', ]),
            models.Index(fields=['component_name', ])
        ]

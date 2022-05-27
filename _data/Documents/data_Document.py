from django.db import models

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


class Document(models.Model):
    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)

    department_name = models.CharField(max_length=250, verbose_name="Department Name", null=True, blank=True)

    def __str__(self):
        return self.department_name

    class Meta:
        ordering = ['department_name', ]
        verbose_name_plural = "Departments"
        verbose_name = "Department"
        indexes = [
            models.Index(fields=['department_id', ]),
            models.Index(fields=['department_name', ])
        ]

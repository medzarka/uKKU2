from django.db import models
from django.contrib.auth.models import User
from _data._data_periods import Semester
from ._data_academic_program import Course
from ._data_measurement import Department


class Campus(models.Model):
    campus_id = models.BigAutoField(primary_key=True, verbose_name='Campus ID')
    campus_name = models.CharField(max_length=512, verbose_name='Campus Name')
    campus_name_ar = models.CharField(max_length=512, verbose_name='Campus Arabic Name')

    def __str__(self):
        return f'{self.campus_name} -- {self.campus_name_ar}'

    class Meta:
        ordering = ['campus_id', 'campus_name']
        verbose_name_plural = "Campus"
        verbose_name = "Campus"
        indexes = [
            models.Index(fields=['campus_id', ]),
            models.Index(fields=['campus_name', ]),
            models.Index(fields=['campus_name_ar', ]),
        ]


class Meeting(models.Model):
    meeting_id = models.BigAutoField(primary_key=True, verbose_name='Meeting ID')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name='meetings')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=False, blank=False, related_name='meetings')
    section = models.IntegerField(verbose_name='Section', null=False, blank=False)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=False, blank=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=False, blank=False)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['semester', 'campus', 'department', 'teacher', 'course', 'section']
        verbose_name_plural = "Meetings"
        verbose_name = "Meeting"
        indexes = [
            models.Index(fields=['semester', ]),
            models.Index(fields=['campus', ]),
            models.Index(fields=['department', ]),
            models.Index(fields=['teacher', ]),
            models.Index(fields=['course', ]),
            models.Index(fields=['section', ]),
        ]

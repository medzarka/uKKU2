from django.db import models


#########################################################################################################
class Specialization(models.Model):
    specialization_id = models.BigAutoField(primary_key=True, verbose_name="Specialization ID")
    specialization_code = models.CharField(max_length=100, verbose_name="Specialization Code")
    specialization_name = models.CharField(max_length=500, verbose_name="Program Name")
    specialization_name_ar = models.CharField(max_length=500, verbose_name="Program Arabic Name")

    def __str__(self):
        return ' [Specialization = ' + self.specialization_name + ']'

    class Meta:
        ordering = ['specialization_code', 'specialization_name']
        verbose_name_plural = "Academic Specializations"
        verbose_name = "Academic Specialization"
        indexes = [
            models.Index(fields=['specialization_code', ]),
            models.Index(fields=['specialization_name', ]),
            models.Index(fields=['specialization_name_ar', ]),
        ]


#########################################################################################################
class Program(models.Model):
    program_id = models.BigAutoField(primary_key=True, verbose_name="Program ID")
    program_code = models.CharField(max_length=100, verbose_name="Program Code")
    program_name = models.CharField(max_length=500, verbose_name="Program Name")
    program_name_ar = models.CharField(max_length=500, verbose_name="Program Arabic Name")
    program_version = models.CharField(max_length=100, verbose_name="Program Version")
    specialization = models.ForeignKey(Specialization, verbose_name='Specialization',
                                       null=True, on_delete=models.CASCADE,
                                       blank=True)

    def __str__(self):
        return str(self.specialization) + '[Program = ' + self.program_name + ' version ' + self.program_version + ']'

    class Meta:
        ordering = ['specialization', 'program_code', 'program_name', 'program_version']
        verbose_name_plural = "Academic Programs"
        verbose_name = "Academic Program"
        indexes = [
            models.Index(fields=['program_code', ]),
            models.Index(fields=['program_name', ]),
            models.Index(fields=['program_name_ar', ]),
            models.Index(fields=['program_version', ]),
            models.Index(fields=['specialization', ]),
        ]


#########################################################################################################

class Course(models.Model):
    course_id = models.BigAutoField(primary_key=True, verbose_name='Course ID')
    course_code = models.CharField(max_length=100, verbose_name='Course Code')
    course_code_ar = models.CharField(max_length=100, verbose_name='Course Arabic Code')
    course_name = models.CharField(max_length=500, verbose_name='Course Name')
    course_name_ar = models.CharField(max_length=500, verbose_name='Course Arabic Name')
    course_level = models.IntegerField(default=1, verbose_name='Course Level')
    program = models.ForeignKey(Program, verbose_name='Academic Program',
                                null=True, on_delete=models.CASCADE,
                                blank=True)

    def __str__(self):
        return str(
            self.program) + ' Course : ' + self.course_code + ' --- ' + self.course_name + '--- (' + self.course_code_ar + ')'

    class Meta:
        ordering = ['program', 'course_code', ]
        verbose_name_plural = "Courses"
        verbose_name = "Course"
        indexes = [
            models.Index(fields=['course_code', ]),
            models.Index(fields=['course_name', ]),
            models.Index(fields=['course_name_ar', ]),
            models.Index(fields=['program', ]),
            models.Index(fields=['course_level', ]),
        ]

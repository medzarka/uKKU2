from django.db import models

from datetime import date


####################################################################################################################
#######################"  Periods: Academic Years and Semesters

class AcademicYear(models.Model):
    academic_year_id = models.BigAutoField(primary_key=True, verbose_name='ID')
    academic_year_name = models.CharField(max_length=100, unique=True, verbose_name='Academic Year Name', blank=False,
                                          null=False)
    academic_year_date_start = models.DateField(verbose_name='First day')
    academic_year_date_end = models.DateField(verbose_name='Last day')

    @property
    def isActualAcademicYear(self):
        present = date.today()
        if self.academic_year_date_start <= present <= self.academic_year_date_end:
            return True
        else:
            return False

    def __str__(self):
        # _start = self.academic_year_date_start.strftime("%A %d. %B %Y")
        # _end = self.academic_year_date_end.strftime("%A %d. %B %Y")
        # _start = self.academic_year_date_start.strftime("%Y")
        # _end = self.academic_year_date_end.strftime("%Y")
        # return _start + '--' + _end
        return self.academic_year_name

    class Meta:
        ordering = ['academic_year_date_start']
        verbose_name_plural = 'Academic Years'
        verbose_name = 'Academic Year'
        indexes = [
            models.Index(fields=['academic_year_name', ]),
        ]


class Semester(models.Model):
    SEMESTER_I = 'SEMESTER I'
    SEMESTER_II = 'SEMESTER II'
    TRIMESTER_I = 'TRIMESTER I'
    TRIMESTER_II = 'TRIMESTER II'
    TRIMESTER_III = 'TRIMESTER III'
    SUMMER_TERM = 'SUMMER TERM'
    TERM_CHOICE = [
        (SEMESTER_I, 'SEMESTER I'),
        (SEMESTER_II, 'SEMESTER II'),
        (TRIMESTER_I , 'TRIMESTER I'),
        (TRIMESTER_II, 'TRIMESTER II'),
        (TRIMESTER_III, 'TRIMESTER III'),
        (SUMMER_TERM, 'SUMMER TERM'),
    ]

    semester_id = models.BigAutoField(primary_key=True, verbose_name='ID')
    semester_name = models.CharField(max_length=100, choices=TERM_CHOICE,
                                     default=TRIMESTER_I, verbose_name='Term Name')

    semester_academic_year = models.ForeignKey('AcademicYear', on_delete=models.CASCADE, verbose_name='Academic Year')
    semester_date_start = models.DateField(verbose_name='First Day', blank=False,
                                           null=False)
    semester_date_end = models.DateField(verbose_name='Last Day', blank=False,
                                         null=False)
    semester_isInUse = models.BooleanField(verbose_name='Is in Use', default=False)

    @property
    def isActualSemester(self):
        present = date.today()
        if self.semester_date_start <= present <= self.semester_date_end:
            return True
        else:
            return False

    @property
    def isSummerTerm(self):
        if self.semester_name == 'SUMMER TERM':
            return True
        return False

    def __str__(self):
        # _start = self.semester_date_start.strftime("%A %d. %B %Y")
        # _end = self.semester_date_end.strftime("%A %d. %B %Y")
        return str(self.semester_academic_year) + '__' + self.semester_name

    class Meta:
        ordering = ['semester_academic_year', 'semester_date_start', ]
        verbose_name_plural = "Semesters"
        verbose_name = "Semester"
        indexes = [
            models.Index(fields=['semester_name', ]),
            models.Index(fields=['semester_academic_year', ]),
        ]

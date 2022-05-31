from enum import unique, Enum

from django.core.mail import send_mail

from django.db import models
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User

#########################################################################################################
from _control._Measurement.Measurement_FS import Measurement_FS
from _data._data_academic_program import Course
from _data._data_periods import Semester
from _data._data_schedule import Meeting

_measurement_grades_fs = FileSystemStorage(location=Measurement_FS.GRADES.value)
_measurement_reports_fs = FileSystemStorage(location=Measurement_FS.REPORTS.value)
_measurement_histograms = FileSystemStorage(location=Measurement_FS.HISTOGRAM.value)


@unique
class ReportState(Enum):
    CREATED = 0
    SUBMITTED = 1
    ACCEPTED = 2
    NEEDS_REVIEW = 3


@unique
class TestType(Enum):
    NONE = 'none'
    TTEST = 'ttest'
    ANNOVA = 'annova'


class Department(models.Model):
    department_id = models.BigAutoField(primary_key=True, verbose_name="Department")
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


def get_sections_grades_upload_file_name(instance, filename):
    _tmp = f'{Measurement_FS.GRADES.value}'
    _tmp += f'{instance.semester.semester_academic_year.academic_year_name}/'
    _tmp += f'{instance.semester.semester_name}/'
    _tmp += f'{instance.section_code}/grades_{instance.section_code}.xlsx'
    return _tmp


def get_sections_reports_upload_file_name(instance, filename):
    _tmp = f'{Measurement_FS.REPORTS.value}'
    _tmp += f'{instance.semester.semester_academic_year.academic_year_name}/'
    _tmp += f'{instance.semester.semester_name}/'
    _tmp += f'{instance.section_department}/sections/'
    _tmp += f'{instance.section_code}/sec_{instance.section_code}.docx'
    return _tmp


def get_courses_reports_upload_file_name(instance, filename):
    _tmp = f'{Measurement_FS.REPORTS.value}'
    _tmp += f'{instance.semester.semester_academic_year.academic_year_name}/'
    _tmp += f'{instance.semester.semester_name}/'
    _tmp += f'{instance.course_department}/courses/'
    _tmp += f'{instance.course_name}/{instance.course_name}.docx'
    return _tmp


def get_department_reports_upload_file_name(instance, filename):
    _tmp = f'{Measurement_FS.REPORTS.value}'
    _tmp += f'{instance.semester.semester_academic_year.academic_year_name}/'
    _tmp += f'{instance.semester.semester_name}/'
    _tmp += f'{instance.department}/department_report/'
    _tmp += f'{instance.department}.docx'
    return _tmp


def get_measurement_export_file_name(instance, filename):
    _tmp = f'{Measurement_FS.REPORTS.value}'
    _tmp += f'{instance.semester.semester_academic_year.academic_year_name}/'
    _tmp += f'{instance.semester.semester_name}/export/'
    _tmp += f'Measurement_export_{instance.semester.semester_academic_year.academic_year_name}'
    _tmp += f'_{instance.semester.semester_name}_{instance.submission_time}.zip'
    return _tmp


class GradesFile(models.Model):
    grades_file_id = models.BigAutoField(primary_key=True, verbose_name="Grades File ID")
    submission_time = models.DateTimeField(auto_now=True, verbose_name="Submission time")
    course_name = models.CharField(max_length=250, verbose_name="Course Name", null=True, blank=True)
    course_code = models.CharField(max_length=250, verbose_name="Course Code", null=True, blank=True)
    campus_name = models.CharField(max_length=250, verbose_name="Campus Name", null=True, blank=True)
    section_code = models.IntegerField(verbose_name="Section Code", null=True, blank=True)

    stat_mean = models.CharField(max_length=250, verbose_name="Grades Mean", null=True, blank=True)
    stat_std = models.CharField(max_length=250, verbose_name="Grades STD", null=True, blank=True)
    stat_skewness = models.CharField(max_length=250, verbose_name="Grades Skewness", null=True, blank=True)
    stat_correlation_sig = models.CharField(max_length=250, verbose_name="Grades Correlation (Sig)", null=True,
                                            blank=True)
    stat_correlation_value = models.CharField(max_length=250, verbose_name="Grades Correlation", null=True, blank=True)
    stat_min = models.CharField(max_length=250, verbose_name="Grades Min", null=True, blank=True)
    stat_max = models.CharField(max_length=250, verbose_name="Grades Max", null=True, blank=True)
    stat_histogram = models.FileField(upload_to=Measurement_FS.HISTOGRAM.value, null=True, blank=True)
    stat_analysis = models.TextField(verbose_name="Grades Analysis", null=True, blank=True)

    grades_file = models.FileField(upload_to=get_sections_grades_upload_file_name, max_length=1024)
    report_file = models.FileField(upload_to=get_sections_reports_upload_file_name, null=True, blank=True,
                                   max_length=1024)
    grades_data = models.TextField(verbose_name="Grades Data", null=True, blank=True)

    teacher_analysis = models.TextField(verbose_name="Grades Analysis", null=True, blank=True)

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='section_reports')

    version = models.IntegerField(verbose_name="Version", default=0)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    report_state = models.IntegerField(verbose_name="State", default=ReportState.CREATED.value)

    grades_data = models.TextField(verbose_name="Grades Data", null=True, blank=True)
    remarks = models.TextField(verbose_name="Remarks", default='', null=True, blank=True)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='section_reviews')
    section_department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    section_courseObj = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    section_meetingObj = models.ForeignKey(Meeting, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return ' Grades File for section ' + str(self.section_code) + ' (' + str(self.submission_time) + ')'

    def getCourseFullName(self):
        return f'[{self.course_code}] ---  {self.course_name}'

    def getRemarks(self):
        res = []
        for line in self.remarks.split('\n'):
            try:
                row = line.split(':::::')
                _tmp = {}
                _version = row[0]
                _time = row[1]
                _remark = row[2]
                _reviewer = row[3]
                __str = f'[Version={_version},  Date={_time},   Reviewer={_reviewer}]   {_remark}'
                res.append(__str)
            except IndexError:
                pass
        return res

    def addRemark(self, remark, user):
        import time
        t = time.localtime()
        current_time = time.strftime("%m/%d/%Y   %H:%M", t)
        remark = remark.replace('\n', '')
        _separator = ':::::'
        _str = f'{self.version}{_separator}{current_time}{_separator}{remark}{_separator}{user}'
        self.remarks = self.remarks + '\n' + _str

    def getReviewstate(self):
        if self.report_state == ReportState.CREATED.value:
            return 'CREATED'
        if self.report_state == ReportState.SUBMITTED.value:
            return 'SUBMITTED'
        if self.report_state == ReportState.ACCEPTED.value:
            return 'ACCEPTED'
        if self.report_state == ReportState.NEEDS_REVIEW.value:
            return 'NEEDS REVIEW'

    def validate(self, _reviewer):
        self.report_state = ReportState.ACCEPTED.value
        self.reviewer = _reviewer

        ## mail
        mail_subject = f'Update status for the Statistical section report for section {self.section_code}'
        mail_message = f'Dear faculty member, we want to notice that the statistical report for the section {self.section_code} is accepted. Best regards'
        self.sendEmail(self.teacher.email, mail_subject, mail_message)

        self.save()

    def refuse(self, _reviewer):
        self.report_state = ReportState.NEEDS_REVIEW.value
        self.reviewer = _reviewer

        ## mail
        mail_subject = f'Update status for the Statistical section report for section {self.section_code}'
        mail_message = f'Dear faculty member, we want to notice that the statistical report for the section {self.section_code} needs revision . Best regards'
        self.sendEmail(self.teacher.email, mail_subject, mail_message)

        self.save()

    def submit(self, update=False, reviewer_email=''):

        # print('-------> ' + str(self.report_state))

        if self.report_state == ReportState.NEEDS_REVIEW.value:
            self.version = self.version + 1
            self.report_state = ReportState.CREATED.value
            self.save()

            ## mail to the reviewer
            mail_subject = f'A new statistical report to review for the section {self.section_code} is submitted'
            mail_message = f'Dear faculty member and Measurement Unit member, we want to notice that the statistical report for the section {self.section_code} is submitted and needs your review. Best regards'
            self.sendEmail(reviewer_email, mail_subject, mail_message)
            ## mail to teacher
            mail_subject = f'A new statistical report to review for the section {self.section_code} is submitted'
            mail_message = f'Dear faculty member, we want to notice that the statistical report for the section {self.section_code} is submitted and is under review. Best regards'
            self.sendEmail(self.teacher.email, mail_subject, mail_message)

            return

        if self.report_state == ReportState.CREATED.value and update == True:
            self.report_state = ReportState.SUBMITTED.value
            self.save()

            ## mail to the reviewer
            mail_subject = f'A new statistical report to review for the section {self.section_code} is submitted'
            mail_message = f'Dear faculty member and Measurement Uinit member, we want to notice that the statistical report for the section {self.section_code} is submitted and needs your review. Best regards'
            self.sendEmail(reviewer_email, mail_subject, mail_message)

            ## mail to the teacher
            mail_subject = f'A new statistical report to review for the section {self.section_code} is submitted'
            mail_message = f'Dear faculty member, we want to notice that the statistical report for the section {self.section_code} is submitted and is under review. Best regards'
            self.sendEmail(self.teacher.email, mail_subject, mail_message)

            return

    def end(self):

        ## mail
        mail_subject = f'Update status for the Statistical section report for section {self.section_code}'
        mail_message = f'Dear faculty member, we want to notice that the statistical report for the section {self.section_code} is deleted. Best Regards'
        self.sendEmail(self.teacher.email, mail_subject, mail_message)
        self.delete()

    def sendEmail(self, receiver_email, title, message):
        from _data._data_emails import email
        __email = email(email_receiver=receiver_email, email_title=title, email_message=message)
        __email.save()
        __email.send()

    def is_validated(self):
        if self.report_state == ReportState.ACCEPTED.value:
            return True
        return False

    def is_submitted(self):
        if self.report_state == ReportState.SUBMITTED.value:
            return True
        return False

    def is_refused(self):
        if self.report_state == ReportState.NEEDS_REVIEW.value:
            return True
        return False

    class Meta:
        ordering = ['section_code', 'submission_time']
        verbose_name_plural = "Grades Files"
        verbose_name = "Grades File"
        indexes = [
            models.Index(fields=['submission_time', ]),
            models.Index(fields=['section_code', ]),
            models.Index(fields=['course_name', ]),
            models.Index(fields=['campus_name', ]),
            models.Index(fields=['section_department', ]),
            models.Index(fields=['section_courseObj', ]),

        ]


class CourseFile(models.Model):
    course_file_id = models.BigAutoField(primary_key=True, verbose_name="Course File ID")
    submission_time = models.DateTimeField(auto_now=True, verbose_name="Submission time")
    course_name = models.CharField(max_length=250, verbose_name="Course Name", null=True, blank=True)
    course_code = models.CharField(max_length=250, verbose_name="Course Code", null=True, blank=True)
    campus_name = models.CharField(max_length=250, verbose_name="Campus Name", null=True, blank=True)
    section_codes = models.CharField(max_length=250, verbose_name="Sections", null=True, blank=True)

    stat_mean = models.CharField(max_length=250, verbose_name="Mean", null=True, blank=True)
    stat_std = models.CharField(max_length=250, verbose_name="STD", null=True, blank=True)
    stat_skewness = models.CharField(max_length=250, verbose_name="Skewness", null=True, blank=True)
    stat_correlation_sig = models.CharField(max_length=250, verbose_name="Correlation (Sig)", null=True,
                                            blank=True)
    stat_correlation_value = models.CharField(max_length=250, verbose_name="Correlation", null=True, blank=True)
    stat_min = models.CharField(max_length=250, verbose_name="Min", null=True, blank=True)
    stat_max = models.CharField(max_length=250, verbose_name="Max", null=True, blank=True)
    stat_histogram = models.FileField(upload_to=Measurement_FS.HISTOGRAM.value, null=True, blank=True)
    stat_analysis = models.TextField(verbose_name="Analysis", null=True, blank=True)
    stat_ttest_annova_value = models.CharField(max_length=250, verbose_name="TTEST/ANNOVA value", null=True, blank=True)
    stat_ttest_annova_sig = models.CharField(max_length=250, verbose_name="TTEST/ANNOVA Sig.", null=True, blank=True)
    stat_ttest_annova = models.CharField(max_length=250, verbose_name="Test Type", default=TestType.NONE.value,
                                         null=True, blank=True)

    report_file = models.FileField(upload_to=get_courses_reports_upload_file_name, null=True, blank=True,
                                   max_length=1024)

    teacher_analysis = models.TextField(verbose_name="Teacher Analysis", null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='course_reports')

    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    report_state = models.IntegerField(verbose_name="State", default=ReportState.CREATED.value)

    course_department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    remarks = models.TextField(verbose_name="Remarks", default='')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Reviewer", null=True, blank=True,
                                 related_name='course_reviews')
    version = models.IntegerField(verbose_name="Version", default=0)

    def __str__(self):
        return ' Report for the course ' + str(self.course_name) + ' (' + str(self.submission_time) + ')'

    def getCourseFullName(self):
        return f'[{self.course_code}] ---  {self.course_name}'

    def getReviewstate(self):
        if self.report_state == ReportState.CREATED.value:
            return 'CREATED'
        if self.report_state == ReportState.SUBMITTED.value:
            return 'SUBMITTED'
        if self.report_state == ReportState.ACCEPTED.value:
            return 'ACCEPTED'
        if self.report_state == ReportState.NEEDS_REVIEW.value:
            return 'NEEDS REVIEW'

    def validate(self):
        self.report_state = ReportState.ACCEPTED.value
        self.save()

    def refuse(self):
        self.report_state = ReportState.NEEDS_REVIEW.value
        self.save()

    def is_validated(self):
        if self.report_state == ReportState.ACCEPTED.value:
            return True
        return False

    def is_submitted(self):
        if self.report_state == ReportState.SUBMITTED.value:
            return True
        return False

    def is_refused(self):
        if self.report_state == ReportState.NEEDS_REVIEW.value:
            return True
        return False

    def submit(self, update=False):

        if self.report_state == ReportState.NEEDS_REVIEW.value:
            self.version = self.version + 1
            self.report_state = ReportState.CREATED.value
            self.save()
            return

        if self.report_state == ReportState.CREATED.value and update is True:
            self.report_state = ReportState.SUBMITTED.value
            self.save()
            return

    def end(self):
        self.delete()

    def getRemarks(self):
        res = []
        for line in self.remarks.split('\n'):
            try:
                row = line.split(':::::')
                _tmp = {}
                _version = row[0]
                _time = row[1]
                _remark = row[2]
                _reviewer = row[3]
                __str = f'[Version={_version},    Date={_time},      Reviewer={_reviewer}]   {_remark}'
                res.append(__str)
            except IndexError:
                pass
        return res

    def addRemark(self, remark, user):
        import time
        t = time.localtime()
        current_time = time.strftime("%m/%d/%Y   %H:%M", t)
        remark = remark.replace('\n', '')
        _separator = ':::::'
        _str = f'{self.version}{_separator}{current_time}{_separator}{remark}{_separator}{user}'
        self.remarks = self.remarks + '\n' + _str

    class Meta:
        ordering = ['course_name', 'submission_time']
        verbose_name_plural = "Course Reports"
        verbose_name = "Course Report"
        indexes = [
            models.Index(fields=['submission_time', ]),
            models.Index(fields=['course_name', ]),
            models.Index(fields=['campus_name', ]),
            models.Index(fields=['course_department', ]),
        ]


class DepartmentFile(models.Model):
    department_file_id = models.BigAutoField(primary_key=True, verbose_name="Department File ID")
    submission_time = models.DateTimeField(auto_now=True, verbose_name="Submission time")

    stat_histogram_low = models.FileField(upload_to=Measurement_FS.HISTOGRAM.value, null=True, blank=True)
    stat_histogram_high = models.FileField(upload_to=Measurement_FS.HISTOGRAM.value, null=True, blank=True)
    report_file = models.FileField(upload_to=get_department_reports_upload_file_name, null=True, blank=True,
                                   max_length=1024)

    teacher_analysis = models.TextField(verbose_name="Teacher Analysis", null=True, blank=True)

    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)

    stat_anova_value = models.CharField(max_length=250, verbose_name="ANNOVA value", null=True, blank=True)
    stat_anova_sig = models.CharField(max_length=250, verbose_name="ANNOVA Sig.", null=True, blank=True)
    stat_eta_value = models.CharField(max_length=250, verbose_name="Eta Test Value", null=True, blank=True)
    stat_eta_sig = models.CharField(max_length=250, verbose_name="Eta Test Sig.", null=True, blank=True)
    number_of_courses = models.CharField(max_length=250, verbose_name="Number of Courses", null=True, blank=True)

    means_low = models.TextField(verbose_name="means_low", null=True, blank=True)
    means_high = models.TextField(verbose_name="means_high", null=True, blank=True)

    def __str__(self):
        return ' Department Report : ' + str(self.department.department_name) + ' ('
        str(self.submission_time) + ')'

    class Meta:
        ordering = ['semester', 'department']
        verbose_name_plural = "Department Reports"
        verbose_name = "Department Report"
        indexes = [
            models.Index(fields=['submission_time', ]),
            models.Index(fields=['department', ]),
            models.Index(fields=['semester', ]),
        ]


class MeasurementReviewerAffectations(models.Model):
    affectation_id = models.BigAutoField(primary_key=True, verbose_name="Review Affectation ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False,
                             related_name='MeasurementaffectationUser')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='MeasurementaffectationReviewers')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        ordering = ['reviewer', 'user']
        verbose_name_plural = "Measurement Reviewer Affectations"
        verbose_name = "Measurement Reviewer Affectation"
        indexes = [
            models.Index(fields=['user', ]),
            models.Index(fields=['reviewer', ]),
            models.Index(fields=['semester', ]),
        ]


class MeasurementExportFile(models.Model):
    measurement_export_file_id = models.BigAutoField(primary_key=True, verbose_name="Measurement Export File ID")
    submission_time = models.DateTimeField(auto_now=True, verbose_name="Submission time")

    export_file = models.FileField(upload_to=get_measurement_export_file_name, null=True, blank=True,
                                   max_length=1024)

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    state = models.IntegerField(verbose_name="State", default=0)  # 0 --> in progress, 1 --> done, -1 --> Error
    elapsedTime = models.TextField(verbose_name="Elapsed Time", default='')

    def __str__(self):
        return ' Measurement Export File : ' + str(
            self.semester.semester_academic_year.academic_year_name) + '--' + str(
            self.semester.semester_name) + ' (' + str(self.submission_time) + ')'

    class Meta:
        ordering = ['semester', 'submission_time', 'state']
        verbose_name_plural = "Measurement Export Files"
        verbose_name = "Measurement Export File"
        indexes = [
            models.Index(fields=['submission_time', ]),
            models.Index(fields=['semester', ]),
            models.Index(fields=['teacher', ]),
            models.Index(fields=['state', ]),
        ]

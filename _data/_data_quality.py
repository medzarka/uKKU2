from enum import unique, Enum

from django.db import models
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from _control._Measurement.Measurement_FS import Quality_FS
from _data._data_periods import Semester

from ._data_measurement import GradesFile, Department
from django.core.exceptions import ValidationError

_quality_tmp_fs = FileSystemStorage(location=Quality_FS.TMP.value)
_quality_reports_fs = FileSystemStorage(location=Quality_FS.REPORTS.value)
_quality_templates_fs = FileSystemStorage(location=Quality_FS.TEMPLATES.value)


def validate_file_size_50(value):
    filesize = value.size

    if filesize > 52428800:  # 50 MB
        raise ValidationError("The maximum file size that can be uploaded is 50MB")
    else:
        return value


def validate_file_size(value):
    filesize = value.size

    if filesize > 10485760:  # 10 MB
        raise ValidationError("The maximum file size that can be uploaded is 10MB")
    else:
        return value


def validate_file_type(value):  ## we accept only PDF, DOC/DOCX, XLS/XLSX, and ZIP files
    file = value.file
    content_types = []
    content_types.append('application/pdf')  # PDF
    content_types.append('application/msword')  # DOC
    content_types.append('application/vnd.openxmlformats-officedocument.wordprocessingml.document')  # DOCX
    content_types.append('application/vnd.ms-excel')  # XLS
    content_types.append('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  # XLSX
    content_types.append('application/zip')  # ZIP

    try:
        content_type = file.content_type
        if content_type not in content_types:
            raise ValidationError(
                "Filetype not supported. The system accepts only PDF, DOC/DOCX, XLS/XLSX, and ZIP files")
        else:
            return value
    except AttributeError:
        pass


@unique
class ReportState(Enum):
    CREATED = 0
    SUBMITTED = 1
    ACCEPTED = 2
    NEEDS_REVIEW = 3


def get_upload_file_name(instance, filename):
    _tmp = f'{Quality_FS.REPORTS.value}'
    _tmp += f'{instance.gradeFile.semester.semester_academic_year.academic_year_name}/'
    _tmp += f'{instance.gradeFile.semester.semester_name}/'
    _tmp += f'{instance.gradeFile.section_department}/'
    _tmp += f'{instance.gradeFile.teacher.first_name}/'
    _tmp += f'{instance.gradeFile.course_name}/'
    _tmp += f'{instance.gradeFile.section_code}/{filename}'
    return _tmp


def get_quality_export_file_name(instance, filename):
    _tmp = f'{Quality_FS.REPORTS.value}'
    _tmp += f'{instance.semester.semester_academic_year.academic_year_name}/'
    _tmp += f'{instance.semester.semester_name}/export/'
    _tmp += f'{instance.quality_type}__Quality_export_{instance.semester.semester_academic_year.academic_year_name}'
    _tmp += f'_{instance.semester.semester_name}_{str(instance.submission_time)[:20]}.zip'
    return _tmp


def get_quality_export_logtrace_filename(instance, filename):
    _tmp = f'{Quality_FS.REPORTS.value}'
    _tmp += f'{instance.semester.semester_academic_year.academic_year_name}/'
    _tmp += f'{instance.semester.semester_name}/export/'
    _tmp += f'{filename}'
    return _tmp


class ReviewerAffectations(models.Model):
    affectation_id = models.BigAutoField(primary_key=True, verbose_name="Review Affectation ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False,
                             related_name='affectationUser')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='affectationReviewers')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        ordering = ['reviewer', 'user']
        verbose_name_plural = "Quality Reviewer Affectations"
        verbose_name = "Quality Reviewer Affectation"
        indexes = [
            models.Index(fields=['user', ]),
            models.Index(fields=['reviewer', ]),
            models.Index(fields=['semester', ]),
        ]


class Course_CFI(models.Model):
    course_cfi_id = models.BigAutoField(primary_key=True, verbose_name="Course CFI ID")
    submission_time = models.DateTimeField(auto_now=True, verbose_name="Submission time")

    # Reports part --------------------------------------------------------------------------------------
    gradeFile = models.ForeignKey(GradesFile, on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='section_CFIs')
    course_specification_file = models.FileField(upload_to=get_upload_file_name, null=True, blank=True,
                                                 verbose_name="Course Specification File",
                                                 validators=[validate_file_size, validate_file_type], max_length=1024)
    exams_samples_file = models.FileField(upload_to=get_upload_file_name, null=True,
                                          blank=True, verbose_name="Exams Samples File",
                                          validators=[validate_file_size_50, validate_file_type], max_length=1024)
    marks_file = models.FileField(upload_to=get_upload_file_name, null=True,
                                  blank=True, verbose_name="Marks File",
                                  validators=[validate_file_size, validate_file_type], max_length=1024)
    clos_measurement_file = models.FileField(upload_to=get_upload_file_name, null=True, blank=True,
                                             verbose_name="CLOs Measurement File",
                                             validators=[validate_file_size, validate_file_type], max_length=1024)
    course_report_file = models.FileField(upload_to=get_upload_file_name, null=True, blank=True,
                                          verbose_name="Course Report File",
                                          validators=[validate_file_size, validate_file_type], max_length=1024)
    kpis_measurements_file = models.FileField(upload_to=get_upload_file_name, null=True, blank=True,
                                              verbose_name="KPIs Measurement File",
                                              validators=[validate_file_size, validate_file_type], max_length=1024)
    instructor_schedule_file = models.FileField(upload_to=get_upload_file_name, null=True, blank=True,
                                                verbose_name="Instructor Schedule File",
                                                validators=[validate_file_size, validate_file_type], max_length=1024)
    course_plan_file = models.FileField(upload_to=get_upload_file_name, null=True, blank=True,
                                        verbose_name="Course Plan File",
                                        validators=[validate_file_size, validate_file_type], max_length=1024)
    curriculum_vitae_file = models.FileField(upload_to=get_upload_file_name, null=True, blank=True,
                                             verbose_name="Faculty Curriculum Vitae",
                                             validators=[validate_file_size, validate_file_type], max_length=1024)
    report_cfi = models.FileField(upload_to=get_upload_file_name, null=True, blank=True,
                                  verbose_name="Course File Index",
                                  validators=[validate_file_size, validate_file_type], max_length=1024)
    report_cfr = models.FileField(upload_to=get_upload_file_name, null=True, blank=True,
                                  verbose_name="Course File Requirements",
                                  validators=[validate_file_size, validate_file_type], max_length=1024)

    # review part --------------------------------------------------------------------------------------
    cfi_version = models.IntegerField(verbose_name="Version", default=0)
    cfi_report_state = models.IntegerField(verbose_name="State", default=ReportState.CREATED.value)
    cfi_remarks = models.TextField(verbose_name="Remarks", default='', null=True, blank=True)
    cfi_reviewer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='cfi_reviews')

    # ---------------------------------------------------------------------------------------------------

    def __str__(self):
        return ' CFI File Index for section ' + str(self.gradeFile.section_code) + ' ('
        str(self.submission_time) + ')'

    def campus(self):
        return f'[{self.gradeFile.campus_name}'

    campus.allow_tags = True

    def courseFullName(self):
        return f'[{self.gradeFile.course_code}] ---  {self.gradeFile.course_name}'

    courseFullName.allow_tags = True

    def department(self):
        return f'[{self.gradeFile.section_department}'

    department.allow_tags = True

    def section(self):
        return self.gradeFile.section_code

    section.allow_tags = True

    def teacher(self):
        return f'[{self.gradeFile.teacher}'

    teacher.allow_tags = True

    def semester(self):
        return f'[{self.gradeFile.semester}'

    semester.allow_tags = True

    def getRemarks(self):
        res = []
        for line in self.cfi_remarks.split('\n'):
            try:
                row = line.split(':::::')
                _tmp = {}
                _version = row[0]
                _time = row[1]
                _remark = row[2]
                _user = row[3]
                __str = f'[Version={_version},  Date={_time},   Reviewer={_user}]   {_remark}'
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
        _str = f'{self.cfi_version}{_separator}{current_time}{_separator}{remark}{_separator}{user}'
        self.cfi_remarks = self.cfi_remarks + '\n' + _str

    def getReviewstate(self):
        if self.cfi_report_state == ReportState.CREATED.value:
            return 'CREATED'
        if self.cfi_report_state == ReportState.SUBMITTED.value:
            return 'SUBMITTED'
        if self.cfi_report_state == ReportState.ACCEPTED.value:
            return 'ACCEPTED'
        if self.cfi_report_state == ReportState.NEEDS_REVIEW.value:
            return 'NEEDS REVIEW'

    def validate(self, user):
        self.cfi_report_state = ReportState.ACCEPTED.value
        self.cfi_reviewer = user
        ## mail
        mail_subject = f'Update status for the quality files report for section {self.gradeFile.section_code}'
        mail_message = f'Dear faculty member, we want to notice that the quality files for the section {self.gradeFile.section_code} are accepted. Best regards'
        self.sendEmail(self.gradeFile.teacher.email, mail_subject, mail_message)

        self.save()

    def refuse(self, user):
        self.cfi_report_state = ReportState.NEEDS_REVIEW.value
        self.cfi_reviewer = user

        ## mail
        mail_subject = f'Update status for the quality files for section {self.gradeFile.section_code}'
        mail_message = f'Dear faculty member, we want to notice that the quality files for the section {self.gradeFile.section_code} need revision. Best regards'
        self.sendEmail(self.gradeFile.teacher.email, mail_subject, mail_message)

        self.save()

    def submit(self, update=False, reviewer_email=''):

        if self.cfi_report_state == ReportState.NEEDS_REVIEW.value:
            self.cfi_version = self.cfi_version + 1
            self.cfi_report_state = ReportState.SUBMITTED.value
            self.save()

            ## mail to the reviewer
            mail_subject = f'New quality files to review for the section {self.gradeFile.section_code} are submitted'
            mail_message = f'Dear faculty member and Quality Unit member, we want to notice that Quality Files for the section {self.gradeFile.section_code} are submitted and needs your review. Best regards'
            self.sendEmail(reviewer_email, mail_subject, mail_message)
            ## mail to teacher
            mail_subject = f'Update status for the quality files for section {self.gradeFile.section_code}'
            mail_message = f'Dear faculty member, we want to notice that the quality files for the section {self.gradeFile.section_code} are submitted and are under review. Best regards'
            self.sendEmail(self.gradeFile.teacher.email, mail_subject, mail_message)

            return

        if self.cfi_report_state == ReportState.CREATED.value and update == True:
            self.cfi_report_state = ReportState.SUBMITTED.value
            self.save()

            ## mail to the reviewer
            mail_subject = f'New quality files to review for the section {self.gradeFile.section_code} are submitted'
            mail_message = f'Dear faculty member and Quality Unit member, we want to notice that Quality Files for the section {self.gradeFile.section_code} are submitted and needs your review. Best regards'
            self.sendEmail(reviewer_email, mail_subject, mail_message)
            ## mail to teacher
            mail_subject = f'Update status for the quality files for section {self.gradeFile.section_code}'
            mail_message = f'Dear faculty member, we want to notice that the quality files for the section {self.gradeFile.section_code} are submitted and are under review. Best regards'
            self.sendEmail(self.gradeFile.teacher.email, mail_subject, mail_message)

            return

    def sendEmail(self, receiver_email, title, message):
        from _data._data_emails import email
        __email = email(email_receiver=receiver_email, email_title=title, email_message=message)
        __email.save()
        __email.send()

    def end(self):
        ## mail
        mail_subject = f'Update status for the quality files for section {self.gradeFile.section_code}'
        mail_message = f'Dear faculty member, we want to notice that the quality reports for the section {self.gradeFile.section_code} is deleted. Best Regards'
        self.sendEmail(self.gradeFile.teacher.email, mail_subject, mail_message)
        self.delete()

    def is_validated(self):
        if self.cfi_report_state == ReportState.ACCEPTED.value:
            return True
        return False

    def is_submitted(self):
        if self.cfi_report_state == ReportState.SUBMITTED.value:
            return True
        return False

    def is_refused(self):
        if self.cfi_report_state == ReportState.NEEDS_REVIEW.value:
            return True
        return False

    class Meta:
        ordering = ['course_cfi_id', 'submission_time']
        verbose_name_plural = "Course File Index Files"
        verbose_name = "Course File Index File"
        indexes = [
            models.Index(fields=['submission_time', ]),
            models.Index(fields=['gradeFile', ]),
        ]


class QualityExportFile(models.Model):
    quality_export_file_id = models.BigAutoField(primary_key=True, verbose_name="Quality Export File ID")
    submission_time = models.DateTimeField(auto_now=True, verbose_name="Submission time")

    export_file = models.FileField(upload_to=get_quality_export_file_name, null=True, blank=True,
                                   max_length=1024)

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True, blank=True)
    state = models.IntegerField(verbose_name="State", default=0)  # 0 --> in progress, 1 --> done, -1 --> Error
    elapsedTime = models.TextField(verbose_name="Elapsed Time", default='')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    quality_type = models.TextField(verbose_name="Quality Type", default='')

    exec_trace = models.TextField(verbose_name="Execution trace", default='')
    exec_trace_file = models.FileField(upload_to=get_quality_export_logtrace_filename, null=True, blank=True,
                                       max_length=1024)

    def __str__(self):
        return ' Quality Export File : ' + str(
            self.semester.semester_academic_year.academic_year_name) + '--' + str(
            self.semester.semester_name) + ' (' + str(self.submission_time) + ')'

    class Meta:
        ordering = ['semester', 'submission_time', 'state']
        verbose_name_plural = "Quality Export Files"
        verbose_name = "Quality Export File"
        indexes = [
            models.Index(fields=['submission_time', ]),
            models.Index(fields=['semester', ]),
            models.Index(fields=['teacher', ]),
            models.Index(fields=['state', ]),
        ]

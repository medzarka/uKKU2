# -*- coding: utf-8 -*-
from time import strftime, gmtime
from django.core.files import File
from django.contrib.auth.models import User, Group
from django.conf import settings
from docxtpl import DocxTemplate

from _control._Measurement.Measurement_FS import Quality_FS
import os

from _data._data_quality import ReportState
import threading
import time
import shutil
import os
from _data._data_measurement import GradesFile, CourseFile, DepartmentFile, MeasurementExportFile
from django.core.files import File

from _data._data_measurement import Department
from _data._data_quality import Course_CFI, QualityExportFile
from _data._data_schedule import Meeting

from random import randint
from datetime import datetime


class QualityArchiveMakerThread(threading.Thread):
    __a_thread_is_working = False
    _lock = threading.Lock()
    _lock2 = threading.Lock()
    _thread_dict = {}

    @classmethod
    def isActiveThread(cls, id):
        with QualityArchiveMakerThread._lock2:
            if id in cls._thread_dict.keys():
                return True
            else:
                return False

    def __init__(self, semester, teacher, department, quality, verbose=False):

        threading.Thread.__init__(self)
        self._selected_semester = semester
        self._teacher = teacher
        self.trace = ''
        self.verbose = verbose
        self.selected_department = department
        self.quality_type = quality

        print('#################  QualityArchiveMakerThread is created')

    def make_archive(self, source, destination):
        base_name = '.'.join(destination.split('.')[:-1])
        format = destination.split('.')[-1]
        root_dir = os.path.dirname(source)
        base_dir = os.path.basename(source.strip(os.sep))
        shutil.make_archive(base_name, format, root_dir, base_dir)

    def createDir(self, path):
        try:
            os.makedirs(path)
        except FileExistsError as e:
            pass  # print('1' + str(e))
        except FileNotFoundError as ee:
            pass  # print('2' + str(ee))

    def addLogTrace(self, msg):
        if self.verbose:
            print(msg.replace('<br>', ''))
        self.trace += '\n' + msg

    @property
    def LogTrace(self):
        return self.trace

    def generate_quality_cfr_report(self, _cfi_obj, _meeting_obj):
        if _cfi_obj is None:
            return False
        else:

            if _cfi_obj.cfi_report_state == ReportState.ACCEPTED.value:
                try:
                    cfr_filename = os.path.join(settings.DATA_DIR, 'media', Quality_FS.TMP.value,
                                                'cfr_report_' + str(_cfi_obj.course_cfi_id) + '.docx')
                    cfi_filename = os.path.join(settings.DATA_DIR, 'media', Quality_FS.TMP.value,
                                                'cfi_report_' + str(_cfi_obj.course_cfi_id) + '.docx')

                    _data = {}
                    _data['id'] = _cfi_obj.course_cfi_id
                    _data['time'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    _data['course_code'] = _meeting_obj.course.course_code
                    _data['course_name'] = _meeting_obj.course.course_name
                    _data['section_code'] = _cfi_obj.gradeFile.section_code
                    _data['teacher'] = _cfi_obj.gradeFile.teacher.last_name
                    _data['date'] = str(_cfi_obj.submission_time)[:16]
                    _data[
                        'cs_filename'] = f'01_{_meeting_obj.course.course_code}_CS.{_cfi_obj.course_specification_file.name.split(".")[-1]}'
                    _data[
                        'samples_filename'] = f'02_{_meeting_obj.course.course_code}_SAMPLES.{_cfi_obj.exams_samples_file.name.split(".")[-1]}'
                    _data[
                        'marks_filename'] = f'03_{_meeting_obj.course.course_code}_MARKS.{_cfi_obj.marks_file.name.split(".")[-1]}'
                    _data[
                        'clo_filename'] = f'04_{_meeting_obj.course.course_code}_CLO.{_cfi_obj.clos_measurement_file.name.split(".")[-1]}'
                    _data[
                        'cr_filename'] = f'05_{_meeting_obj.course.course_code}_CR.{_cfi_obj.course_report_file.name.split(".")[-1]}'
                    try:
                        tmp = _cfi_obj.kpis_measurements_file.path
                        _data[
                            'kpi_filename'] = f'06_{_meeting_obj.course.course_code}_KPI.{_cfi_obj.kpis_measurements_file.name.split(".")[-1]}'
                    except:
                        _data['kpi_filename'] = 'N/A'
                    _data[
                        'timetable_filename'] = f'07_FACULTY_TIMETABLE.{_cfi_obj.instructor_schedule_file.name.split(".")[-1]}'
                    _data[
                        'course_plan_filename'] = f'08_{_meeting_obj.course.course_code}_CP.{_cfi_obj.course_plan_file.name.split(".")[-1]}'
                    _data[
                        'measurement_filename'] = f'9_{_meeting_obj.course.course_code}_MEASUREMENT.{_cfi_obj.gradeFile.report_file.name.split(".")[-1]}'
                    _data[
                        'cv_filename'] = f'10_FACULTY_CV.{_cfi_obj.curriculum_vitae_file.name.split(".")[-1]}'
                    _data['reviewer'] = _cfi_obj.cfi_reviewer.last_name
                    _data['head'] = User.objects.get(username=13571).last_name
                    _data['program'] = _meeting_obj.course.program.program_name
                    _data['department'] = _cfi_obj.gradeFile.section_department.department_name
                    _data['semester'] = _cfi_obj.gradeFile.semester

                    # generate CFR report
                    if self.quality_type == 'cfr':
                        _template_cfr_report = os.path.join('media/' + Quality_FS.TEMPLATES.value, 'cfr_template.docx')
                        tpl = DocxTemplate(_template_cfr_report)
                        tpl.render(_data)
                        tpl.save(cfr_filename)
                        _cfi_obj.report_cfr.save(
                            f'0_{_meeting_obj.course.course_code}_Checklist_Course_File_Requirements.docx',
                            File(open(cfr_filename, 'rb')))
                        os.remove(cfr_filename)

                    # generate CFI report
                    if self.quality_type == 'cfi':
                        _template_cfi_report = os.path.join('media/' + Quality_FS.TEMPLATES.value, 'cfi_template.docx')
                        tpl = DocxTemplate(_template_cfi_report)
                        tpl.render(_data)
                        tpl.save(cfi_filename)
                        _cfi_obj.report_cfi.save(f'0_{_meeting_obj.course.course_code}_CourseFileIndex.docx',
                                                 File(open(cfi_filename, 'rb')))
                        os.remove(cfi_filename)

                    # save the CFI obj
                    self.addLogTrace(f'          [INFO] Updating the CFI object after creating the CFI/CFR.<br>')
                    _cfi_obj.save()

                    return True


                except Exception as e:
                    self.addLogTrace(f'          [ERROR] # An error {str(e)}<br>')
                    return False
            else:
                self.addLogTrace(f'          [WARN] The CFI is not accepted yet. Ignore creating the CFR/CFI.<br>')
                return False

    def run(self):

        with QualityArchiveMakerThread._lock:

            if QualityArchiveMakerThread.__a_thread_is_working == False:
                QualityArchiveMakerThread.__a_thread_is_working = True
            else:
                print("Another thread is working, ignoring !")
                return 0

        start_time = datetime.now()
        try:
            year_txt = self._selected_semester.semester_academic_year.academic_year_name.replace(' ', '').replace('-',
                                                                                                                  '_')
            term_txt = self._selected_semester.semester_name.replace(' ', '')

            _export = QualityExportFile()
            _export.semester = self._selected_semester
            _export.teacher = self._teacher
            _export.department = self.selected_department
            _export.quality_type = self.quality_type
            _export.save()
            QualityArchiveMakerThread._thread_dict[_export.quality_export_file_id] = ''

            self.addLogTrace(' # The quality Export File record is created<br>')

            filename = f'{self.quality_type}__Quality__{year_txt}_{term_txt}_{str(_export.submission_time)[:22]}'
            _basedir = os.path.join('/', 'tmp', 'uKKU', filename)
            self.createDir(_basedir)
            self.addLogTrace(f' # The tmp quality export base folder is created: {_basedir}.<br>')

            for _dep in Department.objects.all():

                if _dep.department_id == self.selected_department.department_id:
                    self.addLogTrace(f'<br><br>####################################################<br>')
                    self.addLogTrace(f'<br><br>####################################################<br>')
                    self.addLogTrace(f'# Working with the department: {_dep.department_name}<br>')

                    _departments_dir = os.path.join(_basedir, _dep.department_name.split(' --')[0])
                    self.createDir(_departments_dir)
                    self.addLogTrace(f'      The department dir is created: {_departments_dir}<br>')

                    for _cfi_report in Course_CFI.objects.filter(gradeFile__semester=self._selected_semester,
                                                                 gradeFile__section_department=_dep):
                        self.addLogTrace('<br>_____________________________<br>')
                        self.addLogTrace(f'[INFO] Working with the section: {_cfi_report.gradeFile.section_code}<br>')

                        ## extract valuable data

                        _the_section_code = _cfi_report.gradeFile.section_code

                        self.addLogTrace(f'          [INFO] The section code is: {_the_section_code}<br>')
                        self.addLogTrace(f'          [INFO] The semester is: {self._selected_semester}<br>')
                        self.addLogTrace(f'          [INFO] The campus is: {_cfi_report.gradeFile.campus_name}<br>')

                        ___meeting = Meeting.objects.get(semester=self._selected_semester, section=_the_section_code,
                                                         teacher=_cfi_report.gradeFile.teacher,
                                                         department=_cfi_report.gradeFile.section_department)

                        ##### create the CFI and the CFR reports only if the work is accepted
                        report_gen_result = self.generate_quality_cfr_report(_cfi_report, ___meeting)
                        if report_gen_result == True:
                            self.addLogTrace('          [INFO] CFR and CFI are generated.<br>')
                        else:
                            self.addLogTrace('          [WARN] CFR and CFI are not generated.<br>')

                        ___course_name = ___meeting.course.course_name
                        ___course_code = ___meeting.course.course_code

                        ___section_department = _cfi_report.gradeFile.section_department.department_name
                        ___section_teacher = ___meeting.teacher.last_name.replace(' ', '_')
                        try:
                            ___report_reviwer = _cfi_report.cfi_reviewer.last_name.replace(' ', '_')
                        except:
                            ___report_reviwer = 'Not assigned'
                        ___report_date = _cfi_report.submission_time
                        self.addLogTrace(
                            f'          [INFO] The section code (verification) is: {___meeting.section}<br>')
                        self.addLogTrace(f'          [INFO] The course name is: {___meeting.course.course_name}<br>')
                        self.addLogTrace(f'          [INFO] The course code is: {___meeting.course.course_code}<br>')
                        self.addLogTrace(f'          [INFO] The department is: {___section_department}<br>')
                        self.addLogTrace(f'          [INFO] The Teacher is: {___section_teacher}<br>')

                        ## we start with the Course File Requirement (CFR) and Course File Index (CFI) Folders

                        _faculty_dir = os.path.join(_departments_dir,
                                                    _cfi_report.gradeFile.teacher.last_name)
                        self.createDir(_faculty_dir)
                        _courses_dir = os.path.join(_faculty_dir, _cfi_report.gradeFile.course_name.replace('-', ' '))
                        self.createDir(_courses_dir)
                        _section_dir = os.path.join(_courses_dir, f'section_{_cfi_report.gradeFile.section_code}')
                        self.createDir(_section_dir)

                        _section_dir_cfr = os.path.join(_section_dir, 'CFR')
                        _section_dir_cfi = os.path.join(_section_dir, 'CFI')

                        if self.quality_type == 'cfr':
                            self.createDir(_section_dir_cfr)
                        if self.quality_type == 'cfi':
                            self.createDir(_section_dir_cfi)

                        ___cfr_mydata = {}
                        ___cfi_mydata = {}
                        try:
                            __theKey = f'01_{___course_code}_CS.{_cfi_report.course_specification_file.path.split(".")[-1]}'
                            ___cfr_mydata[__theKey] = _cfi_report.course_specification_file.path
                            ___cfi_mydata[__theKey] = _cfi_report.course_specification_file.path
                        except:
                            self.addLogTrace(
                                f'          [ERROR] !!! An error was occured when working with the course specification file CFI for section {_cfi_report.gradeFile.section_code}<br>')

                        try:
                            __theKey = f'02_{___course_code}_Samples.{_cfi_report.exams_samples_file.path.split(".")[-1]}'
                            ___cfr_mydata[__theKey] = _cfi_report.exams_samples_file.path
                            ___cfi_mydata[__theKey] = _cfi_report.exams_samples_file.path
                        except:
                            self.addLogTrace(
                                f'          [ERROR] !!! An error was occured when working with the exam example file CFI for section {_cfi_report.gradeFile.section_code}<br>')
                        try:
                            __theKey = f'03_{___course_code}_Marks.{_cfi_report.marks_file.path.split(".")[-1]}'
                            ___cfr_mydata[__theKey] = _cfi_report.marks_file.path
                            ___cfi_mydata[__theKey] = _cfi_report.marks_file.path
                        except:
                            self.addLogTrace(
                                f'          [ERROR] !!! An error was occured when working with the mark file CFI for section {_cfi_report.gradeFile.section_code}<br>')
                            print(
                                f'################## An error was occured when working with the mark file CFI for section {_cfi_report.gradeFile.section_code}<br>')

                        try:
                            __theKey = f'4_{___course_code}_clo.{_cfi_report.clos_measurement_file.path.split(".")[-1]}'
                            ___cfr_mydata[__theKey] = _cfi_report.clos_measurement_file.path
                            ___cfi_mydata[__theKey] = _cfi_report.clos_measurement_file.path

                        except:
                            self.addLogTrace(
                                f'          [ERROR] !!! An error was occured when working with the CLOs file CFI for section {_cfi_report.gradeFile.section_code}<br>')

                        try:
                            __theKey = f'5_{___course_code}_CR.{_cfi_report.course_report_file.path.split(".")[-1]}'
                            ___cfr_mydata[__theKey] = _cfi_report.course_report_file.path
                            ___cfi_mydata[__theKey] = _cfi_report.course_report_file.path

                        except:
                            self.addLogTrace(
                                f'          [ERROR] !!! An error was occured when working with the course report file CFI for section {_cfi_report.gradeFile.section_code}<br>')

                        try:
                            ___cfr_mydata[
                                f'6_{___course_code}_KPI.{_cfi_report.kpis_measurements_file.path.split(".")[-1]}'] = _cfi_report.kpis_measurements_file.path
                        except:
                            self.addLogTrace(
                                f'          [ERROR] !!! An error was occured when working with the KPIs CFI for section {_cfi_report.gradeFile.section_code}<br>')

                        try:
                            ___cfr_mydata[
                                f'7_{___section_teacher}_FS.{_cfi_report.instructor_schedule_file.path.split(".")[-1]}'] = _cfi_report.instructor_schedule_file.path
                        except:
                            self.addLogTrace(
                                f'          [ERROR] !!! An error was occured when working with the instructor schedule file CFI for section {_cfi_report.gradeFile.section_code}<br>')

                        try:
                            ___cfr_mydata[
                                f'8_{___course_code}_CP.{_cfi_report.course_plan_file.path.split(".")[-1]}'] = _cfi_report.course_plan_file.path
                        except:
                            self.addLogTrace(
                                f'          [ERROR] !!! An error was occured when working with the course plan file CFI for section {_cfi_report.gradeFile.section_code}<br>')

                        try:
                            ___cfr_mydata[
                                f'9_{___course_code}_SR.{_cfi_report.gradeFile.report_file.path.split(".")[-1]}'] = _cfi_report.gradeFile.report_file.path
                        except:
                            self.addLogTrace(
                                f'          [ERROR] !!! An error was occured when working with the statistical file CFI for section {_cfi_report.gradeFile.section_code}<br>')

                        try:
                            ___cfr_mydata[
                                f'10_{___section_teacher}_CV.{_cfi_report.curriculum_vitae_file.path.split(".")[-1]}'] = _cfi_report.curriculum_vitae_file.path
                        except:
                            self.addLogTrace(
                                f'          [ERROR] !!! An error was occured when working with the curriculum vitae file CFI for section {_cfi_report.gradeFile.section_code}<br>')

                        try:
                            ___cfi_mydata[
                                f'0_{___meeting.course.course_code}_CourseFileIndex.docx'] = _cfi_report.report_cfi.path
                        except Exception as e:
                            print(str(e))
                            self.addLogTrace(
                                f'          [ERROR] !!! An error was occured when working with the Course File Index for section {_cfi_report.gradeFile.section_code}<br>')

                        try:
                            ___cfr_mydata[
                                f'0_{___meeting.course.course_code}_Checklist_Course_File_Requirements.docx'] = _cfi_report.report_cfr.path
                        except Exception as e:
                            print(str(e))
                            self.addLogTrace(
                                f'          [ERROR] !!! An error was occured when working with the Course File Requirements for section {_cfi_report.gradeFile.section_code}<br>')

                        # copy CFR files
                        if self.quality_type == 'cfr':
                            for key, value in ___cfr_mydata.items():
                                dst = os.path.join(_section_dir_cfr, key)
                                shutil.copyfile(value, dst)

                        # copy CFI files
                        if self.quality_type == 'cfi':
                            for key, value in ___cfi_mydata.items():
                                dst = os.path.join(_section_dir_cfi, key)
                                shutil.copyfile(value, dst)

            source = _basedir
            destination = _basedir + '__.zip'

            self.addLogTrace('<br>------------------------------<br>')
            self.addLogTrace('[INFO] Start creating the archive file<br>')
            self.make_archive(source, destination)
            self.addLogTrace('[INFO] Completing creating the archive file<br>')
            shutil.rmtree(_basedir)
            self.addLogTrace('[INFO] The tmp folder was correctly deleted<br>')
            end_time = datetime.now()
            self.addLogTrace('[DEBUG] source = ' + destination)
            self.addLogTrace('[DEBUG] destination  = ' + filename)

            _export.export_file.save(filename, File(open(destination, 'rb')))
            self.addLogTrace('[INFO] The archive file was correctly updated in the database<br>')
            _export.elapsedTime = '{}'.format(end_time - start_time)

            exec_log_filename = os.path.join(settings.DATA_DIR, 'media', Quality_FS.TMP.value, 'log_trace.txt')
            with open(exec_log_filename, 'w') as f:
                f.write(self.LogTrace.replace('<br>', ''))
            _export.exec_trace_file.save('exec_log_trace.txt', File(open(exec_log_filename, 'rb')))

            _export.exec_trace = self.LogTrace
            self.addLogTrace('[INFO] The exec log trace file was correctly updated in the database<br>')

            _export.state = 1
            _export.save()

            os.remove(destination)
            os.remove(exec_log_filename)


        except Exception as eee:
            self.addLogTrace('[ERROR] !!! An error was occurred  ' + str(eee) + '<br>')
            end_time = datetime.now()
            _export.state = -1
            _export.elapsedTime = '{}'.format(end_time - start_time)
            _export.exec_trace = self.LogTrace
            _export.save()

        with QualityArchiveMakerThread._lock:
            QualityArchiveMakerThread.__a_thread_is_working = False

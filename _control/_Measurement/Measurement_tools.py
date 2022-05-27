# -*- coding: utf-8 -*-
from time import strftime, gmtime

from django.contrib.auth.models import User
import os
import xlrd as xl
import statistics

from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.files.temp import NamedTemporaryFile
from scipy.stats import pearsonr
from scipy.stats import skew
from scipy.stats import norm
import matplotlib
from matplotlib import pyplot as plt
import tempfile
from docxtpl import DocxTemplate, RichText, InlineImage, Listing
from docx.shared import Mm, Inches, Pt
import datetime
import scipy
import numpy as np
from threading import BoundedSemaphore
import arabic_reshaper
from bidi.algorithm import get_display
from bidi import algorithm as bidialg
import math
from collections import OrderedDict
import json

from _control._Measurement.Measurement_FS import Measurement_FS
from _data._data_measurement import GradesFile, CourseFile, ReportState

matplotlib.use('Agg')
max_items = 1
sem = BoundedSemaphore(max_items)

##################### Measurement Shared Config
_reports_dir = 'repositories/units/measurements/reports/'
_templates_dir = 'repositories/units/measurements/Templates/version1/'

_template_section_report = _templates_dir + 'section_report_template.docx'
_template_course_report = _templates_dir + 'course_report_template.docx'
_template_department_report = _templates_dir + 'department_report_template.docx'


class Section_Measurment:

    def __init__(self, filename=None, user=None, semester=None, report_obj=None):
        self.semester = semester
        self.grades_filename = filename
        self.user = user
        self.location_name = ''
        self.section_code = ''
        self.course_name = ''

        self.grades_file_obj = report_obj

        self.errors = []
        self.info = []
        self.warning = []

        self.grades = {}

        self.statistics_tools = MEASUREMENT_Common()
        self.mean = 9999.9999
        self.std = 9999.9999
        self.correlation_value = 9999.9999
        self.correlation_sig = 9999.9999
        self.skewness = 9999.9999
        self.min = 9999.9999
        self.max = 9999.9999

        self.dataloaded = False

    def getReportObj(self):

        if self.grades_file_obj is None:
            if self.dataloaded:
                try:
                    _filereport = GradesFile.objects.get(section_code=self.section_code, semester=self.semester,
                                                         campus_name=self.location_name)
                except GradesFile.DoesNotExist:
                    _filereport = GradesFile()

                _filereport.course_name = self.course_name
                _filereport.campus_name = self.location_name
                _filereport.section_code = self.section_code

                _data = self.compute_statistics()
                _filereport.stat_mean = _data['mean']
                _filereport.stat_std = _data['std']
                _filereport.stat_skewness = _data['skewness']
                _filereport.stat_correlation_value = _data['correlation_value']
                _filereport.stat_correlation_sig = _data['correlation_sig']
                _filereport.stat_min = _data['min']
                _filereport.stat_max = _data['max']
                _filereport.stat_analysis = _data['analysis']
                _filereport.stat_histogram.save('histogram_section_' + str(self.section_code) + '.png',
                                                File(open(_data['stat_histogram'], 'rb')))
                _filereport.grades_file = self.grades_filename
                _filereport.teacher = self.user
                _filereport.semester = self.semester

                __data = json.dumps(self.grades)
                _filereport.grades_data = __data

                _filereport.save()
                self.grades_file_obj = _filereport

                return _filereport

            else:
                return None
        else:
            return self.grades_file_obj

    def extract_data(self):
        mids = []
        finals = []
        totals = []
        try:
            tmp_file = os.path.join('media/' + Measurement_FS.TMP.value, self.grades_filename.name)
            os.makedirs(os.path.dirname(tmp_file), exist_ok=True)
            with open(tmp_file, 'wb+') as destination:
                for chunk in self.grades_filename.chunks():
                    destination.write(chunk)

            workbook = xl.open_workbook(tmp_file, on_demand=True)
            worksheet = workbook.sheet_by_index(0)
            try:
                ____tmp = worksheet.cell_value(6, 5)
            except IndexError:
                ____tmp = ''
            self.section_code = int(worksheet.cell_value(4, 1))
            self.location_name = worksheet.cell_value(0, 1)
            self.course_name = worksheet.cell_value(2, 1)
            if self.section_code == '':
                raise Exception('Unable to read the section from the excel file !!!')
            if self.location_name == '':
                raise Exception('Unable to read the location from the excel file !!!')
            if self.course_name == '':
                raise Exception('Unable to read the course name from the excel file !!!')

            __line = 7
            if ____tmp == '':  # grades without mids
                print('Grades without mids')
                while True:
                    try:
                        __student = worksheet.cell_value(__line, 0)
                        if worksheet.cell_value(__line, 2) != '':
                            finals.append(float(worksheet.cell_value(__line, 2)))
                        if worksheet.cell_value(__line, 3) != '':
                            totals.append(float(worksheet.cell_value(__line, 3)))
                        __line += 1
                    except IndexError:
                        break
                print('---' + str(totals))
                print('---' + str(finals))
            else:
                while True:
                    try:
                        __student = worksheet.cell_value(__line, 0)
                        if worksheet.cell_value(__line, 2) != '':
                            mids.append(float(worksheet.cell_value(__line, 2)))
                        if worksheet.cell_value(__line, 3) != '':
                            finals.append(float(worksheet.cell_value(__line, 3)))
                        if worksheet.cell_value(__line, 4) != '':
                            totals.append(float(worksheet.cell_value(__line, 4)))
                        __line += 1
                    except IndexError:
                        break
            self.grades['mids'] = mids
            self.grades['finals'] = finals
            self.grades['totals'] = totals

            self.info.append('The grade Excel file was well parsed. ')
            self.dataloaded = True
            os.remove(tmp_file)
            return True

        except ValueError as e:
            self.errors.append(
                'Please use the grade file provided by the registration portal (Academia) without any change 1.')
            self.errors.append(str(e))
            # self.errors.append(str(e.__cause__))

        except Exception as e:
            self.errors.append(str(e))
            # self.errors.append(str(e.__cause__))
        return False

    def generate_report(self):
        if self.grades_file_obj is None:
            return False
        else:
            try:
                filename = os.path.join('media/' + Measurement_FS.TMP.value,
                                        'section_report_' + str(self.grades_file_obj.section_code) + '.docx')
                _data = {}
                _data['campus'] = self.grades_file_obj.campus_name
                _data['department'] = self.grades_file_obj.section_department
                _data['course'] = self.grades_file_obj.course_name
                _data['section'] = str(self.grades_file_obj.section_code)
                _data['max_grade'] = '100'
                _data['mean'] = self.grades_file_obj.stat_mean
                _data['std'] = self.grades_file_obj.stat_std
                _data['skewness'] = self.grades_file_obj.stat_skewness
                _data['correlation'] = self.grades_file_obj.stat_correlation_value
                _data['sig'] = self.grades_file_obj.stat_correlation_sig
                _data['min'] = self.grades_file_obj.stat_min
                _data['max'] = self.grades_file_obj.stat_max
                _data['analysis'] = self.grades_file_obj.teacher_analysis
                _data['histogram_file'] = self.grades_file_obj.stat_histogram
                _data['id'] = self.grades_file_obj.grades_file_id
                _data['time'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                self.statistics_tools.generate_section_docx_report(_data, self.grades_file_obj.grades_file_id, filename)
                self.grades_file_obj.report_file.save(
                    'section_report_' + str(self.grades_file_obj.section_code) + '.docx',
                    File(open(filename, 'rb')))
                self.grades_file_obj.save()
                return True
            except Exception as e:
                print('Error ' + str(e))
                return False

    def extractGrades(self):
        mids = []
        finals = []
        totals = []
        try:

            workbook = xl.open_workbook(self.grades_file_obj.grades_file.path, on_demand=True)
            worksheet = workbook.sheet_by_index(0)

            try:
                ____tmp = worksheet.cell_value(6, 5)
            except IndexError:
                ____tmp = ''

            self.section_code = int(worksheet.cell_value(4, 1))
            self.location_name = worksheet.cell_value(0, 1)
            self.course_name = worksheet.cell_value(2, 1)

            if self.section_code == '':
                raise Exception('Unable to read the section from the excel file !!!')
            if self.location_name == '':
                raise Exception('Unable to read the location from the excel file !!!')
            if self.course_name == '':
                raise Exception('Unable to read the course name from the excel file !!!')

            __line = 7
            if ____tmp == '':  # grades without mids
                while True:
                    try:
                        __student = worksheet.cell_value(__line, 0)
                        if worksheet.cell_value(__line, 2) != '':
                            finals.append(float(worksheet.cell_value(__line, 2)))
                        if worksheet.cell_value(__line, 3) != '':
                            totals.append(float(worksheet.cell_value(__line, 3)))
                        __line += 1
                    except IndexError:
                        break
            else:
                while True:
                    try:
                        __student = worksheet.cell_value(__line, 0)
                        if worksheet.cell_value(__line, 2) != '':
                            mids.append(float(worksheet.cell_value(__line, 2)))
                        if worksheet.cell_value(__line, 3) != '':
                            finals.append(float(worksheet.cell_value(__line, 3)))
                        if worksheet.cell_value(__line, 4) != '':
                            totals.append(float(worksheet.cell_value(__line, 4)))
                        __line += 1
                    except IndexError:
                        break
            self.grades['mids'] = mids
            self.grades['finals'] = finals
            self.grades['totals'] = totals

            self.info.append('The grade Excel file was well loaded. ')
            self.grades_file_obj.course_name = self.course_name
            self.grades_file_obj.campus_name = self.location_name
            self.grades_file_obj.section_code = self.section_code

            _data = self.compute_statistics()
            self.grades_file_obj.stat_mean = _data['mean']
            self.grades_file_obj.stat_std = _data['std']
            self.grades_file_obj.stat_skewness = _data['skewness']
            self.grades_file_obj.stat_correlation_value = _data['correlation_value']
            self.grades_file_obj.stat_correlation_sig = _data['correlation_sig']
            self.grades_file_obj.stat_min = _data['min']
            self.grades_file_obj.stat_max = _data['max']
            self.grades_file_obj.stat_analysis = _data['analysis']
            self.grades_file_obj.stat_histogram.save('histogram_section_' + str(self.section_code) + '.png',
                                                     File(open(_data['stat_histogram'], 'rb')))

            self.grades_file_obj.save()
            return True

        except ValueError as e:
            self.errors.append(
                'Please use the grade file provided by the registration portal (Academia) without any change 2.')
            self.errors.append(str(e))
            # self.errors.append(str(e.__cause__))

        except Exception as e:
            self.errors.append(str(e))
            # self.errors.append(str(e.__cause__))
        return False

    def compute_statistics(self):
        _statistics = {}
        # compute the ttest-Annova values
        _statistics['mean'] = self.statistics_tools.statistics_mean(self.grades['totals'])
        _statistics['std'] = self.statistics_tools.statistics_std_deviation(self.grades['totals'])
        _statistics['skewness'] = self.statistics_tools.statistics_skewness(self.grades['totals'])
        _statistics['correlation_value'] = self.statistics_tools.statistics_pearsonr_correlation_value(
            self.grades['mids'],
            self.grades['finals'])
        _statistics['correlation_sig'] = self.statistics_tools.statistics_pearsonr_correlation_sig(
            self.grades['mids'],
            self.grades['finals'])
        _statistics['min'] = self.statistics_tools.statistics_min(self.grades['totals'])
        _statistics['max'] = self.statistics_tools.statistics_max(self.grades['totals'])
        _statistics['analysis'] = self.statistics_tools.generate_analysis(_statistics)

        tempfile = os.path.join(Measurement_FS.TMP.value, 'histogram_section_' + str(self.section_code) + '.png')
        os.makedirs(os.path.dirname(tempfile), exist_ok=True)
        if self.statistics_tools.statistics_generate_histogram_section(self.grades['totals'], self.section_code,
                                                                       tempfile):
            _statistics['stat_histogram'] = tempfile
        else:
            _statistics['stat_histogram'] = ''

        return _statistics


class ____Section_Measurment:

    def __init__(self, GradesFile_obj):
        self.grades_file_obj = GradesFile_obj
        self.location_name = ''
        self.section_code = ''
        self.course_name = ''

        self.upload_done = False

        self.errors = []
        self.info = []
        self.warning = []

        self.grades = {}

        self.statistics_tools = MEASUREMENT_Common()
        self.mean = 9999.9999
        self.std = 9999.9999
        self.correlation_value = 9999.9999
        self.correlation_sig = 9999.9999
        self.skewness = 9999.9999
        self.min = 9999.9999
        self.max = 9999.9999

    def generate_report(self):
        try:
            filename = os.path.join('media/' + Measurement_FS.TMP.value,
                                    'section_report_' + str(self.section_code) + '.docx')
            _data = {}
            _data['campus'] = self.grades_file_obj.campus_name
            _data['department'] = self.grades_file_obj.section_department
            _data['course'] = self.grades_file_obj.course_name
            _data['section'] = str(self.grades_file_obj.section_code)
            _data['max_grade'] = '100'
            _data['mean'] = self.grades_file_obj.stat_mean
            _data['std'] = self.grades_file_obj.stat_std
            _data['skewness'] = self.grades_file_obj.stat_skewness
            _data['correlation'] = self.grades_file_obj.stat_correlation_value
            _data['correlation'] = self.grades_file_obj.stat_correlation_sig
            _data['min'] = self.grades_file_obj.stat_min
            _data['max'] = self.grades_file_obj.stat_max
            _data['analysis'] = self.grades_file_obj.teacher_analysis
            _data['histogram_file'] = self.grades_file_obj.stat_histogram
            _data['id'] = self.grades_file_obj.grades_file_id
            _data['time'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            self.statistics_tools.generate_section_docx_report(_data, self.grades_file_obj.grades_file_id, filename)
            self.grades_file_obj.report_file.save('section_report_' + str(self.section_code) + '.docx',
                                                  File(open(filename, 'rb')))
            self.grades_file_obj.save()
            return True
        except Exception as e:
            print('Error ' + str(e))
            return False

    def extractGrades(self):
        mids = []
        finals = []
        totals = []
        try:

            workbook = xl.open_workbook(self.grades_file_obj.grades_file.path, on_demand=True)
            worksheet = workbook.sheet_by_index(0)

            try:
                ____tmp = worksheet.cell_value(6, 5)
            except IndexError:
                ____tmp = ''

            self.section_code = int(worksheet.cell_value(4, 1))
            self.location_name = worksheet.cell_value(0, 1)
            self.course_name = worksheet.cell_value(2, 1)

            if self.section_code == '':
                raise Exception('Unable to read the section from the excel file !!!')
            if self.location_name == '':
                raise Exception('Unable to read the location from the excel file !!!')
            if self.course_name == '':
                raise Exception('Unable to read the course name from the excel file !!!')

            __line = 7
            if ____tmp == '':  # grades without mids
                while True:
                    try:
                        __student = worksheet.cell_value(__line, 0)
                        if worksheet.cell_value(__line, 2) != '':
                            finals.append(float(worksheet.cell_value(__line, 2)))
                        if worksheet.cell_value(__line, 3) != '':
                            totals.append(float(worksheet.cell_value(__line, 3)))
                        __line += 1
                    except IndexError:
                        break
            else:
                while True:
                    try:
                        __student = worksheet.cell_value(__line, 0)
                        if worksheet.cell_value(__line, 2) != '':
                            mids.append(float(worksheet.cell_value(__line, 2)))
                        if worksheet.cell_value(__line, 3) != '':
                            finals.append(float(worksheet.cell_value(__line, 3)))
                        if worksheet.cell_value(__line, 4) != '':
                            totals.append(float(worksheet.cell_value(__line, 4)))
                        __line += 1
                    except IndexError:
                        break
            self.grades['mids'] = mids
            self.grades['finals'] = finals
            self.grades['totals'] = totals

            self.info.append('The grade Excel file was well loaded. ')
            self.grades_file_obj.course_name = self.course_name
            self.grades_file_obj.campus_name = self.location_name
            self.grades_file_obj.section_code = self.section_code

            _data = self.compute_statistics()
            self.grades_file_obj.stat_mean = _data['mean']
            self.grades_file_obj.stat_std = _data['std']
            self.grades_file_obj.stat_skewness = _data['skewness']
            self.grades_file_obj.stat_correlation_value = _data['correlation_value']
            self.grades_file_obj.stat_correlation_sig = _data['correlation_sig']
            self.grades_file_obj.stat_min = _data['min']
            self.grades_file_obj.stat_max = _data['max']
            self.grades_file_obj.stat_analysis = _data['analysis']
            self.grades_file_obj.stat_histogram.save('histogram_section_' + str(self.section_code) + '.png',
                                                     File(open(_data['stat_histogram'], 'rb')))

            self.grades_file_obj.save()
            return True

        except ValueError as e:
            self.errors.append(
                'Please use the grade file provided by the registration portal (Academia) without any change 3.')
            self.errors.append(str(e))
            # self.errors.append(str(e.__cause__))

        except Exception as e:
            self.errors.append(str(e))
            # self.errors.append(str(e.__cause__))
        return False

    def compute_statistics(self):
        _statistics = {}
        # compute the ttest-Annova values
        _statistics['mean'] = self.statistics_tools.statistics_mean(self.grades['totals'])
        _statistics['std'] = self.statistics_tools.statistics_std_deviation(self.grades['totals'])
        _statistics['skewness'] = self.statistics_tools.statistics_skewness(self.grades['totals'])
        _statistics['correlation_value'] = self.statistics_tools.statistics_pearsonr_correlation_value(
            self.grades['mids'],
            self.grades['finals'])
        _statistics['correlation_sig'] = self.statistics_tools.statistics_pearsonr_correlation_sig(
            self.grades['mids'],
            self.grades['finals'])
        _statistics['min'] = self.statistics_tools.statistics_min(self.grades['totals'])
        _statistics['max'] = self.statistics_tools.statistics_max(self.grades['totals'])
        _statistics['analysis'] = self.statistics_tools.generate_analysis(_statistics)

        tempfile = os.path.join(Measurement_FS.TMP.value, 'histogram_section_' + str(self.section_code) + '.png')
        os.makedirs(os.path.dirname(tempfile), exist_ok=True)
        if self.statistics_tools.statistics_generate_histogram_section(self.grades['totals'], self.section_code,
                                                                       tempfile):
            _statistics['stat_histogram'] = tempfile
        else:
            _statistics['stat_histogram'] = ''

        return _statistics

    def generate_report(self):
        try:
            filename = os.path.join('media/' + Measurement_FS.TMP.value,
                                    'section_report_' + str(self.section_code) + '.docx')
            _data = {}
            _data['campus'] = self.grades_file_obj.campus_name
            _data['department'] = self.grades_file_obj.section_department
            _data['course'] = self.grades_file_obj.course_name
            _data['section'] = str(self.grades_file_obj.section_code)
            _data['max_grade'] = '100'
            _data['mean'] = self.grades_file_obj.stat_mean
            _data['std'] = self.grades_file_obj.stat_std
            _data['skewness'] = self.grades_file_obj.stat_skewness
            _data['correlation'] = self.grades_file_obj.stat_correlation_value
            _data['correlation'] = self.grades_file_obj.stat_correlation_sig
            _data['min'] = self.grades_file_obj.stat_min
            _data['max'] = self.grades_file_obj.stat_max
            _data['analysis'] = self.grades_file_obj.teacher_analysis
            _data['histogram_file'] = self.grades_file_obj.stat_histogram
            _data['id'] = self.grades_file_obj.grades_file_id
            _data['time'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            self.statistics_tools.generate_section_docx_report(_data, self.grades_file_obj.grades_file_id, filename)
            self.grades_file_obj.report_file.save('section_report_' + str(self.section_code) + '.docx',
                                                  File(open(filename, 'rb')))
            self.grades_file_obj.save()
            return True
        except Exception as e:
            print('Error ' + str(e))
            return False


class Department_Measurment:

    def __init__(self, _grades, _means, info=None):
        self.grades = _grades
        self.means = _means
        self.statistics_tools = MEASUREMENT_Common()
        self.anova_test = 9999.9999
        self.anova_sig = 9999.9999
        self.eta_test = 9999.9999
        self.eta_sig = 9999.9999
        self.info = info

    def __concentrate_(self, *args):
        """ Concentrate input list-like arrays

        """
        v = list(map(np.asarray, args))
        vec = np.hstack(np.concatenate(v))
        return (vec)

    def __ss_between_(self, *args):
        """ Return between-subject sum of squares

        """
        # grand mean
        grand_mean = np.mean(self.__concentrate_(*args))

        ss_btwn = 0
        for a in args:
            ss_btwn += (len(a) * (np.mean(a) - grand_mean) ** 2)

        return (ss_btwn)

    def __ss_total_(self, *args):
        """ Return total of sum of square

        """
        vec = self.__concentrate_(*args)
        ss_total = sum((vec - np.mean(vec)) ** 2)
        return (ss_total)

    def compute_statistics(self):
        _statistics = {}
        _statistics['low_means'] = {}
        _statistics['high_means'] = {}
        _statistics['annova_value'] = float("{0:.4f}".format(-1))
        _statistics['annova_sig'] = float("{0:.4f}".format(-1))
        _statistics['eta'] = float("{0:.4f}".format(-1))
        _statistics['eta_sig'] = float("{0:.4f}".format(-1))

        if len(self.grades.keys()) > 1:  # We have more than one course in the department

            __sorted_means = OrderedDict(sorted(self.means.items(), key=lambda t: t[1]))
            __low_means = {}
            __High_means = {}

            for val in __sorted_means.keys():
                if __sorted_means[val] < 60:
                    __low_means[val] = __sorted_means[val]
                if __sorted_means[val] >= 90:
                    __High_means[val] = __sorted_means[val]

            # print('Low means are ' + str(__low_means))
            # print('High means are ' + str(__High_means))

            _annova_value = -1
            _annova_sig = -1
            _eta_squared = -1
            _eta_test = -1
            if len(self.means.keys()) >= 2:
                _annova_value, _annova_sig = scipy.stats.f_oneway(*
                                                                  [self.grades[val]
                                                                   for val in
                                                                   self.grades.keys()])

                _eta_squared = float(self.__ss_between_(*
                                                        [self.grades[val]
                                                         for val in
                                                         self.grades.keys()]) / self.__ss_total_(*
                                                                                                 [
                                                                                                     self.grades[
                                                                                                         val]
                                                                                                     for
                                                                                                     val
                                                                                                     in
                                                                                                     self.grades.keys()]))
                _eta_test = math.sqrt(_eta_squared)

            _statistics['low_means'] = __low_means
            _statistics['high_means'] = __High_means
            _statistics['annova_value'] = float("{0:.4f}".format(_annova_value))
            _statistics['annova_sig'] = float("{0:.4f}".format(_annova_sig))
            _statistics['eta'] = float("{0:.4f}".format(_eta_squared))
            _statistics['eta_sig'] = float("{0:.4f}".format(_eta_test))

        return _statistics

    def generate_report(self, _doc_id, analysis=''):
        _data = self.compute_statistics()
        if _data is None:
            return None
        else:
            __template_department_report = os.path.join('media/' + Measurement_FS.TEMPLATES.value,
                                                        'department_report_template.docx')
            filename = os.path.join('media/' + Measurement_FS.TMP.value,
                                    'department_report_' + str(_doc_id) + '.docx')

            # Generate the histogram file
            temp1 = tempfile.NamedTemporaryFile(prefix="measurement_histogram_", suffix=".png")
            temp2 = tempfile.NamedTemporaryFile(prefix="measurement_histogram_", suffix=".png")

            _tool2 = MEASUREMENT_Common()
            _tool2.generate_low_high_images(_data, temp1, temp2)

            tpl = DocxTemplate(__template_department_report)

            context = {
                'low_image': InlineImage(tpl, temp1, width=Inches(3), height=Inches(3)),
                'high_image': InlineImage(tpl, temp2, width=Inches(3), height=Inches(3)),
                'time': datetime.datetime.now().strftime("%y-%m-%d, %H:%M:%S"),
                'id': str(_doc_id),
                'analysis': analysis,
            }
            context = {**_data, **context}
            context = {**self.info, **context}
            tpl.render(context)
            tpl.save(filename)
            temp1.close()
            temp2.close()
        return filename


class Course_Measurment:

    def __init__(self, _grades_files_objs=[], user=None, semester=None, course_name=None, course_file_obj=None,
                 department=None):
        self.semester = semester
        self.grades_files_objs = _grades_files_objs
        self.user = user
        self.course_name = course_name
        self.department = department

        self.errors = []
        self.info = []
        self.warning = []

        self.sections = []
        self.campuses = []
        self.course_file_obj = course_file_obj
        self.statistics_tools = MEASUREMENT_Common()

        if self.course_file_obj == None:
            self.dataloaded = False
            self.statisrtics_is_done = False
            self.fused_grades, self.composed_grades = self.extractGrades()
            if self.dataloaded:
                self.statistics = self.compute_statistics()

    def generate_report(self):
        if self.course_file_obj is None:
            return False
        else:
            try:
                filename = os.path.join('media/' + Measurement_FS.TMP.value,
                                        'course_report_' + str(self.course_file_obj.course_name) + '.docx')
                _data = {}
                _data['campus'] = self.course_file_obj.campus_name
                _data['department'] = self.course_file_obj.course_department
                _data['course'] = self.course_file_obj.course_name
                _data['section'] = str(self.course_file_obj.section_codes)
                _data['max_grade'] = '100'
                _data['mean'] = self.course_file_obj.stat_mean
                _data['std'] = self.course_file_obj.stat_std
                _data['skewness'] = self.course_file_obj.stat_skewness
                _data['correlation'] = self.course_file_obj.stat_correlation_value
                _data['sig'] = self.course_file_obj.stat_correlation_sig
                _data['min'] = self.course_file_obj.stat_min
                _data['max'] = self.course_file_obj.stat_max
                if self.course_file_obj.stat_ttest_annova == 'TTEST':
                    _data['ttest'] = True
                    _data['annova'] = False
                if self.course_file_obj.stat_ttest_annova == 'ANNOVA':
                    _data['ttest'] = False
                    _data['annova'] = True
                _data['ttest_annova_value'] = self.course_file_obj.stat_ttest_annova_value
                _data['ttest_annova_sig'] = self.course_file_obj.stat_ttest_annova_sig
                _data['analysis'] = self.course_file_obj.teacher_analysis
                _data['histogram_file'] = self.course_file_obj.stat_histogram
                _data['id'] = self.course_file_obj.course_file_id
                _data['time'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                self.statistics_tools.generate_course_docx_report(_data, self.course_file_obj.course_file_id,
                                                                  filename)
                self.course_file_obj.report_file.save(
                    'course_report_' + str(self.course_file_obj.course_name) + '.docx',
                    File(open(filename, 'rb')))
                self.course_file_obj.save()
                return True
            except Exception as e:
                print('Error ' + str(e))
                return False

    def extractGrades(self):
        composed_grades = {}
        fused_grades = {}
        fused_grades['mids'] = []
        fused_grades['finals'] = []
        fused_grades['totals'] = []

        try:
            for _grades_report in self.grades_files_objs:
                workbook = xl.open_workbook(_grades_report.grades_file.path, on_demand=True)
                worksheet = workbook.sheet_by_index(0)

                try:
                    ____tmp = worksheet.cell_value(6, 5)
                except IndexError:
                    ____tmp = ''

                section_code = int(worksheet.cell_value(4, 1))
                location_name = worksheet.cell_value(0, 1)

                self.sections.append(section_code)
                if location_name in self.campuses:
                    pass
                else:
                    self.campuses.append(location_name)

                composed_grades[section_code] = {}
                composed_grades[section_code]['mids'] = []
                composed_grades[section_code]['finals'] = []
                composed_grades[section_code]['totals'] = []

                if section_code == '':
                    raise Exception('Unable to read the section from the excel file !!!')

                __line = 7
                if ____tmp == '':  # grades without mids
                    while True:
                        try:
                            __student = worksheet.cell_value(__line, 0)
                            if worksheet.cell_value(__line, 2) != '':
                                composed_grades[section_code]['finals'].append(
                                    float(worksheet.cell_value(__line, 2)))
                                fused_grades['finals'].append(float(worksheet.cell_value(__line, 2)))
                            if worksheet.cell_value(__line, 3) != '':
                                composed_grades[section_code]['totals'].append(
                                    float(worksheet.cell_value(__line, 3)))
                                fused_grades['totals'].append(float(worksheet.cell_value(__line, 3)))
                            __line += 1
                        except IndexError:
                            break
                else:
                    while True:
                        try:
                            __student = worksheet.cell_value(__line, 0)
                            if worksheet.cell_value(__line, 2) != '':
                                composed_grades[section_code]['mids'].append(
                                    float(worksheet.cell_value(__line, 2)))
                                fused_grades['mids'].append(float(worksheet.cell_value(__line, 2)))
                            if worksheet.cell_value(__line, 3) != '':
                                composed_grades[section_code]['finals'].append(
                                    float(worksheet.cell_value(__line, 3)))
                                fused_grades['finals'].append(float(worksheet.cell_value(__line, 3)))
                            if worksheet.cell_value(__line, 4) != '':
                                composed_grades[section_code]['totals'].append(
                                    float(worksheet.cell_value(__line, 4).replace('.', ',')))
                                fused_grades['totals'].append(float(worksheet.cell_value(__line, 4)))
                            __line += 1
                        except IndexError:
                            break

            self.dataloaded = True
        except Exception as e:
            self.errors.append(e.__str__())
            print(e.__str__())

        self.info.append('The grade Excel file was well loaded.')
        # print('The grade Excel file was well loaded.')

        return fused_grades, composed_grades

    def compute_statistics(self):
        _statistics = {}
        # compute the ttest-Annova values
        if len(self.composed_grades.keys()) == 2:
            # TTEST
            _statistics['TTEST'] = True
            _statistics['ANNOVA'] = False
            list_values = [v for v in self.composed_grades.values()]
            res = scipy.stats.ttest_ind(list_values[0]['totals'], list_values[1]['totals'])

            __ttest_annova_value = float("{0:.4f}".format(res.statistic))
            __ttest_annova_sig = float("{0:.4f}".format(res.pvalue))
            _statistics['ttest_annova_value'] = float("{0:.4f}".format(__ttest_annova_value))
            _statistics['ttest_annova_sig'] = float("{0:.4f}".format(__ttest_annova_sig))
        else:
            # ANNOVA
            _statistics['ANNOVA'] = True
            _statistics['TTEST'] = False
            __ttest_annova_value, __ttest_annova_sig = scipy.stats.f_oneway(*
                                                                            [self.composed_grades[val]['totals']
                                                                             for val in self.composed_grades.keys()])

            _statistics['ttest_annova_value'] = float("{0:.4f}".format(__ttest_annova_value))
            _statistics['ttest_annova_sig'] = float("{0:.4f}".format(__ttest_annova_sig))

        _statistics['mean'] = self.statistics_tools.statistics_mean(self.fused_grades['totals'])
        _statistics['std'] = self.statistics_tools.statistics_std_deviation(self.fused_grades['totals'])
        _statistics['skewness'] = self.statistics_tools.statistics_skewness(self.fused_grades['totals'])
        _statistics['correlation_value'] = self.statistics_tools.statistics_pearsonr_correlation_value(
            self.fused_grades['mids'],
            self.fused_grades['finals'])
        _statistics['correlation_sig'] = self.statistics_tools.statistics_pearsonr_correlation_sig(
            self.fused_grades['mids'],
            self.fused_grades['finals'])
        _statistics['min'] = self.statistics_tools.statistics_min(self.fused_grades['totals'])
        _statistics['max'] = self.statistics_tools.statistics_max(self.fused_grades['totals'])
        _statistics['analysis'] = self.statistics_tools.generate_analysis(_statistics)
        tempfile = os.path.join(Measurement_FS.TMP.value, 'histogram_course_' + str(self.course_name) + '.png')
        os.makedirs(os.path.dirname(tempfile), exist_ok=True)
        if self.statistics_tools.statistics_generate_histogram_section(self.fused_grades['totals'], self.course_name,
                                                                       tempfile):
            _statistics['stat_histogram'] = tempfile
        else:
            _statistics['stat_histogram'] = ''
        self.statisrtics_is_done = True
        return _statistics

    def create_Update_Course_report(self):

        if self.statisrtics_is_done:
            try:
                _course_file = CourseFile.objects.get(course_name=self.course_name, semester=self.semester)
            except CourseFile.DoesNotExist:
                _course_file = CourseFile()
                _course_file.report_state = ReportState.CREATED.value

            _tmp = ''
            for _sec in self.sections:
                if _tmp != '':
                    _tmp += ', '
                _tmp += str(_sec)
            _course_file.section_codes = _tmp

            _tmp = ''
            for _campuses in self.campuses:
                _tmp += str(_campuses) + ' \n '
            _course_file.campus_name = _tmp

            _course_file.course_name = self.course_name
            _course_file.stat_mean = self.statistics['mean']
            _course_file.stat_std = self.statistics['std']
            _course_file.stat_skewness = self.statistics['skewness']
            _course_file.stat_min = self.statistics['min']
            _course_file.stat_max = self.statistics['max']
            _course_file.stat_correlation_value = self.statistics['correlation_value']
            _course_file.stat_correlation_sig = self.statistics['correlation_sig']

            if self.statistics['TTEST'] == True:
                _course_file.stat_ttest_annova = 'TTEST'
            else:
                _course_file.stat_ttest_annova = 'ANNOVA'

            _course_file.stat_ttest_annova_value = self.statistics['ttest_annova_value']
            _course_file.stat_ttest_annova_sig = self.statistics['ttest_annova_sig']

            _course_file.stat_analysis = self.statistics['analysis']

            _course_file.stat_histogram.save('histogram_course_' + str(self.course_name) + '.png',
                                             File(open(self.statistics['stat_histogram'], 'rb')))

            _course_file.teacher = self.user
            _course_file.semester = self.semester
            _course_file.course_department = self.department

            _course_file.save()

            return _course_file

        else:
            return None

    def getStatistics(self):
        if self.statisrtics_is_done:
            return self.statistics
        return None


class MEASUREMENT_Common():

    def __init__(self):
        pass

    def statistics_mean(self, _data):
        return float("{0:.4f}".format(statistics.mean(_data)))

    def statistics_std_deviation(self, _data):
        try:
            return float("{0:.4f}".format(statistics.stdev(_data)))
        except:
            return 0

    def statistics_skewness(selfself, _data):
        return float("{0:.4f}".format(skew(_data, bias=False)))

    def statistics_pearsonr_correlation_value(self, _data1, _data2):
        try:
            return float("{0:.4f}".format(pearsonr(_data1, _data2)[0]))
        except ValueError:
            return 'None'

    def statistics_pearsonr_correlation_sig(self, _data1, _data2):
        try:
            return float("{0:.4f}".format(pearsonr(_data1, _data2)[1]))
        except ValueError:
            return 'None'

    def statistics_min(selfself, _data):
        return min(_data)

    def statistics_max(selfself, _data):
        return max(_data)

    def generate_analysis(self, _data):
        _mean = _data['mean']
        __analysis = []
        if _mean > 90:
            __analysis.append('The Grades Mean is High')
        if _mean < 60:
            __analysis.append('The Grades Mean is Low')
        if 60 <= _mean <= 90:
            __analysis.append('The Grades Mean is Normal')

        _std = _data['std']
        if _std < 5:
            __analysis.append('The spread of grades is Low --> the grades are very close')
        if _std > 15:
            __analysis.append('The spread of grades is  High --> the grades are very far')
        if 15 > _std > 5:
            __analysis.append('The spread of grades is  correct')

        _skewness = _data['skewness']
        if _skewness >= 0:
            __analysis.append('The skewness is positive --> Most of grades are less than the mean')
        else:
            __analysis.append('The skewness is negative --> Most of grades are more than the mean')

        _correlation = _data['correlation_sig']
        try:
            if _correlation == 'None':
                pass
            else:
                if _correlation >= 0.05:
                    __analysis.append(
                        'The correlation sig. is greater or equal to 0.05 --> There is no correlation between Mids and Finals')
                else:
                    __analysis.append(
                        'The correlation sig. is less than 0.05 --> There is a good correlation between Mids and '
                        'Finals')
        except TypeError:
            pass

        try:
            _ttest_annova_sig = _data['ttest_annova_sig']
            if _ttest_annova_sig >= 0.05:
                __analysis.append(
                    'The section results are very close')
            else:
                __analysis.append('There are difference in section results')
        except:
            pass

        _str = ''
        for _part in __analysis:
            _str += _part + '. '
            _str += '\n'

        return _str

    def statistics_generate_histogram_section(self, _data, __section, filename):
        isDone = False
        try:
            sem.acquire()
            # plot the histogram

            a = np.array(_data)
            # Fit a normal distribution to the data:
            mu, std = norm.fit(a)
            number = a.size

            # Plot the histogram.
            plt.hist(a, bins=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], density=True, color='#607c8e',
                     edgecolor='black',
                     rwidth=0.8)
            # Plot the PDF.
            x = np.linspace(0, 100, 100)
            p = norm.pdf(x, mu, std)
            plt.plot(x, p, 'k', linewidth=3)
            title = 'Section = ' + str(__section) + ',  Number of Students=' + str(number)
            plt.title(title)
            plt.savefig(filename)
            plt.close()
            isDone = True
        except Exception as e:
            print('-----' + e)
        finally:
            sem.release()
        return isDone

    def statistics_generate_histogram_course(self, _data, __course_name, filename):
        isDone = False
        try:
            sem.acquire()
            # plot the histogram

            a = np.array(_data)
            # Fit a normal distribution to the data:
            mu, std = norm.fit(a)
            number = a.size

            # Plot the histogram.
            plt.hist(a, bins=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], density=True, color='#607c8e',
                     edgecolor='black',
                     rwidth=0.8)
            # Plot the PDF.
            x = np.linspace(0, 100, 100)
            p = norm.pdf(x, mu, std)
            plt.plot(x, p, 'k', linewidth=3)
            title = "Course = %s,  Number of Students = %d" % (__course_name, number)
            plt.title(title)
            plt.savefig(filename)
            plt.close()
            isDone = True
        finally:
            sem.release()
        return isDone

    def generate_section_docx_report(self, _data, _doc_id, filename):
        if _data is None:
            return None
        else:
            try:
                _template_section_report = os.path.join('media/' + Measurement_FS.TEMPLATES.value,
                                                        'section_report_template.docx')
                tpl = DocxTemplate(_template_section_report)

                context = {
                    'histogram': InlineImage(tpl, _data['histogram_file'], width=Inches(3), height=Inches(3)),
                    'time': datetime.datetime.now().strftime("%y-%m-%d, %H:%M:%S"),
                    'id': str(_doc_id),
                }
                context = {**_data, **context}
                tpl.render(context)
                tpl.save(filename)
            except Exception as e:
                print("Error in DOCx Generation -----")
                print(str(e))
                print(str(e.with_traceback()))
                print(str(e.__cause__))
        return filename

    def generate_low_high_images(self, _data, low_file, high_file):
        try:
            sem.acquire()

            # Choose the height of the bars
            height = _data['low_means'].values()

            # Choose the names of the bars
            bars = []

            for __ll in _data['low_means'].keys():
                reshaped_text = arabic_reshaper.reshape(__ll)
                bars.append(get_display(reshaped_text))
            y_pos = np.arange(len(bars))
            # Create bars
            plt.bar(y_pos, height)
            # Rotation of the bars names
            plt.xticks(y_pos, bars, rotation=90)
            # Custom the subplot layout
            plt.subplots_adjust(bottom=0.4, top=0.99)
            plt.savefig(low_file)
            plt.close()
        finally:
            sem.release()

        try:
            sem.acquire()

            # Choose the height of the bars
            height = _data['high_means'].values()

            # Choose the names of the bars
            bars = []
            for __ll in _data['high_means'].keys():
                reshaped_text = arabic_reshaper.reshape(__ll)
                bars.append(get_display(reshaped_text))
            y_pos = np.arange(len(bars))

            # Create bars
            plt.bar(y_pos, height)

            # Rotation of the bars names
            plt.xticks(y_pos, bars, rotation=90)

            # Custom the subplot layout
            plt.subplots_adjust(bottom=0.4, top=0.99)
            plt.savefig(high_file)
            plt.close()
        finally:
            sem.release()

        return low_file, high_file

    def generate_course_docx_report(self, _data, _doc_id, filename):
        if _data is None:
            return None
        else:
            try:
                _template_course_report = os.path.join('media/' + Measurement_FS.TEMPLATES.value,
                                                       'course_report_template.docx')
                tpl = DocxTemplate(_template_course_report)

                context = {
                    'histogram': InlineImage(tpl, _data['histogram_file'], width=Inches(3), height=Inches(3)),
                    'time': datetime.datetime.now().strftime("%y-%m-%d, %H:%M:%S"),
                    'id': str(_doc_id),
                }
                context = {**_data, **context}
                tpl.render(context)
                tpl.save(filename)
            except Exception as e:
                print("Error in DOCx Generation -----")
                print(str(e))
                print(str(e.with_traceback()))
                print(str(e.__cause__))
        return filename

    def generate_department_docx_report(self, _data, _doc_id, filename):
        if _data is None:
            return None
        else:
            __template_department_report = os.path.join('media/' + Measurement_FS.TEMPLATES.value,
                                                        'department_report_template.docx')

            # Generate the histogram file
            temp1 = tempfile.NamedTemporaryFile(prefix="measurement_histogram_", suffix=".png")
            temp2 = tempfile.NamedTemporaryFile(prefix="measurement_histogram_", suffix=".png")

            self.generate_low_high_images(_data, temp1, temp2)

            tpl = DocxTemplate(__template_department_report)

            context = {
                'low_image': InlineImage(tpl, temp1, width=Inches(3), height=Inches(3)),
                'high_image': InlineImage(tpl, temp2, width=Inches(3), height=Inches(3)),
                'time': datetime.datetime.now().strftime("%y-%m-%d, %H:%M:%S"),
                'id': str(_doc_id),
            }
            context = {**_data, **context}
            tpl.render(context)
            tpl.save(filename)
            temp1.close()
            temp2.close()
        return filename


class SectionReportDocList:

    def __init__(self, _semester):
        self.semester = _semester

    def generateReport(self):
        pass

import pandas as pd
import os


class GradesFileReader:

    def __init__(self, filename):
        self.filename = filename
        self.data = {}

        self.done = 0
        self.msgs = []

    def read(self):
        '''
        This method reads the content of the grades file and fill the data property that contains the extracted information
        '''

        if os.path.exists(self.filename) and os.path.isfile(self.filename):
            __data = pd.read_excel(self.filename, header=None)
            df = pd.DataFrame(__data)

            try:
                if df.iat[0, 0] == 'المقر':
                    self.data['campus'] = df.iat[0, 1]
                else:
                    self.done = -1
                    self.msgs.append('An error is found in the campus information.')

                if df.iat[1, 0] == 'الدرجة':
                    self.data['level'] = df.iat[1, 1]
                else:
                    self.done = -1
                    self.msgs.append('An error is found in the educational level information.')

                if df.iat[2, 0] == 'اسم المقرر':
                    self.data['course'] = df.iat[2, 1]
                else:
                    self.done = -1
                    self.msgs.append('An error is found in the course name.')

                if df.iat[3, 0] == 'النشاط':
                    self.data['activity'] = df.iat[3, 1]
                else:
                    self.done = -1
                    self.msgs.append('An error is found in the activity information.')

                if df.iat[4, 0] == 'الشعبة':
                    self.data['section'] = df.iat[4, 1]
                else:
                    self.done = -1
                    self.msgs.append('An error is found in the section information.')

                if df.iat[6, 0] == 'رقم الطالب' and df.iat[6, 1] == 'اسم الطالب' and df.iat[6, 2] == 'فصلي (50%)' and \
                        df.iat[6, 3] == 'نهائي (50%)' and \
                        df.iat[6, 4] == 'الدرجة' and df.iat[6, 5] == 'التقدير':
                    grades = []
                    for index in range(7, len(df)):
                        tmp = {}



                        tmp['student_id'] = int(df.iat[index, 0])
                        tmp['student_name'] = df.iat[index, 1]
                        tmp['mids'] = float(df.iat[index, 2])
                        tmp['finals'] = float(df.iat[index, 3])
                        tmp['totals'] = float(df.iat[index, 4])
                        tmp['grade'] = df.iat[index, 5]
                        grades.append(tmp)
                    self.data['grades'] = grades
                    if self.done != -1:
                        self.done = 1
                else:
                    self.done = -1
                    self.msgs.append('An error is found in the grades information.')
            except IndexError:
                self.done = -1
                self.msgs.append('An error is found in the file format.')
            except ValueError:
                self.done = -1
                self.msgs.append(
                    'An error is found in the file format (some data should be numeric, but found strings !).')
        else:
            self.done = -1
            self.msgs.append('The file does not exist or is a folder.')

        print(self.data)
        print(self.done)
        print(self.msgs)


if __name__ == "__main__":
    tool = GradesFileReader(r'/home/mzarka/grades.xls')
    tool.read()

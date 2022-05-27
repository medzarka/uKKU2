from enum import Enum, unique


@unique
class Measurement_FS(Enum):
    TMP = 'measurement/tmp/'
    REPORTS = 'measurement/reports/'
    TEMPLATES = 'measurement/templates/'
    GRADES = 'measurement/grades/'
    HISTOGRAM = 'measurement/histograms/'

class Quality_FS(Enum):
    TMP = 'quality/tmp/'
    REPORTS = 'quality/reports/'
    TEMPLATES = 'quality/templates/'
from enum import Enum, unique


@unique
class Document_FS(Enum):
    TMP = 'Documents/tmp/'
    docs = 'Documents/docs/'

#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

KB = 1000
MB = KB * 1000
GB = MB * 1000
TB = GB * 1000


def convert_size_to_kb(size_in_bytes):
    if size_in_bytes < 1:
        return 0
    return float(size_in_bytes) / KB


def convert_size_to_mb(size_in_bytes):
    if size_in_bytes < 1:
        return 0
    return float(size_in_bytes) / MB


def convert_size_to_gb(size_in_bytes):
    if size_in_bytes < 1:
        return 0
    return float(size_in_bytes) / GB

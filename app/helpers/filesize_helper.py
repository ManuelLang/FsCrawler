#  Copyright (c) 2023. Manuel LANG
#  Software under GNU AGPLv3 licence

KB = 1000
MB = KB * 1000
GB = MB * 1000
TB = GB * 1000


def convert_size_to_kb(size_in_bytes: int):
    if size_in_bytes < 1:
        return 0
    return round(float(size_in_bytes) / KB, 2)


def convert_size_to_mb(size_in_bytes: int):
    if size_in_bytes < 1:
        return 0
    return round(float(size_in_bytes) / MB, 2)


def convert_size_to_gb(size_in_bytes: int):
    if size_in_bytes < 1:
        return 0
    return round(float(size_in_bytes) / GB, 2)


def format_file_size(size_in_bytes: int) -> str:
    if size_in_bytes < KB:
        return f"{size_in_bytes} o"
    elif size_in_bytes < MB:
        res = float(size_in_bytes) / KB
        return f"{res:.3f} Ko"
    if size_in_bytes < GB:
        res = float(size_in_bytes) / MB
        return f"{res:.3f} Mo"
    if size_in_bytes < TB:
        res = float(size_in_bytes) / GB
        return f"{res:.3f} Go"
    res = float(size_in_bytes) / TB
    return f"{res:.3f} To"





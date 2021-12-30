import datetime
from os import path


def extract_filename(url):
    fragment_removed = url.split("#")[0]  # keep to left of first #
    query_string_removed = fragment_removed.split("?")[0]
    scheme_removed = query_string_removed.split("://")[-1].split(":")[-1]
    if scheme_removed.find("/") == -1:
        return ""
    return path.basename(scheme_removed)


def time_str_to_object(time_str):
    return datetime.datetime.strptime(time_str, '%H:%M').time() if time_str else None


def time_object_to_str(time, pattern='%H:%M'):
    return time.strftime(pattern) if time else ''

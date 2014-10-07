# Convert between CSV strings and python-equivalent JSON types
from decimal import Decimal

from jsonlines.errors import ParseFailure

def has_value(s):
    """
    return True if this CSV string is not an empty cell
    """
    return bool(unicode(s).strip())


def decode(s, strict=False):
    """
    Return the python-equivalent object for a JSON values stored
    as a string in a CSV or spreadsheet.

    :param s: unicode CSV string
    :param strict: True to raise ParseFailure on values not supported
        by strict JSON parser

    :returns: a single JSON value: unicode, decimal, None, True, False
        or {}, and when not strict float('inf'), -float('inf') or float('nan')
    """
    s = unicode(s).strip()
    if s == u'null':
        return None
    if s == u'true':
        return True
    if s == u'false':
        return False
    if s == u'{}':
        return {}
    if s == u'NaN':
        if strict:
            raise ParseFailure('Strict JSON does not allow NaN values')
        return float('nan')
    if s == u'Infinity':
        if strict:
            raise ParseFailure('Strict JSON does not allow Infinity values')
        return float('inf')
    if s == u'-Infinity':
        if strict:
            raise ParseFailuer('Strict JSON does not allow -Infinity values')
        return -float('inf')


def decode_list(s, list_delimiter, strict=False):
    """
    Return the python-equivalent list of objects for a JSON values
    stored as a string in a CSV or spreadsheet.

    :param s: unicode CSV string
    :param list_delimiter: unicode string used to separate
        values stored as a list within this column
    :param strict: True to raise ParseFailure on values not supported
        by strict JSON parser

    :returns: a list containing 0 or more JSON values
    """
    s = unicode(s).strip()

    if s == list_delimiter:
        return []

    return [decode(part, strict) for part in s.split(list_delimiter)]

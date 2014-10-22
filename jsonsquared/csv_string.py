# Convert between CSV strings and python-equivalent JSON types
from __future__ import unicode_literals

from decimal import Decimal
import re

from jsonsquared.errors import ParseFailure


JSON_STRING_RE = r'"(?:[^"\\]|\\["\\/bfnrt]|\\u[0-9a-fA-F]{4})*"$'
JSON_STRING_PARTIAL_RE = JSON_STRING_RE[:-2]
JSON_NUMBER_RE = r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][-+]?\d+)?$'

DOUBLE_QUOTES = '"\N{LEFT DOUBLE QUOTATION MARK}\N{RIGHT DOUBLE QUOTATION MARK}'

def has_value(s):
    """
    return True if this CSV string is not an empty cell
    """
    return bool(unicode(s).strip())


def decode(s, allow_nan=False):
    """
    Return the python-equivalent object for a JSON value stored
    as a string in a CSV or spreadsheet.

    :param s: unicode CSV string
    :param allow_nan: True to allow IEEE float +/-inf and NaN

    :returns: a single JSON value: unicode, decimal, None, True, False
        or {}, and when allow_nan float('inf'), -float('inf') or float('nan')

    :raises: ParseError on invalid JSON string-formatted input,
        ValueError on empty/whitespace-only string passed
    """
    s = unicode(s).rstrip()
    first_len = len(s)
    s = s.lstrip()
    left_stripped = len(s) - first_len

    if not s:
        raise ValueError('Expecting a value, not an empty string')

    if s == 'null':
        return None
    if s == 'true':
        return True
    if s == 'false':
        return False
    if s == '{}':
        return {}

    if re.match(JSON_NUMBER_RE, s):
        # keep all the digits
        return Decimal(s)

    if len(s) < 2 or s[0] not in DOUBLE_QUOTES or s[-1] not in DOUBLE_QUOTES:
        # Normal string
        return s

    inner = s[1:-1]
    if inner[:2].rstrip() == '\\':
        # Extended JSON
        e = inner[2:].strip()
        if e == 'NaN':
            if not allow_nan:
                raise ParseFailure(
                    'Strict JSON parsing does not allow NaN values')
            return float('nan')
        if e == 'Infinity':
            if not allow_nan:
                raise ParseFailure(
                    'Strict JSON parsing does not allow Infinity values')
            return float('inf')
        if e == '-Infinity':
            if not allow_nan:
                raise ParseFailure(
                    'Strict JSON parsing does not allow -Infinity values')
            return -float('inf')
        raise ParseFailure(
            'Extended JSON not recognised: {0}. Allowed values are '
            '"NaN", "Infinity" and "-Infinity"'.format(json.dumps(e)))

    # straight quotes for JSON parsing
    s = '"' + inner + '"'
    if re.match(JSON_STRING_RE, s):
        return json.loads(s)

    # build a human-friendly error message
    m = re.match(JSON_STRING_PARTIAL_RE, s)
    bad_index = m.end() + left_stripped
    bad_part = s[bad_index:bad_index + 11]
    if len(bad_part) > 10:
        bad_part = bad_part[:10] + '...'
    raise ParseFailure(
        'JSON String parsing failed at position {0}: {1}'.format(
            bad_index, json.dumps(bad_part)))



def decode_list(s, list_delimiter, allow_nan=False):
    """
    Return the python-equivalent list of objects for a JSON values
    stored as a string in a CSV or spreadsheet.

    :param s: unicode CSV string
    :param list_delimiter: unicode string used to separate
        values stored as a list within this column
    :param allow_nan: True to allow IEEE float +/-inf and NaN

    :returns: list of 0+ JSON values

    :raises: ParseError on invalid JSON string-formatted input
    """
    s = unicode(s)

    if s.strip() == list_delimiter:
        return []

    elements = s.split(list_delimiter)
    if len(elements) > 1 and not has_value(elements[-1]):
        del elements[-1]

    errors = []
    out = []
    for i, e in enumerate(elements):
        try:
            out.append(decode(e, allow_nan))
        except ParseError as err:
            errors.append((i, err))

    if errors:
        pass

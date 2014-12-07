# Convert between CSV strings and python-equivalent JSON types
from __future__ import unicode_literals

from decimal import Decimal
import re

try:
    import simplejson as json
except ImportError:
    import json

from jsonsquared.errors import ParseFailure, JSONSquaredError


ERROR_SNIPPET_LENGTH = 10

CONTROL_CHARACTERS = ''.join(unichr(x) for x in range(32))
JSON_STRING_PLAIN_RE = r'[^"\\' + CONTROL_CHARACTERS + r']'
JSON_STRING_ESCAPES_RE = r'\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4})'
LENIENT_PARTS_RE = r'(?:\\[^\S\n]*\n|\r|\n|")' # Quoted string extension
QUOTED_STRING_RE = (
    r'"(?:' + JSON_STRING_PLAIN_RE +
    r'|' + JSON_STRING_ESCAPES_RE +
    r'|' + LENIENT_PARTS_RE + r')*"$')
QUOTED_STRING_NEXT_LENIENT_PART_RE = (
    r'(?P<strict>(?:' + JSON_STRING_PLAIN_RE +
    r'|' + JSON_STRING_ESCAPES_RE +
    r')*)(?P<lenient>' + LENIENT_PARTS_RE + r')')
QUOTED_STRING_PARTIAL_RE = QUOTED_STRING_RE.rstrip(r'"$')

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
    :param allow_nan: True to allow IEEE floating point +/-inf and NaN

    :returns: a single JSON value: unicode, Decimal, None, True, False
        or {}; when allow_nan is True Decimal values may include values
        'Infinity', '-Infinity' and 'NaN'.

    :raises: ParseError on invalid Quoted string-formatted input,
        ValueError on empty/whitespace-only string passed
    """
    original_s = s
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
    if s == '[]':
        return []

    if re.match(JSON_NUMBER_RE, s):
        # keep all the digits
        return Decimal(s)

    if len(s) < 2 or s[0] not in DOUBLE_QUOTES or s[-1] not in DOUBLE_QUOTES:
        # Normal string
        return s

    inner = s[1:-1]
    if inner[:2].rstrip() == '\\':
        # IEEE floats
        e = inner[2:].strip()
        if e == 'NaN':
            if not allow_nan:
                raise ParseFailure(
                    'Strict JSON parsing does not allow NaN values', 0, e)
            return Decimal('NaN')
        if e == 'Infinity':
            if not allow_nan:
                raise ParseFailure(
                    'Strict JSON parsing does not allow Infinity values', 0, e)
            return Decimal('Infinity')
        if e == '-Infinity':
            if not allow_nan:
                raise ParseFailure(
                    'Strict JSON parsing does not allow -Infinity values', 0, e)
            return Decimal('-Infinity')
        raise ParseFailure(
            'IEEE float not recognised. Allowed values are '
            '"NaN", "Infinity" and "-Infinity"', 0, inner)

    # straight quotes for JSON parsing
    s = '"' + inner + '"'
    if re.match(QUOTED_STRING_RE, s):
        s = '"' + _expand_inner_quoted_string_extensions(inner) + '"'
        if str is bytes:
            # XXX: encoding because json in python <2.7.8 returns separate
            # surrogate pairs when passed a unicode object including
            # escaped surrogates
            s = s.encode('utf-8')
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            raise JSONSquaredError(
                'csv_string.decode generated invalid JSON', original_s, s)

    # build a human-friendly error message
    m = re.match(QUOTED_STRING_PARTIAL_RE, s)
    bad_index = m.end() + left_stripped
    bad_part = s[:-1][bad_index:bad_index + ERROR_SNIPPET_LENGTH + 1]
    if len(bad_part) > ERROR_SNIPPET_LENGTH:
        bad_part = bad_part[:ERROR_SNIPPET_LENGTH] + '...'
    raise ParseFailure(
        'Quoted string parsing failed', bad_index, bad_part)


def _expand_inner_quoted_string_extensions(s):
    """
    implementation of our json strings lenient extensions:
    1. remove backslash-prefixed real-newlines
    2. replace real newlines with backslash-n
    3. remove real carriage returns
    4. backslash-escape unescaped double-quotes
    """
    out = []
    m = None
    for m in re.finditer(QUOTED_STRING_NEXT_LENIENT_PART_RE, s):
        out.append(m.group('strict'))
        group = m.group('lenient')
        if group == '\n':
            out.append(r'\n')
        elif group == '"':
            out.append(r'\"')
    if m is None:
        return s
    out.append(s[m.end():])
    return ''.join(out)



def decode_list(s, list_delimiter, allow_nan=False):
    """
    Return the python-equivalent list of objects for JSON values
    stored as a string in a CSV or spreadsheet.

    :param s: unicode CSV string
    :param list_delimiter: unicode string used to separate
        values stored as a list within this column
    :param allow_nan: True to allow IEEE float +/-inf and NaN

    :returns: list of 1 or more JSON values

    :raises: ParseFailure on invalid JSON string-formatted input
    """
    s = unicode(s)

    elements = s.split(list_delimiter)

    preparse = []
    errors = []
    out = []

    # emit doubled list_delimiters into list before parsing
    q = iter(elements)
    while True:
        try:
            e = next(q)
        except StopIteration:
            break
        if e:
            preparse.append(e)
            continue
        try:
            e2 = next(q)
        except StopIteration:
            break
        if preparse:
            preparse[-1] = preparse[-1] + list_delimiter + e2
        else:
            preparse.append(list_delimiter + e2)

    for e in preparse:
        # skip empty elements instead of raising errors
        if not has_value(e):
            continue
        val = None
        try:
            val = decode(e)
        except ParseFailure as e:
            errors.append(e.args)




    for i, e in enumerate(elements):
        if e != '' and out:
            out[-1] = out[-1] + list_delimiter
        try:
            out.append(decode(e, allow_nan))
        except ParseError as err:
            errors.append((i, err))

    if errors:
        pass

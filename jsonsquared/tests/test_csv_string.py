from __future__ import unicode_literals

from jsonsquared.csv_string import has_value, decode, decode_list
from jsonsquared.errors import ParseFailure

try:
    import unittest2 as unittest
except ImportError:
    import unittest
from decimal import Decimal

class TestHasValue(unittest.TestCase):
    def test_has_value(self):
        self.assertTrue(has_value('wat'))

    def test_empty_string(self):
        self.assertFalse(has_value(''))

    def test_whitespace_string(self):
        self.assertFalse(has_value(' \t\r\n'))


class TestDecode(unittest.TestCase):
    def test_no_value_raises_valueerror(self):
        self.assertRaises(ValueError, decode, '  ')

    def test_null(self):
        self.assertEquals(decode(' null\n'), None)

    def test_true(self):
        self.assertEquals(decode('true '), True)

    def test_false(self):
        self.assertEquals(decode('\N{NO-BREAK SPACE} false'), False)

    def test_empty_object(self):
        self.assertEquals(decode(' {} '), {})

    def test_null_is_case_sensitive(self):
        self.assertEquals(decode('Null'), 'Null')

    def test_true_is_case_sensitive(self):
        self.assertEquals(decode('TRUE'), 'TRUE')

    def test_false_is_case_sensitive(self):
        self.assertEquals(decode('falsE'), 'falsE')

    def test_empty_object_no_internal_whitespace_allowed(self):
        self.assertEquals(decode(' { } '), '{ }')

    def test_natural_number(self):
        self.assertEquals(decode('42'), Decimal('42'))

    def test_negative_integer(self):
        self.assertEquals(decode('-9'), Decimal('-9'))

    def test_decimal_number(self):
        self.assertEquals(decode('0.0009'), Decimal('0.0009'))

    def test_exponent_number(self):
        self.assertEquals(decode('-1.96e-20'), Decimal('-1.96e-20'))

    def test_plenty_of_precision(self):
        self.assertEquals(unicode(decode('6.' + '0' * 100 + '42')),
            '6.' + '0' * 100 + '42')

    def test_string_single_quote(self):
        self.assertEquals(decode('"'), '"')

    def test_string_unicode(self):
        self.assertEquals(decode('\N{SNOWMAN}'), '\N{SNOWMAN}')

    def test_json_string_unicode(self):
        self.assertEquals(decode('"\N{SNOWMAN}"'), '\N{SNOWMAN}')

    def test_json_string_high_unicode(self):
        self.assertEquals(decode('"\U0001f4a9"'), '\U0001f4a9')

    def test_json_string_escaped_surrogate_pairs(self):
        self.assertEquals(decode(r'"\ud83d\udca9"'), '\U0001f4a9')

    def test_json_string_significant_whitespace(self):
        self.assertEquals(decode('"  hello "'), '  hello ')

    def test_json_string_right_quotes(self):
        self.assertEquals(decode('\N{RIGHT DOUBLE QUOTATION MARK} o "'), ' o ')

    def test_json_string_left_quotes(self):
        self.assertEquals(decode('" y \N{LEFT DOUBLE QUOTATION MARK}'), ' y ')

    def test_json_string_auto_escape_double_quotes(self):
        self.assertEquals(decode('"""'),'"')

    def test_json_string_escaped_backslash(self):
        self.assertEquals(decode(r'"\\"'), '\\')

    def test_json_string_allow_escaped_double_quotes(self):
        self.assertEquals(decode(r'"\""'), '"')

    def test_json_string_auto_escape_double_quotes_leading_backslash(self):
        self.assertEquals(decode(r'"\\""'), r'\"')

    def test_json_string_with_embedded_newline(self):
        self.assertEquals(decode('"hello\nworld"'), 'hello\nworld')

    def test_json_string_with_escaped_embedded_newline(self):
        self.assertEquals(decode('"hello\\\nworld"'), 'helloworld')

    def test_json_string_with_escaped_embedded_whitespace_newline(self):
        self.assertEquals(decode('"hello\\ \r\nworld"'), 'helloworld')

    def test_json_string_with_escaped_embedded_whitespace_newlines(self):
        self.assertEquals(decode('"hello\\ \r\n\nworld"'), 'hello\nworld')


class TestDecodeList(object):
    def test_empty_list(self):
        self.assertEquals(decode_list('x', 'x'), [])

    def test_one_element(self):
        self.assertEquals(decode_list('0', 'x'), [0])

    def test_trailing_delimiter(self):
        self.assertEquals(decode_list('0,', ','), [0])

    def test_delimiter_prefix(self):
        self.assertEquals(decode_list('xx2', 'x'), ['x2'])

    def test_delimiter_suffix(self):
        self.assertEquals(decode_list('2xx', 'x'), ['2x'])

    def test_delimiter_ambiguous(self):
        self.assertEquals(decode_list('2xxxxx3', 'x'), ['2xx', 3])

    def test_delimiter_disambiguate(self):
        self.assertEquals(decode_list('2xx x xx3', 'x'), ['2x', 'x3'])


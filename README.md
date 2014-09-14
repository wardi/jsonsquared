# JSON Squared

JSON Squared is a library for lossless conversion between JSON or
[JSON Lines](http://jsonlines.org) and CSV or Excel format in a sparse
style convenient for editing.

Many libraries exist for converting between JSON and CSV. This one
makes the assumption that your JSON contains many objects with a
similar structure. For each value that is a list of objects it
is assumed that the objects in the list share a similar structure.

Features:

* Compact table format even with multiple nested lists of objects
* JSON types are maintained
* Not limited to data files that fit in RAM, can stream data or use
  disk space temporarily for conversions
* Simple, clear error reporting for parsing errors

Current limitations:

* Topmost JSON element must be a list containing only JSON objects
  (for JSON Lines each topmost element must be a JSON object)
* Lists directly containing other lists are not supported

## Design choices

### Simple types

CSV allows only string values. JSON Squared maintains JSON types
by reserving the following string values:

CSV value | JSON value
--- | ---
`null` | `null`
`true` | `true`
`false` | `false`

When these exact lowercase strings appear as the complete value
of a CSV cell they will be converted to the corresponding special
JSON value.

Any value that can be [parsed as a JSON number](docs/number.gif)
will be represented as a number in JSON. e.g.:

CSV value | JSON value
--- | ---
`42` | 42
`0.0009` | 0.0009
`-1.96e-20` | -1.96e-20

JSON Squared will leave numbers exactly as
they appear and not introduce any underflow, overflow or rounding
errors during conversions. Beware that spreadsheet programs and
programs that produce or parse JSON may introduce these errors.

Values that have double-quotes (straight `"` left `“` or right `”`)
as their first and last characters (matching type not necessary) will
have their first and last characters removed, then be parsed as
JSON strings. Straight double quotes (`"`) and backslashes (`\`) must be
backslash-escaped. e.g:

CSV value | JSON value
--- | ---
`"what's that?"` | `"what's that?"`
`“she said \"hi\".“` | `"she said \"hi\"."`

This format is typically used only for:

* the empty string: `""`
* strings with unprintable control codes, e.g.: `"\u0003\u0000"`
* strings that would otherwise be interpreted as numbers or special
  values, e.g.: `"true"` or `"19.99"`
to represent: empty strings

Strings containing newlines are not escaped by default, but escaping
may be forced on the command line.

Any other value is treated as a string value. Leading and trailing
whitespace is maintained.

CSV value | JSON value
--- | ---
`what's that?` | `"what's that?"`
`True` | `"True"`
`0x8000` | `"0x8000"`


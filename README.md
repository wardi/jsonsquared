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

* `null`
* `true`
* `false`

When these exact lowercase strings appear as the complete value
of a CSV cell they will be converted to their corresponding special
JSON values.

Any string that can be parsed as a JSON number will be represented
as a number in JSON.

![JSON number parsing diagram](docs/number.gif)


JSON Squared will leave numbers exactly as
they appear and not introduce any underflow, overflow or rounding
errors during conversions. Beware that spreadsheet programs and
programs that produce or parse JSON may introduce these errors.

Values that have double-quotes (straight `"` left `“` or right `”`)
as their first and last characters (matching type not necessary) will
have their first and last characters removed, then be treated as strings.
Quotes appearing within the strings are not processed specially, so
don't need to be escaped in any way.

Any other value is treated as a string value. Leading and trailing
whitespace is maintained.

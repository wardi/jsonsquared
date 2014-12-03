<!-- vim: set et sw=2 sts=2 spell spelllang=en_us: -->

# [JSON]²

## Gory details

Filling in the details not covered by the [readme](README.md)

### Reserved values

[readme](README.md#reserved-values)

When these strings appear as the value
of a CSV cell, ignoring whitespace on the left and right,
they will be converted to their corresponding special
JSON value.

All letters must be lower-case. No
characters are permitted between the braces or brackets
for empty objects and lists.


### Numbers

[readme](README.md#numbers)

Commas, whitespace and other separators are not permitted anywhere
within these numbers, or the value will be treated as a
[normal string](#normal-strings).

JSON Squared will maintain the precision of the numbers given
and not introduce any underflow, overflow or rounding
errors during conversions.


### JSON strings

[readme](README.md#json-strings)

Surrounding quotes will be converted to straight quotes before
parsing. Left and right quotes will not be replaced within the string
body.

Straight double-quotes in the string body that are not already escaped
by a backslash will be escaped automatically before parsing.

Real carriage return characters (U+000D) will be removed. Next, real
newline characters (U+000A) preceded by a backslash will be removed
(as well as whitespace between the backslash and newline).
Finally any remaining real newline characters will be
replaced with the newline escape sequence (`\n`) before parsing.

JSON strings with invalid backslash escape sequences or control
characters can cause parsing errors that will prevent a CSV document
from being converted to JSON.

All errors are collected and reported with a clear reference to the
position of the invalid characters:

greeting |
--- |
"just \saying hi" |

```
Error parsing cell A2: JSON String parsing failed at position 5: "\saying hi"
```


## Extras


### Extended JSON

JSON is occasionally extended to cover IEEE floating point special values.
These special values are represented as JSON strings with a
backslash-whitespace (`\ `) prefix. This prefix is otherwise an invalid
part of a JSON string.

a | b | c
--- | --- | ---
"\ NaN" | "\ Infinity" | "\ -Infinity"

```js
[
  {
    "a": NaN,
    "b": Infinity,
    "c": -Infinity
  }
]
```



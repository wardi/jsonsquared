<!-- vim: set sw=2 sts=2 spell spelllang=en_us: -->

# [JSON]²

JSON Squared is a library for lossless conversion between
[JSON](http://json.org) or
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
* JSON files with repeated keys or with keys in a special order are
  an abomination and will not be supported, even though we could

Limitations:

* Topmost JSON element must be a list containing only JSON objects
  (for JSON Lines each topmost element must be a JSON object)
* JSON objects must have at least one simple value, e.g.
  a string or number


## Design choices

### Reserved values

CSV allows only string values. JSON Squared maintains JSON types
by reserving the following string values:

CSV value | JSON value
--- | ---
`null` | `null`
`true` | `true`
`false` | `false`
`[]` | `[]`
`{}` | `{}`

When these exact lowercase strings appear as the value
of a CSV cell, ignoring whitespace on the left and right,
they will be converted to the corresponding special
JSON value.

### Numbers

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

### JSON strings

Values that have double-quotesas their first and last characters,
ignoring whitespace on the left and right, will
have the quotes and surrounding whitespace removed, then be
[parsed as JSON strings](docs/string.gif)
. Double-quotes may be straight `"` left `“` or right `”`
for Excel-friendliness, matching quotes is not required.

Within the JSON string straight double quotes (`"`) and backslashes
(`\`) must be backslash-escaped, e.g.:

CSV value | JSON value
--- | ---
`   "what's that?"` | `"what's that?"`
`“she said \"hi\".“` | `"she said \"hi\"."`

This format is typically used only for:

* the empty string: `""`
* strings with unprintable control codes, e.g.: `"\u0003\u0000"`
* strings that would otherwise be interpreted as numbers or special
  values, e.g.: `"true"` or `"19.99"`

Strings containing newlines are not escaped by default, but escaping
may be forced on the command line.

### Normal strings

Any other value is treated as a string value. Leading and trailing
whitespace is maintained.

CSV value | JSON value
--- | ---
`   what's that?` | `"   what's that?"`
`True` | `"True"`
`0x8000` | `"0x8000"`
`I said "sure."` | `"I said \"sure.\""`

### Lists of simple types

Lists of the simple types above may be represented
collapsed into a single cell by choosing a delimiter, or vertically
in neighboring rows. For lists a `[𝑥]` suffix is added to
the column heading, where `𝑥` is the delimiter chosen, e.g. delimited:

name | rooms[,] | colors[ ]
--- | --- | ---
Tim | 19,14,18 | green blue

Or vertically:

name | rooms[,] | colors[ ]
--- | --- | ---
Tim | 19, | green
 | 14 | blue
 | 18 |

Or a mixture:

name | rooms[,] | colors[ ]
--- | --- | ---
Tim | 19 | green
 | 14,18, | blue


convert identically to:

```json
[
  {
    "name": "Tim",
    "rooms": [19, 14, 18],
    "colors": ["green", "blue"]
  }
]
```

A single trailing delimiter may be included in each cell and will be
ignored, as shown the example above.

JSON strings are supported within
lists, but lists are first separated by their delimiter ignoring
any quoting implied by JSON strings, so don't use a delimiter that may
appear in a JSON string or you may not get the result you expect, e.g.:

name | says[,]
--- | ---
Ryan | "hi, there", "friend"

converts to:

```json
[
  {
    "name": "Ryan",
    "says": ["\"hi", " there\"", "friend"]
  }
]
```

Empty lists are represented as a single delimiter with
nothing in front, e.g.:

name | pets[,]
--- | ---
May | ,

converts to:

```json
[
  {
    "name": "May",
    "pets": []
  }
]
```


### Nested objects

JSON objects nested directly inside other objects are represented
by extra columns with the parent name and child name joined with a
period (`.`).  e.g.:

id | name.en | name.fr
--- | --- | ---
190007 | Franklin | Benjamin

becomes:

```json
[
  {
    "id": 190007,
    "name": {
      "en": "Franklin",
      "fr": "Benjamin"
    }
  }
]
```

### Lists of objects

Lists of JSON objects within other objects are represented
by extra columns with the parent name and child name joined with a
forward slash (`/`). e.g.:

address | residents/name | residents/age | cars/make | cars/colour
--- | --- | --- | --- | ---
12 oak ave. | sam | 43 | honda | gray
 | linda | 45 | |

becomes:

```json
[
  {
    "address": "12 oak ave.",
    "residents": [
      {"name": "sam", "age": 43},
      {"name": "linda", "age": 45}
    ],
    "cars": [
      {"make": "honda", "color": "gray"}
    ]
  }
]
```



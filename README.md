<!-- vim: set et sw=2 sts=2 spell spelllang=en_us: -->

# [JSON]²

JSON Squared is a (planned) library for lossless conversion between
[JSON](http://json.org) or
[JSON Lines](http://jsonlines.org) and CSV or Excel format in a sparse
style convenient for editing.

Many libraries exist for converting between JSON and CSV. This library
makes the assumption that your JSON contains many objects with a
similar structure. For each path (list of keys) to a list of objects it
is assumed that the objects in the lists share a similar structure.

Features:

* Compact table format even with multiple nested lists of objects
* JSON types are maintained
* Not limited to data files that fit in RAM, can stream data or use
  disk space temporarily for conversions
* Simple, clear error reporting for parsing errors

Limitations:

* JSON files with repeated keys or with keys in a special order are
  not supported

## Example

address | owners[,] | pets/name | pets/dob | pets/toys[,]
--- | --- | --- | --- | ---
12 Oak ave. | Tim | Fluffy | 2009 | pink elephant,green ball
 | | Beast | 2011 |
 | | Tiny | 2005 | orange platypus
199 Cliff ave. | June,James | Sophie | 2009 | knotted rope
 | | | | octopus-like thing
 | | | | piranha squeak toy
 | | Theo | 2009 |

Converts to:

```json
[
  {
    "address": "12 Oak ave.",
    "owners": ["Tim"],
    "pets": [
      { "name": "Fluffy", "dob": 2009, "toys": ["pink elephant", "green ball"] },
      { "name": "Beast", "dob": 2011 },
      { "name": "Tiny", "dob": 2005, "toys": ["orange platypus"] }
    ]
  },
  {
    "address": "199 Cliff ave.",
    "owners": ["June", "James"],
    "pets": [
      {
        "name": "Sophie",
        "dob": 2009,
        "toys": ["knotted rope", "octopus-like thing", "piranha squeak toy"]
      },
      { "name": "Theo", "dob": 2009 }
    ]
  }
]
```


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

Values that have double-quotes as their first and last characters,
ignoring whitespace on the left and right, will
have the quotes and surrounding whitespace removed, then be
[parsed as JSON strings](docs/string.gif).
Double-quotes may be straight `"` left `“` or right `”`
for Excel-friendliness, matching quotes is not required.

Within the JSON string straight double quotes (`"`) and backslashes
(`\`) must be backslash-escaped, e.g.:

CSV value | JSON value
--- | ---
`   "what's that?"` | `"what's that?"`
`“she said \"hi\".“` | `"she said \"hi\"."`

This format is typically used only for:

* the empty string: `""`
* strings with unprintable control codes, e.g.: `"\u0003\u0000"`
* strings that would otherwise be interpreted as numbers or special
  values, e.g.: `"true"` or `"19.99"`

Strings containing newlines are not escaped by default, but escaping
may be forced on the command line.

### Normal strings

Any other value is treated as a normal string value. Leading and trailing
whitespace is maintained.

CSV value | JSON value
--- | ---
`   what's that?` | `"   what's that?"`
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

vertical:

name | rooms[,] | colors[ ]
--- | --- | ---
Tim | 19, | green
 | 14 | blue
 | 18 |

or a mix of delimited and vertical:

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
ignored, as shown the examples above.

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
period (`.`), e.g.:

id | name.en | name.fr
--- | --- | ---
190007 | Franklin | Benjamin

```json
[
  {
    "id": 190007,
    "name": {"en": "Franklin", "fr": "Benjamin"}
  }
]
```

### Lists of objects

Lists of JSON objects within other objects are represented
by extra columns with the parent name and child name joined with a
forward slash (`/`), e.g.:

address | residents/name | residents/age | cars/make | cars/colour
--- | --- | --- | --- | ---
12 oak ave. | sam | 43 | honda | gray
 | linda | 45 | |

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

### Lists of lists

Lists can be nested in column headings by replacing the list markers
with forward slashes for all but the last level, e.g:

name | data[,] | data/[,] | data//[,]
--- | --- | --- | ---
my grid | 1 | 2,3 | 4
 | 5 | 6,7 |

```json
[
  {
    "name": "my grid",
    "data": [1, [2, 3, [4]], 5, [6, 7]]
  }
]
```

Empty lists are used to break up nested lists without adding
elements in between. Choose a delimiter more visible than a comma
for lists containing only lists to help make nesting clearer, e.g.:

, e.g.:

name | data[>] | data/[>] | data//[,]
--- | --- | --- | ---
grid2 | > | > | 1,2
 | | > | 3,4

```json
[
  {
    "name": "my grid",
    "data": [[[1, 2], [3, 4]]]
  }
]
```

## Edge cases

### Unusual keys

Keys that are empty strings or strings containing periods (`.`),
double quotes (`"`), forward slashes (`/`) or
opening brackets (`[`) can given as JSON strings, e.g.:

odd."" | "\u005B\u002C]" | "\u002F"/"\u002E\u002E"
--- | --- | ---
1 | 2 | 3

```json
[
  {
    "odd": {"": 1},
    "[,]": 2,
    "/": [
      {"..": 3}
    ]
  }
]
```

You must use the Unicode-escaped versions of the special characters
or your keys will be interpreted incorrectly. For reference:

Original | JSON Escaped
--- | ---
`.` | `\u002E`
`"` | `\u0022`
`/` | `\u002F`
`[` | `\u005B`


### Top of JSON is not a list

We use period (`.`) as a prefix in the column heading to indicate keys of a
top-level object, e.g.:

.title | .things[,]
--- | ---
spelling | cat
 | dog
 | ball

```json
{
  "title": "spelling",
  "things": ["cat", "dog", "ball"]
}
```

For simple objects we use a period as a column heading by itself, e.g:

. |
--- |
pretty boring JSON |

```json
"pretty boring JSON"
```

### Mixed value types

Simple types, objects and other lists may all appear as values for the
same keys in different objects by having the same column name specified
different ways. Only one column may be given a value for each object.

id | foo | foo[,] | foo.bar | foo/baz
--- | --- | --- | --- | ---
1 | 42 | | |
2 | | 7,6 | |
3 | | | "carbon rod" |
4 | | | | true

```json
[
  {"id": 1, "foo": 42},
  {"id": 2, "foo": [7, 6]},
  {"id": 3, "foo": {"bar": "carbon rod"}},
  {"id": 4, "foo": [{"baz": true}]}
]
```

Within a list we can switch between objects types on different rows while
we build the list.

collection | things[,] | things/id | things/name
--- | --- | --- | ---
heap | 19,{} | |
 | | c=64 |
 | | 1541 | disk drive
 | false | |

```json
[
  {
    "collection": "heap",
    "things": [
      19,
      {},
      {"id": "c=64"},
      {"id": 1541, "name": "disk drive"},
      false
    ]
  }
]
```

This pattern is necessary to represent empty objects 

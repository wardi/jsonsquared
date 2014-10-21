<!-- vim: set et sw=2 sts=2 spell spelllang=en_us: -->

# [JSON]²

JSON Squared is a (planned) library for lossless conversion between
[JSON](http://json.org) and CSV or Excel format in a sparse
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
12 Oak ave. | Tim K. | Fluffy | 2009 | pink elephant, green ball
 | | Beast | 2011 |
 | | Tiny | 2005 | orange platypus
199 Cliff ave. | June S. | Sophie | 2009 | knotted rope
 | James N. | | | octopus-like thing
 | | | | piranha squeak toy
 | | Theo | 2009 |

Converts to:

```json
[
  {
    "address": "12 Oak ave.",
    "owners": ["Tim K."],
    "pets": [
      { "name": "Fluffy", "dob": 2009, "toys": ["pink elephant", "green ball"] },
      { "name": "Beast", "dob": 2011 },
      { "name": "Tiny", "dob": 2005, "toys": ["orange platypus"] }
    ]
  },
  {
    "address": "199 Cliff ave.",
    "owners": ["June S.", "James N."],
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


## Simple types

### Reserved values

CSV allows only string values. JSON Squared maintains JSON types
in CSV files by reserving the following string values:

CSV string | JSON value
--- | ---
`null` | `null`
`true` | `true`
`false` | `false`
`{}` | `{}`

When these exact strings appear as the value
of a CSV cell, ignoring whitespace on the left and right,
they will be converted to their corresponding special
JSON value.

### Numbers

Any CSV string that can be [parsed as a JSON number](docs/number.gif)
will be represented as a number in JSON.

CSV string | JSON value
--- | ---
`42` | 42
`0.0009` | 0.0009
`-1.96e-20` | -1.96e-20

JSON Squared will leave numbers exactly as
they appear and not introduce any underflow, overflow or rounding
errors during conversions.

### JSON strings

CSV strings that have double-quotes as their first and last characters,
ignoring whitespace on the left and right, will
have the quotes and surrounding whitespace removed then be
[parsed as JSON strings](docs/string.gif).
Double-quotes may be straight (`"`) left (`“`) or right (`”`)
for Excel-friendliness. Matching left and right quotes is not required.

Within the JSON string straight double quotes (`"`) and backslashes
(`\`) must be backslash-escaped.

CSV string | JSON value
--- | ---
`   "what's that?"` | `"what's that?"`
`“she said \"hi\".“` | `"she said \"hi\"."`

JSON strings are typically used for:

* the empty string: `""`
* strings with unprintable control codes, e.g.: `"\u0003\u0000"`
* strings that have significant leading or trailing whitespace
* strings that would otherwise be interpreted as numbers or special
  values, e.g.: `"true"` or `"19.99"`

### Extended JSON

JSON is occasionally extended to cover IEEE floating point special values.
These special values are represented as JSON strings with a
backslash-whitespace (`\ `) prefix. This prefix is otherwise an invalid
part of a JSON string.

CSV string | JSON value
--- | ---
`"\ NaN"` | `NaN` \*
`"\ Infinity"` | `Infinity` \*
`"\ -Infinity"` | `-Infinity` \*

\* raises error if the "allow NaN" option is not enabled

### Normal strings

Any other value is treated as a normal string value. Leading and trailing
whitespace is removed.

CSV string | JSON value
--- | ---
`   what's that?` | `"what's that?"`
`True` | `"True"`
`0x8000` | `"0x8000"`
`I said "sure."` | `"I said \"sure.\""`

## Compound types

### Lists of simple types

Lists of simple types may be represented
collapsed into a single cell by choosing a delimiter, or vertically
in neighboring rows. For lists a `[𝑥]` suffix is added to
the column heading, where `𝑥` is the delimiter chosen.

name | rooms[,] | colors[ ]
--- | --- | ---
Tim | 19, 14, 18 | green blue

```json
[
  {
    "name": "Tim",
    "rooms": [19, 14, 18],
    "colors": ["green", "blue"]
  }
]
```

Lists continue to neighboring rows if those row do not contain
an element that forces the start of a new object. In this example
a value in the "name" column would start a new object.

A single trailing delimiter may be included in each cell and will
be ignored. These examples are equivalent to the one above:

name | rooms[,] | colors[ ]
--- | --- | ---
Tim | 19, | green
 | 14 | blue
 | 18 |

name | rooms[,] | colors[ ]
--- | --- | ---
Tim | 19 | green
 | 14, 18, | blue

JSON strings are supported within lists, but they may not contain
the delimiter used by the list. Lists are split on their delimiter
before string values are parsed.

name | says[,]
--- | ---
Ryan | "hi, there", "friend"

```json
[
  {
    "name": "Ryan",
    "says": ["\"hi", "there\"", "friend"]
  }
]
```

Empty lists in JSON Squared are written as a single delimiter with
nothing in front.

name | pets[,]
--- | ---
May | ,

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
period (`.`).

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
forward slash (`/`).

address | residents/name | residents/age | cars/make | cars/color
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
with forward slashes for all but the last level.

name | data[,] | data/[,] | data//[,]
--- | --- | --- | ---
nested | 1 | 2, 3 | 4
 | 5 | 6, 7 |

```json
[
  {
    "name": "nested",
    "data": [1, [2, 3, [4]], 5, [6, 7]]
  }
]
```

Empty lists are used to break up nested lists without adding
elements in between. Choose a delimiter more visible than a comma
for lists containing only lists to help make nesting clearer.

name | data[>] | data/[>] | data//[,]
--- | --- | --- | ---
lumpy | > | > | 1, 2
 | | > | 3, 4

```json
[
  {
    "name": "lumpy",
    "data": [[[1, 2], [3, 4]]]
  }
]
```

This works for lists of lists at the top-level too.

[>] | /[,]
--- | ---
> | 1, 0, 0, 0
> | 0, 1, 0, 0
> | 0, 0, 1, -1
> | 0, 0, 0, 1

```json
[
  [1, 0, 0, 0],
  [0, 1, 0, 0],
  [0, 0, 1, -1],
  [0, 0, 0, 1]
]
```

### Explicit object boundaries

When an object in a list contains no simple-typed values we may need to
mark where that object ends and where the next object in the same list
begins. We use the same method as when we have nested lists: insert an
empty list one level above.

very[-] | very/listy[,]
--- | ---
  | do, re, mi
  | fa
- | so, la
  | ti, do

```json
[
  {
    "very":[
      {"listy": ["do", "re", "mi", "fa"]},
      {"listy": ["so", "la", "ti", "do"]}
    ]
  }
]
```

This works with the top-level list too. Adding an empty list at the
first element isn't required but can look more consistent.

[>] | listy[,]
--- | ---
> | how, are, things
> | fine
  | thanks

```json
[
  {"listy": ["how", "are", "things"]},
  {"listy": ["fine", "thanks"]}
]
```

## Edge cases

### Top-level objects

We use period (`.`) as a prefix in the column heading to indicate keys of a
top-level object.

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

### Top-level simple types

For simple types we use a period as a column heading by itself.

. |
--- |
pretty boring JSON |

```json
"pretty boring JSON"
```


### Unusual keys

Keys that are empty strings or strings containing periods (`.`),
double quotes (`"`), forward slashes (`/`) or
opening brackets (`[`) can given as JSON strings.

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
we build the list. This is the only way to include empty objects (`{}`)
in lists along with non-empty objects.

collection | things[,] | things/id | things/name
--- | --- | --- | ---
heap | 19,{} | C=64 |
 | | 1541 | disk drive
 | false | |

```json
[
  {
    "collection": "heap",
    "things": [
      19,
      {},
      {"id": "C=64"},
      {"id": 1541, "name": "disk drive"},
      false
    ]
  }
]
```


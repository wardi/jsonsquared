<!-- vim: set et sw=2 sts=2 spell spelllang=en_us: -->

# [JSON]²

JSON Squared is a tool being developed for lossless conversion between
[JSON](http://json.org) and CSV or Excel format in a sparse
style convenient for editing.

Many libraries exist for converting between JSON and CSV. This library
assumes that the JSON file contains many objects with a
similar structure and for each path (list of keys) it
assumes that the objects in the list share a similar structure.

Features:

* Compact table format even with multiple nested lists of objects
* JSON types are maintained
* Not limited to data files that fit in RAM, can stream data
  (CSV to JSON) use two-pass method (JSON files to CSV) or use
  intermediate temp file (JSON stream to CSV)
* Simple, clear error reporting for parsing errors

Limitations:

* Repeating keys within the same JSON object is not supported,
  e.g. `{"data": 1, "data": 42, "data": 83}`
* JSON objects in files produced will always have their keys in
  the same order, e.g. `[{"a": 1, "b": 2}, {"a": 2, "b": 1}, ...]`

## 0. Example

address | owners[] | pets/name | pets/joined | pets/toys[,]
--- | --- | --- | --- | ---
12 Oak ave. | Tim K. | Fluffy | 2009 | pink elephant, green ball
 | | Beast | 2011 |
 | | Tiny | 2005 | orange platypus
199 Cliff ave. | June S. | Sophie | 2009 | rope, octopus, piranha
 | James N. | Theo | 2009 |

Converts to:

```json
[
  {
    "address": "12 Oak ave.",
    "owners": ["Tim K."],
    "pets": [
      { "name": "Fluffy", "joined": 2009, "toys": ["pink elephant", "green ball"] },
      { "name": "Beast", "joined": 2011 },
      { "name": "Tiny", "joined": 2005, "toys": ["orange platypus"] }
    ]
  },
  {
    "address": "199 Cliff ave.",
    "owners": ["June S.", "James N."],
    "pets": [
      { "name": "Sophie", "joined": 2009, "toys": ["rope", "octopus", "piranha"] },
      { "name": "Theo", "joined": 2009 }
    ]
  }
]
```


## 1. Simple types

### Reserved values

CSV allows only string values. JSON Squared maintains JSON types
in CSV files by reserving the following string values:

a | b | c | d | e
--- | --- | --- | --- | ---
null | true | false | {} | []

```json
[
  {
    "a": null,
    "b": true,
    "c": false,
    "d": {},
    "e": []
  }
]
```

[details...](details.md#reserved-values)

### Numbers

Any cell value that can be [parsed as a JSON number](docs/number.gif)
will be represented as a number in JSON.

a | b | c
--- | --- | ---
42 | 0.0009 | -1.96e-20

```json
[
  {
    "a": 42,
    "b": 0.0009,
    "c": -1.96e-20
  }
]
```

[details...](details.md#numbers)


### JSON strings

Cell values that have double-quotes as their first and last characters,
ignoring whitespace on the left and right, will be
[parsed as JSON strings](docs/string.gif)
([with some allowances](details.md#json-strings)).

a | b | c | d
--- | --- | --- | ---
"   what's that?" | “she said "hi".“ | "two<br/>lines" | "one \ <br/>line"

```json
[
  {
    "a": "   what's that?",
    "b": "she said \"hi\".",
    "c": "two\nlines",
    "d": "one line"
  }
]
```

JSON strings are typically used for:

* the empty string: `""`
* strings with unprintable control codes, e.g.: `"\u0003\u0000"`
* strings that have significant leading or trailing whitespace
* strings that would otherwise be interpreted as numbers or special
  values, e.g.: `"true"` or `"19.99"`

[details...](details.md#json-strings)


### Normal strings

Any value that is not [reserved](#reserved-values),
[decimal](#numbers) or [surrounded by double-quotes](#json-strings)
is treated as a normal string value. Leading and trailing
whitespace is removed. There is no escaping required for any characters.

a | b | c | d | e
--- | --- | --- | --- | ---
      what's that? | True | 0x8000 | I said "sure." | c:\sys\net.txt

```json
[
  {
    "a": "what's that?",
    "b": "True",
    "c": "0x8000",
    "d": "I said \"sure\"",
    "e": "c:\\sys\\net.txt"
  }
]
```

## 2. Compound types

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
    "name": {
      "en": "Franklin",
      "fr": "Benjamin"
    }
  }
]
```

### Vertical lists

Create lists by adding brackets (`[]`) to a column heading.

List contents continue to from one row to the next, as long as
those rows aren't part of a new object. In this example
only a value in the "name" column would start a new object:

name | rooms[] | colors[]
--- | --- | ---
Tim | 19 | green
 | 14 | blue
 | 18 |

```json
[
  {
    "name": "Tim",
    "rooms": [19, 14, 18],
    "colors": ["green", "blue"]
  }
]
```

[details...](details.md#vertical-lists)


### Horizontal lists

Save space by combining short lists into fewer cells with horizontal
lists.  Include a delimiter between the brackets in the heading and
that delimiter will be used to split cells into multiple list elements.

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

Horizontal lists act as vertical lists as well, so you always have
room to add more list elements.

[details...](details.md#horizontal-lists)


### Lists of objects

Join a parent name with a child name with a forward slash (`/`)
in a column heading to create a list of objects.

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

[details...](details.md#lists-of-objects)


## 3. Edge cases

 * [Empty lists](details.md#empty-lists)
 * [Empty objects](details.md#empty-objects)
 * [Lists of lists](details.md#lists-of-lists)
 * [Explicit object boundaries](details.md#explicit-object-boundaries)
 * [Top-level objects](details.md#top-level-objects)
 * [Top-level simple types](details.md#top-level-simple-types)
 * [Unusual keys](details.md#unusual-keys)
 * [Mixed value types](details.md#mixed-value-types)
 * [IEEE floats](details.md#ieee-floats)


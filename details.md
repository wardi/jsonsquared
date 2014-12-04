<!-- vim: set et sw=2 sts=2 spell spelllang=en_us syntax=markdown: -->

# [JSON]²

## The gory details

Filling in the bits of JSON Squared not covered by the [readme](README.md).

### Reserved values

[back](README.md#reserved-values)

When these strings appear as the value
of a CSV cell, ignoring whitespace on the left and right,
they will be converted to their corresponding special
JSON value.

All letters must be lower-case. No
characters are permitted between the braces or brackets
for empty objects and lists.


### Numbers

[back](README.md#numbers)

Commas, whitespace and other separators are not permitted anywhere
within these numbers, or the value will be treated as a
[normal string](#normal-strings).

JSON Squared will maintain the precision of the numbers given
and not introduce any underflow, overflow or rounding
errors during conversions.


### Quoted strings

[back](README.md#quoted-strings)

* For Excel-smart-quote-friendliness the surrounding double-quotes
  may be straight (`"`) left (`“`) or right (`”`) quotes. Matching left
  and right quotes is not required.

  Surrounding quotes will be converted to straight quotes before
  parsing. Left and right quotes will not be replaced within the string
  body.

* Straight double-quotes (`"`) within the string body *do not* need to
  be escaped with a backslash. This
  means means that backslash (`\`) is
  the only character that needs escaping when converting a
  [normal string](#normal-strings) to a quoted string.

  Straight double-quotes in the string body that are not already escaped
  by a backslash will be escaped automatically before being parsed
  as a JSON string.

* Real newline characters may be included in the string body. Newlines
  for just for formatting in the spreadsheet may be backslash-escaped.

  Real carriage return characters (U+000D) will be removed. Next, real
  newline characters (U+000A) preceded by a backslash will be removed
  (as well as whitespace between the backslash and newline).
  Finally any remaining real newline characters will be
  replaced with the newline escape sequence (`\n`) before being
  parsed as a JSON string.

Quoted strings with control characters or a backslash escape sequence
invalid in a JSON string cause parsing errors that will prevent a
CSV document from being converted to JSON.

All errors are collected and reported with a clear reference to the
position of the invalid characters:

greeting |
--- |
"just \saying hi" |

```
Error parsing cell A2: Quoted String parsing failed at position 5: "\saying hi"
```

See also: [Extended JSON](#extended-json).


### Vertical lists

[back](README.md#vertical-lists)

Lists continue on to rows without a value in any simple-typed sibling
or parent column. A sibling or parent column shares the exact or a partial
prefix with the column of interest.

See also: [Empty lists](#empty-lists).

### Horizontal lists

[back](README.md#horizontal-lists)

Each list element is parsed as a simple type as though
it was in its own cell. Normal rules such as removing surrounding
whitespace apply.

Delimiters must be at least one character but may be multiple characters
to avoid conflicting with list element values.
Whitespace in delimiters is significant. A closing brace (`]`) may not
be used as any part of a delimiter.

To include the delimiter text as a value in a list (without replacing all
other delimiters in the column) use the complete delimiter twice with
no whitespace in between.

name | says[,]
--- | ---
Ryan | hi,, there, friend

```json
[
  {
    "name": "Ryan",
    "says": ["hi, there", "friend"]
  }
]
```

### Lists of objects

[back](README.md#lists-of-objects)

List elements are added by including values on following rows.
Values from sibling columns on the same row
are combined into single objects.



## Edge cases

### Empty lists

[back](README.md#3-edge-cases)

Empty lists in JSON Squared are written as simple types.

name | pets | pets[]
--- | --- | ---
May | [] |
Sam | | Rex

```json
[
  { "name": "May", "pets": [] },
  { "name": "Sam", "pets": ["Rex"] }
]
```


### Empty objects

[back](README.md#3-edge-cases)

Empty objects that appear in lists with normal objects must be included
as simple types.

messages[] | messages/text
--- | ---
 | hello
{} |
 | is there anyone there?
 | no, we're not here right now.

```json
[
  {
    "messages": [
      {"text": "hello"},
      {},
      {"text": "is there anyone there?"},
      {"text": "no we're not here right now"}
    ]
  }
]

```

### Lists of lists

[back](README.md#3-edge-cases)

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

Empty lists are used to break up nested lists when not adding
elements in between.

name | data[] | data/[] | data//[,]
--- | --- | --- | ---
lumpy | | | 1, 2
 | | [] | 3, 4

```json
[
  {
    "name": "lumpy",
    "data": [[[1, 2], [3, 4]]]
  }
]
```

This works for lists of lists at the top-level too.

[] | /[,]
--- | ---
[] | 1, 0, 0, 0
[] | 0, 1, 0, 0
[] | 0, 0, 1, -1
[] | 0, 0, 0, 1

```json
[
  [1, 0, 0, 0],
  [0, 1, 0, 0],
  [0, 0, 1, -1],
  [0, 0, 0, 1]
]
```


### Explicit object boundaries

[back](README.md#3-edge-cases)

When an object in a list contains no [simple-typed](#1-simple-types)
values use the nested list method to
mark where one object ends and where the next object in the same list
begins: insert an empty list one level above.

very/listy | very/listy[,]
--- | ---
 | do, re, mi
 | fa
[] | so, la
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

listy | listy[,]
--- | ---
[] | how, are, things
[] | fine
  | thanks

```json
[
  {"listy": ["how", "are", "things"]},
  {"listy": ["fine", "thanks"]}
]
```


### Top-level objects

[back](README.md#3-edge-cases)

Use period (`.`) as a prefix in the column heading to indicate keys of a
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

[back](README.md#3-edge-cases)

For simple types use a period as a column heading by itself.

. |
--- |
pretty boring JSON |

```json
"pretty boring JSON"
```


### Unusual keys

[back](README.md#3-edge-cases)

Keys that are empty strings or strings containing periods (`.`),
double quotes (`"`), forward slashes (`/`) or
opening brackets (`[`) may be written as [Quoted strings](quoted-strings).

odd."" | "\u005B]" | "\u002F"/"\u002E\u002E"
--- | --- | ---
1 | 2 | 3

```json
[
  {
    "odd": {"": 1},
    "[]": 2,
    "/": [
      {"..": 3}
    ]
  }
]
```

Use the Unicode-escaped versions of characters with a
special meaning in JSON Squared column names. For reference:

Original | JSON Escaped
--- | ---
`.` | `\u002E`
`"` | `\u0022`
`/` | `\u002F`
`[` | `\u005B`

List delimiters may not be written as Quoted strings.


### Mixed value types

[back](README.md#3-edge-cases)

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

Different objects types may appear in the same list.

collection | things[,] | things/id | things/name
--- | --- | --- | ---
heap | 19 | C=64 |
 | | 1541 | disk drive
 | false | |

```json
[
  {
    "collection": "heap",
    "things": [
      19,
      {"id": "C=64"},
      {"id": 1541, "name": "disk drive"},
      false
    ]
  }
]
```

### IEEE floats

[back](README.md#3-edge-cases)

Enable the 'allow_nan' option in JSON Squared to include support for
IEEE floating point special values.

These special values are represented as Quoted strings with a
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



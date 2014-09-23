"""Convert JSON to easily-editable CSV format "JSON Squared"

Usage:
  json2 [INPUT_JSON [OUTPUT_CSV]] [-L] [-z] [-e CSV_ENCODING]
        [-f FOLD_MAX] [-d DELIMITERS]

Options:
  -d --list-delimiters=DELIMITERS  string of characters to use when splitting
                                   lists within the same cell: the first one
                                   not found in the list text will be used
                                   [default: ,|;:/!-_]
  -e --encoding=CSV_ENCODING       text encoding for CSV file
  -f --fold-max=FOLD_MAX           fold lists onto next row before exceeding
                                   FOLD_MAX characters in the same cell
                                   [default: 20]
  -L --json-lines                  consume JSON Lines (newline-delimited JSON)
                                   instead of plain JSON
  -z --gzip                        gunzip input JSON file

See also
"""

from docopt import docopt

from jsonsquared.version import __version__

def parse_arguments():
    # docopt magic
    return docopt(__doc__, version=__version__)

def main():
    print parse_arguments()

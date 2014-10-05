"""JSON Squared command line interface

Usage:
  json2 csv [INPUT_JSON [OUTPUT_CSV]] [-L] [-z] [-e ENCODING] [-f FOLD_MAX]
            [-d DELIMITERS]
  json2 xls INPUT_JSON OUTPUT_XLS [-L] [-z] [-f FOLD_MAX] [-d DELIMITERS]
  json2 uncsv [INPUT_CSV [OUTPUT_JSON]] [-L | -i INDENT] [-z] [-e ENCODING]
  json2 unxls INPUT_XLS [OUTPUT_JSON] [-L | -i INDENT] [-z]
  json2 -h

Options:
  -d --list-delimiters=DELIMITERS  string of characters to use when splitting
                                   lists within the same cell: the first one
                                   not found in the list text will be used
                                   [default: ,|;:/!-+>_]
  -e --encoding=ENCODING           text encoding for CSV file
  -f --fold-max=FOLD_MAX           fold lists onto next row before exceeding
                                   FOLD_MAX characters in the same cell
                                   [default: 20]
  -h --help                        show this help text
  -i --indent=INDENT               pretty-print JSON using INDENT spaces
  -L --json-lines                  consume/produce JSON Lines (newline-delimited
                                   JSON) instead of plain JSON
  -z --gzip                        consume/produce gzipped JSON
"""

from docopt import docopt

from jsonsquared.version import __version__

def parse_arguments():
    # docopt magic
    return docopt(__doc__, version=__version__)

def main():
    print parse_arguments()

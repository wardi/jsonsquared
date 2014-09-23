"""Convert "JSON Squared" CSV format to JSON

Usage:
  unjson2 [INPUT_CSV [OUTPUT_JSON]] [-L | -i INDENT] [-z] [-e CSV_ENCODING]

Options:
  -e --encoding=CSV_ENCODING       text encoding for CSV file
  -i --indent=INDENT               pretty-print JSON using INDENT spaces
  -L --json-lines                  produce JSON Lines (newline-delimited JSON)
                                   instead of plain JSON
  -z --gzip                        gzip JSON output
"""

from docopt import docopt

from jsonsquared.version import __version__

def parse_arguments():
    # docopt magic
    return docopt(__doc__, version=__version__)

def main():
    print parse_arguments()

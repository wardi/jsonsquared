
class ParseFailure(Exception):
    def __init__(self, message, offset=None, column=None, row=None, text=None):
        self.message = message
        self.offset = offset
        self.column = column
        self.row = row
        self.text = text
        super(ParseFailure, self).__init__(
            self.message,
            self.offset,
            self.column,
            self.row,
            self.text)

class JSONSquaredError(Exception):
    pass

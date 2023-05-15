import re

class GameConsts:
    def __init__(self):
        self.DEFAULT_STRING_FORMAT = "utf-8"
        self.MESSAGE_LENGTH_HEADER_LENGTH = 128
        self.DEFAULT_PORT = 65432
        self.inputs_regex = re.compile("[^\w \-\_0-9]")
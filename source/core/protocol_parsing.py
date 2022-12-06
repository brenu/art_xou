import json
from source.core.game_consts import GameConsts

game_consts = GameConsts()

class ProtocolParsing:
    @staticmethod 
    def parse(data):
        message = json.dumps(data).encode(game_consts.DEFAULT_STRING_FORMAT)
        message_length = ("0"*(game_consts.MESSAGE_LENGTH_HEADER_LENGTH - len(str(len(message)))) + str(len(message))).encode(game_consts.DEFAULT_STRING_FORMAT)

        return message_length+message
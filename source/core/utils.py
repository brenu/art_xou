import socket
import platform

class Utils:
    @staticmethod
    def close_connection(connection: socket.socket):
        if platform.system() != "Windows":
            connection.shutdown(socket.SHUT_RDWR)
            connection.close()
        else:
            connection.close()
"""
    name : session.py
    
    purpose : all session related classes are inserted here.
    
    author : denjK
"""

import socket
import ssl
from abc import abstractmethod
from logger.logger import log, Level
from ssl_files import consts as ssl_file_consts

SSL_PROTOCOL = ssl.PROTOCOL_SSLv23


def create_ssl_socket(is_server, key_file=None, cert_file=None):
    """
    create an ssl socket (server or client) and returns it.
    :param bool is_server: is the socket a server or a client, if it is, key_file and cert_file is mandatory 
    :param key_file: the private key for the certificate
    :param cert_file: certificate for the server.
    :return SSLSocket: 
    """

    sock = socket.socket()
    ssl_sock = ssl.wrap_socket(sock, keyfile=key_file, certfile=cert_file, server_side=is_server,
                               cert_reqs=ssl.CERT_NONE, ssl_version=SSL_PROTOCOL)
    return ssl_sock


class SSLSocket(object):
    """ a basic implementation to an ssl socket"""

    SOCK_TIMEOUT = 15
    DEFAULT_BUFFER_LENGTH = 1024

    @abstractmethod
    def __init__(self, host, port):
        self._sock = None
        self._host = host
        self._port = port

    def send_data(self, data):
        self._sock.send(data)

    def recv_data(self, buffer_length=DEFAULT_BUFFER_LENGTH):
        return self.recv_data(buffer_length)

    @classmethod
    def create_ssl_socket(cls, sock):
        """
        create a new instance of cls as _sock is socket.
        :param socket.socket sock: a socket. 
        :return cls: an instance of the class.
        """
        host, port = sock.getsockname()
        ssl_sock = cls(host, port)
        ssl_sock._sock = sock
        return ssl_sock



class SSLClient(SSLSocket):
    """ implementation of SSLClient """

    SOCK_TIMEOUT = 15
    DEFAULT_BUFFER_LENGTH = 1024

    def __init__(self, host, port):
        super(SSLClient, self).__init__(host, port)
        self._sock = create_ssl_socket(False)


    def start_session(self):
        try:
            self._sock.connect((self._host, self._port))
            log("Successfully connected to server!", Level.INFO)
        except Exception as e:
            log("Exception occurred! - {exc}".format(exc=e), Level.FATAL)
            raise e

    def send_data(self, data):
        self._sock.send(data)

    def recv_data(self, buffer_length=DEFAULT_BUFFER_LENGTH):
        try:
            return self._sock.recv(buffer_length)
        except ssl.SSLError as ssl_error:
            log("Exception occurred when trying to receive data {exc}, returning empty string instead.".format(
                exc=ssl_error),
                Level.CRITICAL)


class SSLServer(SSLSocket):
    """ implementation of SSLServer """

    DEFAULT_BACKLOG = 5

    def __init__(self, host, port, key_file=ssl_file_consts.PRIVATE_KEY, cert_file=ssl_file_consts.SERVER_CERTIFICATE):
        self._sock = create_ssl_socket(True,
                                       key_file=key_file,
                                       cert_file=cert_file)
        self._host = host
        self._port = port
        self.init()
        super(SSLSocket, self).__init__()

    def init(self):
        """ initiation of starter command for the socket."""
        self._sock.listen(self.DEFAULT_BACKLOG)
        self._sock.bind((self._host, self._port))

    def accept(self):
        try:
            sock, (ip, port) = self._sock.accept()
            log("accepted {ip}:{port}".format(ip=ip, port=port), Level.INFO)
            return SSLClient.create_ssl_socket(sock)
        except ssl.SSLError as e:
            log("Exception occurred while accepting clients - {e}".format(e=e), Level.FATAL)







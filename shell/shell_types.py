from subprocess import Popen, PIPE
from time import sleep
from core_utils.logger import logger

class CmdCommunicator(object):
    _EOL = "\r\n"
    _SUFFIX_COMMAND = " 2>&1" + _EOL
    _EXPECTED_STRING = "CMD_PROMPT>"

    def __init__(self, cmd_location):
        self._process = Popen(cmd_location, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        sleep(2)
        self._process.stdin.write("prompt CMD_PROMPT$G" + self._SUFFIX_COMMAND)
        self.expect()

    def run(self, command, expected_string=_EXPECTED_STRING):
        self._process.stdin.write(command + self._SUFFIX_COMMAND)
        self._process.stdin.flush()
        data = self.expect(expected_string)
        refined_data = data[len(command) + len(self._SUFFIX_COMMAND) + 1:-1 * (len(expected_string) + len(self._EOL))]
        return CmdOutput(refined_data)

    def expect(self, expected_string=_EXPECTED_STRING):
        data = self._process.stdout.read(1)
        while expected_string not in data:
            next_data = self._process.stdout.read(1)
            data += next_data
        return data

    def close(self):
        self._process.kill()
        logger.log("successfully ended the process", logger.Level.INFO)

class CmdOutput(object):

    def __init__(self, text):
        self._text = text

    def __repr__(self):
        return self._text
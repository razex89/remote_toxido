from enum import Enum

class RemoteCommunicatorConsts(object):
    DEFAULT_TIMEOUT = 180
    IDENTIFIER = "0x1234567890"
    EOL = "\x03\x03\x03"
    SELF_SHUTDOWN_OUT = "SELF_SHUTDOWN"
    SUCCESS_CREATE_CMD_OUT = "SUCCESS_CREATE_CMD"
    SUCCESS_CLOSE_CMD_OUT = "SUCCESS_CLOSE_CMD"
    CMD_TEMPLATE_OUT = "OUTPUT {out}"
    COMMAND_PATTERN = "(?P<command>^.*)\x03\x03(?P<args>.*)?\x03\x03\x03"
    STD_TYPES = Enum("STD",zip(["INPUT", "OUTPUT", "ERROR"], range(3)))
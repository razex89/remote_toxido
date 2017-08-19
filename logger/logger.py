"""
    name : logger.py
    
    purpose : logger.
    
    author : denjK
"""

# IMPORTS
from enum import Enum
import sys
from colorama import Fore, init, Style

init()


# ENUM
class Level(Enum):
    INFO = 0
    WARNING = 1
    CRITICAL = 2
    FATAL = 3


# CONSTS
LOG_TEMPLATE = "{color}{type}{end_color}: {message}"
COLOR_DIC = {Level.INFO: Fore.CYAN, Level.WARNING: Fore.YELLOW, Level.FATAL: Fore.RED, Level.CRITICAL: Fore.GREEN}


def log(message, level):
    """
        Purpose: prints a message to the log (usually the screen)
    :param string message: the message to output.
    :param int level: (mostly comes as enum) the level of message (info , warning..)
    :return:
    """

    try:
        level = Level(level)
        print LOG_TEMPLATE.format(color=COLOR_DIC[level], type=level.name, end_color=Style.RESET_ALL, message=message)

    except ValueError:
        print "Level does not exist.. please take Level type from Level enum."
        sys.exit(1)
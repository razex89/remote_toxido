from shell_types import CmdCommunicator

def create_shell():
    cmd = CmdCommunicator(r"C:\windows\system32\cmd.exe")
    return cmd



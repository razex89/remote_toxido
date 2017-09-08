"""
    name: main.py
    
    purpose: running the program
    
    author: denjK

"""
import argparse
from communication import communication


def main():
    ip, port = argument_parser()
    init(ip, port)

def init(ip, port):
    conn = communication.RemoteCommunicator(ip, port)
    conn.connect()
    conn.loop_get_commands()


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('ip', type=str, help="ip_address")
    parser.add_argument('port', type=int, help="port")

    args = parser.parse_args()
    return args.ip, int(args.port)


if __name__ == "__main__":
    main()

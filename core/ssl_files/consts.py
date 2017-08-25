import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_CERTIFICATE = os.path.join(BASE_DIR, "server.crt")
PRIVATE_KEY = os.path.join(BASE_DIR, "server.key")
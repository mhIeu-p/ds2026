#!/usr/bin/env python3
# client.py
# Usage: python3 client.py <SERVER_IP> <PORT> <FILE_PATH>
# Example: python3 client.py 127.0.0.1 9000 test.txt

import socket
import struct
import argparse
import os
import sys

CHUNK_SIZE = 4096

def send_file(server_ip, port, file_path):
    if not os.path.isfile(file_path):
        print(f"[-] File not found: {file_path}")
        return

    filename = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)

    print(f"[+] Connecting to {server_ip}:{port}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, port))
        print("[+] Connected.")

        # 1) send filename length (4 bytes) + filename (utf-8)
        name_bytes = filename.encode('utf-8')
        s.sendall(struct.pack('>I', len(name_bytes)))
        s.sendall(name_bytes)

        # 2) send filesize (8 bytes)
        s.sendall(struct.pack('>Q', filesize))

        # 3) send file content in chunks
        sent = 0
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                s.sendall(chunk)
                sent += len(chunk)
                print(f"\r    Sent {sent}/{filesize} bytes", end='', flush=True)
        print("\n[+] File sent successfully.")

def main():
    parser = argparse.ArgumentParser(description="Simple TCP file client")
    parser.add_argument('server', help='Server IP or hostname')
    parser.add_argument('port', type=int, help='Server port')
    parser.add_argument('file', help='Path to file to send')
    args = parser.parse_args()
    send_file(args.server, args.port, args.file)

if __name__ == '__main__':
    main()

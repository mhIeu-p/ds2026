#!/usr/bin/env python3
# server.py
# Usage: python3 server.py [PORT]
# Example: python3 server.py 9000

import socket
import struct
import argparse
import os

CHUNK_SIZE = 4096

def recv_all(sock, n):
    """Receive exactly n bytes from sock, or raise EOFError."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            raise EOFError("Socket closed before we received expected bytes")
        data.extend(packet)
    return bytes(data)

def handle_client(conn, addr, out_dir):
    print(f"[+] Connection from {addr}")
    try:
        # 1) read filename length (4 bytes)
        raw = recv_all(conn, 4)
        (name_len,) = struct.unpack('>I', raw)

        # 2) read filename
        name_bytes = recv_all(conn, name_len)
        filename = name_bytes.decode('utf-8', errors='replace')
        safe_name = os.path.basename(filename)  # prevent path traversal
        out_path = os.path.join(out_dir, "received_" + safe_name)
        print(f"[+] Receiving file: {filename} -> saving as {out_path}")

        # 3) read filesize (8 bytes)
        raw = recv_all(conn, 8)
        (filesize,) = struct.unpack('>Q', raw)
        print(f"[+] Expected size: {filesize} bytes")

        # 4) read file content
        received = 0
        with open(out_path, 'wb') as f:
            while received < filesize:
                to_read = min(CHUNK_SIZE, filesize - received)
                chunk = conn.recv(to_read)
                if not chunk:
                    raise EOFError("Connection closed while receiving file")
                f.write(chunk)
                received += len(chunk)
                # progress print
                print(f"\r    Received {received}/{filesize} bytes", end='', flush=True)
        print("\n[+] File transfer complete.")
    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        conn.close()
        print("[+] Connection closed.\n")

def main():
    parser = argparse.ArgumentParser(description="Simple TCP file server")
    parser.add_argument('port', nargs='?', type=int, default=9000, help='Port to listen on (default 9000)')
    parser.add_argument('--out', '-o', default='.', help='Output directory (default current)')
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', args.port))
        s.listen(1)
        print(f"[+] Listening on 0.0.0.0:{args.port}")
        while True:
            conn, addr = s.accept()
            # For simplicity: handle one client at a time (blocking)
            handle_client(conn, addr, args.out)

if __name__ == '__main__':
    main()

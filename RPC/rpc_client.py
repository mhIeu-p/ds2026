from xmlrpc.client import ServerProxy, Binary
import argparse
import os
import sys


def send_file(server_url: str, file_path: str) -> None:
    if not os.path.isfile(file_path):
        print(f"[-] File not found: {file_path}")
        return

    filename = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)

    print(f"[+] Connecting to RPC server at {server_url}")
    proxy = ServerProxy(server_url, allow_none=True)

    try:
        pong = proxy.ping()
        print(f"[+] Server ping response: {pong}")
    except Exception as e:
        print(f"[-] Failed to ping server: {e}")
        return

    # Read file as bytes
    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except Exception as e:
        print(f"[-] Error reading file: {e}")
        return

    print(f"[+] Sending file '{filename}' ({filesize} bytes) via RPC...")
    try:
        # Wrap bytes in Binary for XML-RPC
        result = proxy.upload_file(filename, Binary(data))
        print(f"[+] Server response: {result}")
    except Exception as e:
        print(f"[-] RPC error: {e}")


def main():
    parser = argparse.ArgumentParser(description="RPC file transfer client")
    parser.add_argument("server_url",
                        help="Server URL, e.g. http://127.0.0.1:8000")
    parser.add_argument("file",
                        help="Path to file to send")
    args = parser.parse_args()

    send_file(args.server_url, args.file)


if __name__ == "__main__":
    main()

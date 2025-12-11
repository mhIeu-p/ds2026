from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.client import Binary
import argparse
import os


class RequestHandler(SimpleXMLRPCRequestHandler):
    # Restrict RPC path for safety
    rpc_paths = ("/RPC2",)


class FileTransferService:
    """
    Exposes RPC methods for file transfer.
    Client will upload a file as binary data.
    """

    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)

    def upload_file(self, filename: str, data: Binary) -> str:
        """
        Save received binary file to the output directory.

        :param filename: original filename from client
        :param data: xmlrpc.client.Binary object containing file bytes
        :return: status message
        """
        # Prevent path traversal, keep only the base name
        safe_name = os.path.basename(filename)
        out_path = os.path.join(self.out_dir, "received_" + safe_name)

        try:
            with open(out_path, "wb") as f:
                f.write(data.data)
            print(f"[+] Received file '{filename}' ({len(data.data)} bytes)")
            print(f"    Saved as: {out_path}")
            return f"OK: saved as {out_path}"
        except Exception as e:
            print(f"[-] Error while saving file: {e}")
            return f"ERROR: {e}"

    def ping(self) -> str:
        """Simple health check RPC."""
        return "pong"


def main():
    parser = argparse.ArgumentParser(description="RPC file transfer server")
    parser.add_argument("port", nargs="?", type=int, default=8000,
                        help="Port to listen on (default 8000)")
    parser.add_argument("--out", "-o", default=".",
                        help="Output directory for received files (default current)")
    args = parser.parse_args()

    service = FileTransferService(args.out)

    with SimpleXMLRPCServer(("0.0.0.0", args.port),
                            requestHandler=RequestHandler,
                            allow_none=True) as server:
        server.register_introspection_functions()
        server.register_instance(service)

        print(f"[+] RPC server listening on 0.0.0.0:{args.port}")
        print(f"[+] Output directory: {os.path.abspath(args.out)}")
        print("[+] Methods: upload_file(filename, data), ping()")

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[+] Server stopped.")


if __name__ == "__main__":
    main()

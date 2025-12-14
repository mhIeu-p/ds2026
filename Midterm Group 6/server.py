import socket
import threading

HOST = "0.0.0.0"
PORT = 9001

clients = {}  # username -> (conn, ip, p2p_port)
lock = threading.Lock()

def handle_client(conn, addr):
    username = None
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            parts = data.strip().split(" ", 2)
            cmd = parts[0]

            if cmd == "REGISTER":
                username = parts[1]
                p2p_port = parts[2]
                with lock:
                    clients[username] = (conn, addr[0], p2p_port)
                conn.sendall(b"OK\n")

            elif cmd == "LIST":
                with lock:
                    users = ",".join(clients.keys())
                conn.sendall(f"USERS {users}\n".encode())

            elif cmd == "GETADDR":
                target = parts[1]
                with lock:
                    if target in clients:
                        _, ip, port = clients[target]
                        conn.sendall(f"ADDR {ip} {port}\n".encode())
                    else:
                        conn.sendall(b"ERR\n")

            elif cmd == "MSG":
                target, msg = parts[1], parts[2]
                with lock:
                    if target in clients:
                        tconn, _, _ = clients[target]
                        tconn.sendall(f"FROM {username}: {msg}\n".encode())

            elif cmd == "QUIT":
                break
    finally:
        if username:
            with lock:
                clients.pop(username, None)
        conn.close()

def main():
    print("Server started on port", PORT)
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen()

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()

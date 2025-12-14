import socket
import threading
import sys

SERVER_IP = "127.0.0.1"
SERVER_PORT = 9001

peer_conn = None


def listen_server(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if msg:
                print("\n[SERVER]", msg.strip())
        except:
            break


def p2p_listener(port):
    s = socket.socket()
    s.bind(("0.0.0.0", port))
    s.listen()
    print(f"Listening on port: {port}")

    while True:
        conn, addr = s.accept()
        print(f"\n[P2P] Incoming connection from {addr}")
        global peer_conn
        peer_conn = conn
        threading.Thread(target=p2p_receive, args=(conn,), daemon=True).start()


def p2p_receive(conn):
    while True:
        try:
            msg = conn.recv(1024).decode()
            if msg:
                print("\n[P2P]", msg.strip())
        except:
            print("\n[P2P] Peer disconnected")
            break


def main():
    global peer_conn

    if len(sys.argv) != 3:
        print("Usage: python client.py <username> <p2p_port>")
        return

    username = sys.argv[1]
    p2p_port = int(sys.argv[2])

    # Connect to server
    server = socket.socket()
    server.connect((SERVER_IP, SERVER_PORT))
    server.sendall(f"REGISTER {username} {p2p_port}\n".encode())

    threading.Thread(target=listen_server, args=(server,), daemon=True).start()
    threading.Thread(target=p2p_listener, args=(p2p_port,), daemon=True).start()

    print(f"[INFO] Logged in as {username}")
    print("Commands:")
    print(" /list")
    print(" /addr <username>")
    print(" /msg <username> <message>   (via server)")
    print(" /connect <ip> <port>        (P2P)")
    print(" /disconnect")
    print(" /quit")

    while True:
        try:
            cmd = input(f"{username}> ").strip()

            #server commands
            if cmd == "/list":
                server.sendall(b"LIST\n")

            elif cmd.startswith("/addr"):
                server.sendall(f"GETADDR {cmd.split()[1]}\n".encode())

            elif cmd.startswith("/msg"):
                _, user, msg = cmd.split(" ", 2)
                server.sendall(f"MSG {user} {msg}\n".encode())

            #P2P protocol
            elif cmd.startswith("/connect"):
                _, ip, port = cmd.split()
                peer_conn = socket.socket()
                peer_conn.connect((ip, int(port)))
                print("[P2P] Connected to peer")
                threading.Thread(target=p2p_receive, args=(peer_conn,), daemon=True).start()

            elif cmd == "/disconnect":
                if peer_conn:
                    peer_conn.close()
                    peer_conn = None
                    print("[P2P] Disconnected. Back to server chat.")
                else:
                    print("[INFO] No P2P connection.")

            elif cmd == "/quit":
                server.sendall(b"QUIT\n")
                break

            # message
            else:
                if peer_conn:
                    peer_conn.sendall(f"{username}: {cmd}\n".encode())
                else:
                    print("[INFO] Use /msg <user> <text> to chat via server.")

        except KeyboardInterrupt:
            break

    server.close()
    if peer_conn:
        peer_conn.close()


if __name__ == "__main__":
    main()

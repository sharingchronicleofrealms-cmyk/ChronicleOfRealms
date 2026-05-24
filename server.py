import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 5555

clients = []
players = {}  # player_name -> simple state


def send(sock, msg):
    try:
        sock.send((json.dumps(msg) + "\n").encode())
    except:
        pass


def broadcast(msg):
    for c in clients:
        send(c, msg)


def handle_client(conn, addr):
    print("Connected:", addr)
    clients.append(conn)

    player_name = None

    try:
        buffer = ""

        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            buffer += data

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                msg = json.loads(line)

                msg_type = msg.get("type")
                player_name = msg.get("player", player_name)

                # JOIN
                if msg_type == "join":
                    players[player_name] = {
                        "x": 0,
                        "y": 0,
                        "hp": 10
                    }

                # ACTION (movement placeholder)
                elif msg_type == "action":
                    action = msg.get("data", {})

                    if player_name not in players:
                        continue

                    if action.get("move") == "up":
                        players[player_name]["y"] -= 1
                    if action.get("move") == "down":
                        players[player_name]["y"] += 1
                    if action.get("move") == "left":
                        players[player_name]["x"] -= 1
                    if action.get("move") == "right":
                        players[player_name]["x"] += 1

                # CHAT (global for now)
                elif msg_type == "chat":
                    broadcast({
                        "type": "chat",
                        "player": player_name,
                        "data": msg.get("data")
                    })

                # send updated world state to everyone
                broadcast({
                    "type": "state",
                    "data": players
                })

    except:
        pass

    print("Disconnected:", addr)
    if conn in clients:
        clients.remove(conn)
    conn.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Server running on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == "__main__":
    main()
import socket
import threading
import random

# clientii vor fi identificati dupa descriptorii de socket
print(socket.gethostname())
PORT = 3300
SERVER = socket.gethostbyname('127.0.0.1')
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
MAX_CLIENTS = 3
# AF_INET pentru adrese Internet Protocol v4; SOCK_STREAM pentru TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)
connections = []


def create_response(response_type, message):
    resp = {
        "type": response_type,
        "message": message
    }
    resp = str(resp).encode(FORMAT)
    return resp


def decide_game_result(server_choice, client_choice):
    if server_choice == client_choice:
        return 0
    elif server_choice == 'rock':
        if client_choice in ['scissors', 'lizard']:
            return 1
        elif client_choice in ['paper', 'spock']:
            return -1
    elif server_choice == 'paper':
        if client_choice in ['rock', 'spock']:
            return 1
        elif client_choice in ['scissors', 'lizard']:
            return -1
    elif server_choice == 'scissors':
        if client_choice in ['paper', 'lizard']:
            return 1
        elif client_choice in ['rock', 'spock']:
            return -1
    elif server_choice == 'lizard':
        if client_choice in ['paper', 'spock']:
            return 1
        elif client_choice in ['rock', 'scissors']:
            return -1
    elif server_choice == 'spock':
        if client_choice in ['rock', 'scissors']:
            return 1
        elif client_choice in ['paper', 'lizard']:
            return -1


def digest_client_request(conn, addr, client_request):
    if client_request["type"] == "player game choice":
        client_choice = client_request["message"].strip().lower()
        # serverul genereaza random o optiune
        options = ['rock', 'paper', 'scissors', 'lizard', 'spock']
        server_choice = random.choice(options)
        game_result = decide_game_result(server_choice, client_choice)
        if game_result == 1:
            msg = "You lost! "
        elif game_result == -1:
            msg = "You won! "
        elif game_result == 0:
            msg = "It's a tie! "

        msg += f"Server chose {server_choice}, you chose {client_choice}."
        resp = create_response("game result", msg)
        conn.send(resp)
        stop_game = False
        if game_result == 1 or game_result == -1:
            stop_game = True
        return stop_game


def handle_client(conn, addr):
    print(f"[SERVER] {addr} connected.")
    connected = True
    while connected:
        client_request = conn.recv(1024).decode(FORMAT)

        if client_request:
            client_request = eval(client_request)
            print(f"User({addr[1]}): {client_request}")
            stop_game = digest_client_request(conn, addr, client_request)
            if stop_game:
                connected = False
        else:
            connected = False
    # inchidem conexiunea
    print(f'Closing connection with user {addr[1]}...')
    connections.remove((conn, addr))
    conn.close()


def start():
    print("[SERVER] Server is starting...")
    server.listen()
    print(f"[SERVER] Server is listening on {SERVER}:{PORT}")
    while True:
        try:
            conn, addr = server.accept()
            # verificam daca mai pot intra si alti clienti
            if threading.activeCount() - 1 < MAX_CLIENTS:
                connections.append((conn, addr))
                thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                thread.start()
                print(f"[SERVER] TOTAL CONNECTIONS: {threading.activeCount() - 1}")
            else:
                print(f"Max players reached ({MAX_CLIENTS} players).")
                conn.send(create_response("server full", f"The server is full ({MAX_CLIENTS} players)."))
                conn.close()
        except:
            print('Sudden interrupt.')
            return


start()

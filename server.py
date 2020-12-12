import socket
import threading

# userii vor fi identificati dupa descriptorii de socket
print(socket.gethostname())
PORT = 3300
SERVER = socket.gethostbyname('127.0.0.1')
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
MAX_CLIENTS = 2
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)
connections = []


def handle_client(conn, addr):
    print(f"[SERVER] {addr} connected.")
    connected = True
    while connected:
        msg = conn.recv(1024).decode(FORMAT)

        if msg:
            # msg = eval(msg)
            print(f"User({addr[1]}): {msg}")
            # print(len(connections))
            # conn.send("Msg received".encode(FORMAT))
        else:
            connected = False
    # inchidem conexiunea
    print(f'Closing connection with user {addr[1]}...')
    connections.remove((conn, addr))
    conn.close()


def create_response(response_type, message):
    resp = {
        "type": response_type,
        "message": message
    }
    resp = str(resp).encode(FORMAT)
    return resp


def start():
    print("[SERVER] Server is starting...")
    server.listen()
    print(f"[SERVER] Server is listening on {SERVER}:{PORT}")
    while True:
        try:
            conn, addr = server.accept()
            # verificam daca mai pot intra si alti playeri
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
import socket
import threading

PORT = 3300
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "-d"
SERVER = socket.gethostbyname('127.0.0.1')
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
connected = True

message = []


# functii ce tin de comportamentul aplicatiei cand trimitem comenzi

def send_message(msg):
    message = str(msg).encode(FORMAT)
    client.send(message)


def send_message_handler():
    while connected:
        try:
            command = input()
            send_message(command)
            # verificam daca avem de a face cu un request de disconnect
            if check_disconnect_request(command):
                return
        except:
            print('Sudden interrupt.')
            return


def check_disconnect_request(msg):
    if msg == DISCONNECT_MESSAGE:
        send_message([msg])
        disconnect()
        print('Disconnected.')
        return True
    return False


def disconnect():
    global connected
    connected = False
    # sys.exit()


# functii ce tin de comportamentul aplicatie in momentul in care primim mesaje/comenzi

def receive_message_handler():
    while connected:
        msg = client.recv(1024).decode(FORMAT)

        # if message empty, disconnect
        if not msg:
            disconnect()
            return
        print('Raw message: ', msg)

        # msg = eval(msg)


# facem un thread care primeste mesaje de la server
thread_receive = threading.Thread(target=receive_message_handler, args=(), daemon=True)
thread_receive.start()
# pe threadul principal luam input de la client si il trimitem la server
send_message_handler()

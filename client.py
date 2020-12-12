import socket
import threading

PORT = 3300
FORMAT = 'utf-8'
SERVER = socket.gethostbyname('127.0.0.1')
ADDR = (SERVER, PORT)
# AF_INET pentru adrese Internet Protocol v4; SOCK_STREAM pentru TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
connected = True
message = []


# functii ce tin de comportamentul aplicatiei cand trimitem optiunile de joc
def send_option(option):
    option = option.strip().lower()
    options = ['rock', 'paper', 'scissors', 'lizard', 'spock']
    if not(option in options):
        print(f"Option is not valid. Try {options}")
        return
    req = {
        "type": "player game choice",
        "message": option
    }
    client_message = str(req).encode(FORMAT)
    client.send(client_message)


def send_message_handler():
    while connected:
        try:
            command = input()
            if not connected:
                return
            send_option(command)
        except:
            print('Sudden interrupt.')
            return


def disconnect():
    global connected
    connected = False
    print('Press RETURN to end execution...')


# functii ce tin de comportamentul aplicatie in momentul in care primim raspunsuri de la server


def receive_message_handler():
    while connected:
        resp = client.recv(1024).decode(FORMAT)
        # daca mesajul este gol, ne deconectam
        if not resp:
            print('Client disconnecting...')
            disconnect()
            return

        resp = eval(resp)
        print('Raw message: ', resp)
        if resp['type'] == 'game result':
            print(resp['message'])
            if "It's a tie!" in resp['message']:
                print("Rematch! Submit new choice!")


# facem un thread care primeste mesaje de la server
thread_receive = threading.Thread(target=receive_message_handler, args=(), daemon=True)
thread_receive.start()
# pe threadul principal luam input de la client si il trimitem la server
send_message_handler()

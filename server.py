import socket
import threading

HOST = "127.0.0.1"
PORT = 8080
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(128)
print("Server started to listen maximum 5 connections")


def handle_client(client_socket):
    client_socket.send("OK\n".encode("utf-8"))
    client_socket.close()


while True:
    client, addr = server.accept()
    print(f"Set up connection with {addr[0]}:{addr[1]}")
    handler = threading.Thread(
                                target=handle_client,
                                args=(client,),
                                daemon=True
                            )
    handler.start()

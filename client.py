import socket

TARGET_HOST = "localhost"
TARGET_PORT = 8080


def recv_all(client):
    data = b""
    while True:
        chunk = client.recv(1024)
        if chunk:
            data += chunk
        else:
            break
    return data


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((TARGET_HOST, TARGET_PORT))
response = recv_all(client)
if response.decode() == "OK\n":
    print("Message 'OK' was succesfully received")
else:
    print("Message 'OK' wasn't received")
client.close()

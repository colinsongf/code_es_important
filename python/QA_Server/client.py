import socket
import json
BUF_SIZE = 1024

client = socket.socket()

client.connect(('10.253.51.7',9002))
#client.connect(('0.0.0.0',9002))
while True:
    msg = input(">>>").strip()
    if len(msg) ==0: client.close()
    client.send(msg.encode("utf-8"))
    data = client.recv(BUF_SIZE)
    data = data.decode("utf-8")
    data = json.loads(data)
    print("recv:>",data)

client.close()


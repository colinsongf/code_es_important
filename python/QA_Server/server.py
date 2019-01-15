#利用python的socketserver起了一个并发的处理服务

import socketserver
import json
from QuestionAnswer import QuestionAnswer


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        qa = QuestionAnswer()
        while True:
            self.data = self.request.recv(1024)
            if not self.data:
                return
            self.data = self.data.decode("UTF-8")
            q = self.data
            answer = qa.find_answer(q)
            self.request.sendall(answer.encode("UTF-8"))


def start(host="localhost", port=9999):
    print("Begain to start!")
    server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999 #Linux
    start(HOST, PORT)


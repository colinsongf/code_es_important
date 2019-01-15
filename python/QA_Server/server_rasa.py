#利用python的socketserver起了一个并发的处理服务

import socketserver
import json
import logging
from urllib import parse,request

class QuestionAnswer():
    def __init__(self):
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
        logging.basicConfig(filename='grgnlp.log', level=logging.INFO, format=LOG_FORMAT)

    def find_answer_ec(self,text,u):
        logging.info("问题: %s",text)

        textmod={"sender": u, "message": text}
        textmod = json.dumps(textmod).encode(encoding='utf-8')
        header_dict = {"Content-Type": "application/json"}
        url='http://localhost:5002/webhooks/rest/webhook'
        req = request.Request(url=url,data=textmod,headers=header_dict)
        res = request.urlopen(req)
        res = res.read()
        txt = res.decode(encoding='utf-8')
        json_data = json.loads(txt)
        answer = json_data[0]['text']
        logging.info("回答: %s",answer)
        return str(answer)


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        qa = QuestionAnswer()
        while True:
            self.data = self.request.recv(1024)
            if not self.data:
                return
            self.data = self.data.decode("UTF-8")
            json_data = json.loads(self.data)
            q = json_data['data']['speechtext']
            u = json_data['clientIp']
            findstatus=[0]
            findanswer = qa.find_answer_ec(q, u)
            json_a ={
                        "status": findstatus[0],
                        "clientIp": u,
                        "msgType": 100,
                        "data": {
                            "speechtext": "",
                            "intent": findanswer
                        },
                        "timeOut": 30
                    }
            answer = json.dumps(json_a)

            self.request.sendall(answer.encode("UTF-8"))



def start(host="localhost", port=9002):
    print("Begain to start!")
    server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9002 #Linux
    start(HOST, PORT)


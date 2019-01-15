#!/usr/bin/python
# -*- coding: UTF-8 -*-


#单轮问答系统，基于es的tfidf搜索，期间添加了同义词，关键词提取，滑窗等

from elasticsearch import Elasticsearch
import pandas as pd
import json
import sys
import jieba
import jieba.posseg as pseg
import operator
import codecs
import logging
import random
from collections import deque

def main():
    es = ElasticSearch()
    input_text = sys.argv[1]
    jb = KeyWordExtract()
    queryDoc = es.search(input_text)
    if (len(queryDoc) == 0):
        print("请您移步到服务中心咨询工作人员")
    elif (len(queryDoc) == 2):
        print(queryDoc[1]) 
    else:
        keyword1 = jb.extractWord(input_text)
        for index in range(len(queryDoc)) :
            keyword2 = jb.extractWord(queryDoc[index])
            if jb.compareWord(keyword1, keyword2):
                print(queryDoc[index+1])
                return
            index = index+1 
            
        print("请您移步到服务中心咨询工作人员") 
        #print(queryDoc[1])


class QuestionAnswer:
    def __init__(self):
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
        logging.basicConfig(filename='grgnlp.log', level=logging.INFO, format=LOG_FORMAT)
        self.usr = {'robotname' : '我'}
        self.do_not_know = [
            "这个问题太难了，{robotname}还在学习中",
            "这个问题{robotname}不会，要么我去问下",
            "您刚才说的是什么，可以再重复一遍吗",
            "{robotname}刚才走神了，一不小心没听清",
            "{robotname}理解的不是很清楚啦，你就换种方式表达呗",
            "不如我们换个话题吧",
            "咱们聊点别的吧",
            "{robotname}正在学习中",
            "{robotname}正在学习哦",
            "不好意思请问您可以再说一次吗",
            "额，这个问题嘛。。。",
            "{robotname}得好好想一想呢",
            "请问您说什么",
            "您问的问题好有深度呀",
            "{robotname}没有听明白，您能再说一遍吗",
        ]
        self.es = ElasticSearch()
        self.jb = KeyWordExtract()
        self.sy = Synonym()
        self.status = 0 # 0：短句场景，1：长句场景
        self.canslc = ['一','二','三','四','五','六','七','八','九']
        self.amemory = deque(maxlen=10)
        self.qmemory = deque(maxlen=1)
        self.common_used_numerals={'一':1, '二':2, '两':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9}
        pass


    def random_item(self, mylist):
        assert mylist is not None, "The list can not be None."
        if isinstance(mylist, list):
            item = mylist[random.randint(0, len(mylist)-1)]
        elif isinstance(mylist, str):
            item = mylist
        return item


    def find_one_answer(self, queryDoc):
        logging.info("答案: %s", queryDoc[1])
        return str(queryDoc[1])


    def find_no_answer(self, longtext):
        logging.info("处理长问题")
        respstr = ""
        answerlist = self.jb.multiExtarctWord(longtext, self.es)
        answerlen = len(answerlist)
        if answerlen > 1 :
            respstr += "您问的是不是：%s，答案是：%s。" % (answerlist[answerlen-2], answerlist[answerlen-1])
        else :
            response = self.random_item(self.do_not_know)
            respstr = response.format(**self.usr)

        logging.info("答案: %s", respstr)
        return str(respstr)


    def find_milti_answer(self, queryDoc, textstr, stat):
        keyword1 = self.jb.extractWord(textstr)
        for index in range(0, len(queryDoc), 2) :
            keyword2 = self.jb.extractWord(queryDoc[index])
            if self.jb.compareWord(keyword1, keyword2):
                logging.info("答案: %s", queryDoc[index+1])
                return str(queryDoc[index+1])
        
        response = self.random_item(self.do_not_know)
        respstr = response.format(**self.usr)
        logging.info("答案: %s", respstr)
        stat[0]=1
        return str(respstr)


    def find_long_question(self, req):
        respstr = ""
        if req == "退出" :
            respstr = "您好，请详细说明要咨询的问题，如：去火车站怎么走"
            self.status = 0
            self.qmemory.clear()
            self.amemory.clear()
            return str(respstr)
        else:
            for word in req:
                if word in self.canslc:
                    index = self.common_used_numerals.get(word)
                    if index <= self.amemory[-1]:
                        respstr = self.amemory[index-1]
                        self.status = 0
                        self.qmemory.clear()
                        self.amemory.clear()
                    
        if respstr == "":
            respstr = self.qmemory[0]

        logging.info("答案: %s", respstr)
        return str(respstr)

    def find_answer_cc(self,text,status):
        logging.info("问题: %s",text)
        queryDoc = self.es.search_cc(text, 5)
        if (len(queryDoc) == 0):
            response = self.random_item(self.do_not_know)
            respstr = response.format(**self.usr)
            logging.info("答案: %s", respstr)
            status[0]=1
            return str(respstr)
        elif (len(queryDoc) == 2):
            return self.find_one_answer(queryDoc)
        else:
            return self.find_milti_answer(queryDoc, text, status)
            

    def find_answer(self,input_text):
        logging.info("问题: %s",input_text)
        text = self.sy.synonymstr(input_text)
        logging.info("处理之后: %s", text)
        if self.status == 0 :
            queryDoc = self.es.search(text, 5)
            if (len(queryDoc) == 0):
                return self.find_no_answer(text)
            elif (len(queryDoc) == 2):
                return self.find_one_answer(queryDoc)
            else:
                return self.find_milti_answer(queryDoc, text)
        else :
            return self.find_long_question(text)

'''

class QuestionAnswer:
    def __init__(self):
        pass
    
    #def find_answer(self,input_text):
    def find_answer(self,text):
        es = ElasticSearch()
        jb = KeyWordExtract()
        #sy = Synonym()
        #text = sy.synonymstr(input_text)
        #print (text)
        queryDoc = es.search(text)
        if (len(queryDoc) == 0): 
            return str(json.dumps({"answer":"我也不知道"}))
        elif (len(queryDoc) == 2): 
            return str(json.dumps({"answer":queryDoc[1]}))
        else:
            keyword1 = jb.extractWord(text)
            for index in range(len(queryDoc)) :
                keyword2 = jb.extractWord(queryDoc[index])
                if jb.compareWord(keyword1, keyword2):
                    return str(json.dumps({"answer":queryDoc[index+1]}))
                index = index+1 
        return str(json.dumps({"answer":"我也不知道"}))
'''
#同义词处理
class Synonym: 

    def __init__(self):  
        seperate_word = {}
        self.dict1 = {}
        i=0
        file = codecs.open("sameword.txt","r","utf-8") 
        lines = file.readlines()  
        for line in lines:
           seperate_word[i] = line.split()  
           i = i + 1
        x1 = len(lines)
        for i in range(0, x1):
            x2 = {k: seperate_word[i][0] for k in seperate_word[i]}  
            self.dict1 = dict(self.dict1, **x2)  

    def synonym(self, txt):
        word = ""
        if txt in self.dict1:
            word = self.dict1[txt]
            return word
        else:
            return txt

    def synonymstr(self, txt):
        seg_list = pseg.cut(txt)
        word_list = []
        for w in seg_list :
            if operator.eq(w.flag, "ns"):
                sameWord = self.synonym(w.word)
                word_list.append(sameWord)
                continue
            word_list.append(w.word)
        sameStr = ""
        same_str = sameStr.join(word_list)
        return  same_str


#关键词提取加滑窗处理长问句
class KeyWordExtract:
    def __init__(self):
        self.jb = jieba.load_userdict("dict.txt")

    def extractWord(self, input_text):
        seg_list = pseg.cut(input_text)
        word_list = []
        for w in seg_list :
            if operator.eq(w.flag, "ns"):
                word_list.append(w.word)
        return word_list
       
    def compareWord(self, kw1, kw2):
        for w in kw1:
            for k in kw2:
                if operator.eq(w, k):
                    return True
        return False

    def multiExtarctWord(self, text, es):
        l = 0
        kwList = self.extractWord(text)
        joinStr = ""
        kwNum = len(kwList)
        answer = []

        if kwNum == 1:
            qlist =  es.search(kwList[0], 1)
            if len(qlist) > 1:
                answer.append(qlist[0])
                answer.append(qlist[1])
            return answer
        
        for i in range(kwNum-1, 0 , -1):
            while l + i<= kwNum :
                kWord = joinStr.join(kwList[l:l+i])
                # todo search
                qlist =  es.search(kWord, 1)
                if len(qlist) > 1:
                    answer.append(qlist[0])
                    answer.append(qlist[1])
                # end of serach
                l += 1
            if len(answer) > 1:
                return answer
            l = 0
        return answer

"""
    类名称：ElasticSearch
    描述: ElasticSearch查找相关操作
"""
class ElasticSearch:
    def __init__(self):
        self.es = Elasticsearch([{"host":"10.253.51.7","port":9200}])
        #LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
        #logging.basicConfig(filename='grgglp.log',  format=LOG_FORMAT)
    
    """
        函数名称：getDataFromFile
        描述： 从文本中得到数据
        参数: 无
        返回值: None
    """
    def getDataFromFile(self):
        file_data = pd.read_csv("./subway_qa_new.csv") 
        file_json = file_data.to_json(orient="records")
        file_json_list = json.loads(file_json)
        return file_json_list
    
    """
        函数名称：createIndex
        描述：创建索引文件
        参数: 无
        返回值: None
    """
    def createIndex(self,index_name,doc_type_name):
        file_json_list = self.getDataFromFile()
        print(len(file_json_list)) 
        for i in range(len(file_json_list)):  
            self.es.index(index=index_name,doc_type=doc_type_name,body=json.dumps(file_json_list[i]))
    
    """
        函数名称：search
        描述：通过ElasticSearch从Index中查询文件
        参数: input_text:输入的文本
        返回值: 50个查询到的匹配输入文本的答案
    """
    def search(self, input_text, qsize):
        query = {"query":{"match":{"Question": input_text}}}
        query_doc = self.es.search(body = query,size = qsize)
        query_doc_source = query_doc["hits"]["hits"]
        query_list = []
        for i in range(len(query_doc_source)):
            logging.info("分数: %s, 问题: %s",query_doc_source[i]["_score"], query_doc_source[i]["_source"]["Question"])
        for i in range(len(query_doc_source)):
            if(query_doc_source[i]["_score"] > 2.0) :
                query_list.append(query_doc_source[i]["_source"]["Question"])
                query_list.append(query_doc_source[i]["_source"]["Answer"])
                return query_list
            if(query_doc_source[i]["_score"] > 1.6) :
                query_list.append(query_doc_source[i]["_source"]["Question"])
                query_list.append(query_doc_source[i]["_source"]["Answer"])
        return query_list

    def search_cc(self, input_text, qsize):
        query = {"query":{"match":{"Sentence": input_text}}}
        query_doc = self.es.search(index="ccbank_index",doc_type="ccbank_doc",body = query,size = qsize)
        query_doc_source = query_doc["hits"]["hits"]
        query_list = []
        for i in range(len(query_doc_source)):
            logging.info("分数: %s, 问题: %s",query_doc_source[i]["_score"], query_doc_source[i]["_source"]["Sentence"])
        for i in range(len(query_doc_source)):
            if(query_doc_source[i]["_score"] > 2.0) :
                query_list.append(query_doc_source[i]["_source"]["Sentence"])
                query_list.append(query_doc_source[i]["_source"]["Command"])
                return query_list
            if(query_doc_source[i]["_score"] > 1.6) :
                query_list.append(query_doc_source[i]["_source"]["Sentence"])
                query_list.append(query_doc_source[i]["_source"]["Command"])
        return query_list 

    def searchALL(self):
        query = {"query":{"match_all":{}}}
        query_doc = self.es.search(body = query,size = 10)
        return query_doc
   
if __name__ == '__main__':
    main()


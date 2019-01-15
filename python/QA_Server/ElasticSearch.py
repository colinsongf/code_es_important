#!/usr/bin/python
# -*- coding: UTF-8 -*-

#向es插入数据

from elasticsearch import Elasticsearch
import pandas as pd
import json
import sys

'''
def analysis(x):
    result_list = x[2].replace("<br>","").split("问：")
    site = result_list[0]
    question_answer_list = result_list[1].split("答：")
    question = question_answer_list[1]
    answer_list = question_answer_list[0].split("@")
    
    qa_list = []
    for answer in answer_list:
        qa_one_list = []
        qa_one_list.append(answer)
        qa_one_list.append(question)
        qa_list.append(qa_one_list)
    print(qa_list)
    return qa_list

def standardization():
    answer_list = []
    file_data = pd.read_csv("./subway_question_answer.csv",header = None) 
    answer_list = file_data[[2]].apply(lambda x:analysis(x),axis = 1)
    result_list = []
    for i in range(len(answer_list)):
        result_list.extend(answer_list[i])
    result_pd = pd.DataFrame(result_list)
    result_pd.to_csv("./subway_qa.csv",header = False,index = False)

'''


def main():
    #standardization()
    es = ElasticSearch()
    #es.createIndex("ccbank_index","ccbank_doc")
    #input_text = "1"
    #input_text = "尝美食"
    #input_text = sys.argv[1]
    #queryDoc = es.search(input_text)
    queryDoc = es.searchALL()
    print(queryDoc)

"""
    类名称：ElasticSearch
    描述: ElasticSearch查找相关操作
"""
class ElasticSearch:
    def __init__(self):
        self.es = Elasticsearch([{"host":"10.253.51.7","port":9200}])
    
    """
        函数名称：getDataFromFile
        描述： 从文本中得到数据
        参数: 无
        返回值: None
    """
    def getDataFromFile(self):
        file_data = pd.read_csv("./bank_modify.csv") 
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
    def search(self, input_text):
        query = {"query":{"match":{"Sentence": input_text}}}
        query_doc = self.es.search(index="ccbank_index",doc_type="ccbank_doc",body = query,size = 10)
        query_doc_source = query_doc["hits"]["hits"]
        query_list = []
        for i in range(len(query_doc_source)):
            if(query_doc_source[i]["_score"] > 1.0) : 
                query_list.append(query_doc_source[i]["_source"]["Sentence"])
                query_list.append(query_doc_source[i]["_score"])
        #print(query_list)
        return query_list

    def searchALL(self):
        query = {"query":{"match_all":{}}}
        query_doc = self.es.search(index="ccbank_index",doc_type="ccbank_doc",body = query,size = 10)
        return query_doc
   
if __name__ == '__main__':
    main()




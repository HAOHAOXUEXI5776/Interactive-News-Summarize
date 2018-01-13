#coding:utf-8
import numpy as np
import copy #用于深复制
class ANew():
    def __init__(self):
        self.title = []
        self.body = []
        self.bodySize = 0
        self.OneGram = [] #维度为“所有满足要求的OneGram的长度”
                          #记录对应OneGram出现的次数
        self.OneGramLen = 0
        self.v = [] #文章的向量化表示，用于计算ICS
                    #计算的方式为：包含的OneGramId的平均
        self.vf = 0. #v的范数
        # self.v = [] # same size as dictionary

    def SetSelf(self, title, body):
        self.title = title.strip().split()
        self.body = body.strip().split()
        self.bodySize = len(self.body)

    def SetOneGram(self, OneGramId, dics2i):
        self.OneGramLen = len(OneGramId)
        self.OneGram = [0 for i in range(0, self.OneGramLen)]
        # allword = copy.deepcopy(self.title)
        # allword.extend(self.body)
        # for word in allword:
        for word in self.body:
            wid = dics2i[word]
            for i in range(0, self.OneGramLen):
                if wid == OneGramId[i]:
                    self.OneGram[i] += 1
                    break


    def Setv(self, oneGram, OneGramId):
        self.v = [0. for i in range(0, self.OneGramLen)]
        self.vf = 0.
        for i in range(0, self.OneGramLen):
            wid = OneGramId[i]
            self.v[i] = self.OneGram[i]*oneGram[wid].tfidf
            self.vf += self.v[i]*self.v[i]
        self.vf = np.sqrt(self.vf)

def BuildNews(NewsName, NewsNum):
    New = []
    fn = './Processed/'+NewsName+'/words.txt'
    f = open(fn, 'r')
    for i in range(0, NewsNum):
        a = ANew()
        title = f.readline()
        body = f.readline()
        a.SetSelf(title, body)
        New.append(a)
    f.close()
    return New

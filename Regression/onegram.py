#coding:utf-8
import numpy as np
class ANgram():
    def __init__(self, n):
        self.n = n #n-gram中的n

        self.tfidf = 0.
        self.len = 0
        self.inTitle = 0 #出现在标题中的次数
        self.ics = 0. # Intra-cluster Similarity
        self.ce = 0. #类别信息熵
        self.ide = 0.

        self.tf = 0
        self.content = ""#记录该n-gram的内容
        self.inNew = [] #记录在哪些文章中出现过
        self.inNewLen = 0 #多少篇文章中出现过
        self.lcontent = [] #左边的上下文
        self.rcontent = [] #右边的上下文

    def downinNew(self):
        #有重复的文章编号
        a = list(set(self.inNew))
        a.sort()
        self.inNew = a
        self.inNewLen = len(self.inNew)

    def update(self, intitle, nid):
        #该词在标题中，则intitle为1，否则为0
        self.inNew.append(nid)
        self.inTitle += intitle
        self.tf += 1

    def gettfidf(self, newsnum):
        inNewLen = float(self.inNewLen)
        self.tfidf = self.tf*np.log(newsnum/inNewLen)

    def getics(self, New, OneGramLen):
        #包含该词的文章的相似度
        o = [0. for i in range(0, OneGramLen)] #这些文章的平均向量
        of = 0. #o的范数||o||
        for newsid in self.inNew:
            for i in range(0, OneGramLen):
                o[i] += New[newsid].v[i]
        inNewLen = float(self.inNewLen)
        for i in range(0, OneGramLen):
            o[i]/=inNewLen
        for i in range(0, OneGramLen):
            of += o[i]*o[i]
        of = np.sqrt(of)

        cossum = 0.
        for newsid in self.inNew:
            tmpcos = 0.
            for i in range(0, OneGramLen):
                tmpcos += o[i]*New[newsid].v[i]
            if New[newsid].vf != 0 and of != 0:
                tmpcos /=(New[newsid].vf*of)
            cossum += tmpcos
        self.ics = cossum/inNewLen

    def getce(self, oneGram, OneGramId):
        #其他的词与该词在同一篇新闻的次数越高
        #说明该词不具代表性
        self.ce = 0.
        inNewLen = float(self.inNewLen)
        for ogid in OneGramId:
            overlap = 0
            otherinNew = oneGram[ogid].inNew
            for newsid in self.inNew:
                if newsid in otherinNew:
                    overlap += 1
            if overlap != 0:
                ol = overlap/inNewLen
                self.ce += ol*np.log(ol)
        self.ce = -1*self.ce

    def getide(self):
        idel = 0.
        left = {} #统计左边上下文的词的频数
        for le in self.lcontent:
            if le not in left:
                left[le] = 1
            else:
                left[le] += 1
        for le in left:
            left[le] /= float(self.tf)
            idel += left[le]*np.log(left[le])
        idel = -1*idel

        ider = 0.
        right = {}
        for ri in self.rcontent:
            if ri not in right:
                right[ri] = 1
            else:
                right[ri] += 1
        for ri in right:
            right[ri] /= float(self.tf)
            ider += right[ri]*np.log(right[ri])
        ider = -1*ider
        self.ide = (ider+idel)/2.0



    def p(self, dici2s, f=""):
        outstr = self.content
        outstr += "tf="+str(self.tf)+" inTitle="+str(self.inTitle)+'\n'
        outstr += "tfidf="+str(self.tfidf)+" ics="+str(self.ics)+" ide="+str(self.ide)+" ce="+str(self.ce)
        # for nid in self.inNew:
            # outstr += str(nid)+' '
        # print outstr
        if f != "":
            f.write(outstr+'\n')

windows = 3 #上下文的窗口大小
#构造OneGram使用词典来构造
def Build1Gram(NewsName, NewsNum, dics2i, dici2s, dicL,stoplist):
    OneGram = [] #1-gram tf >= 25
    OneGramId = [] # 记录OneGram对应的在词典中的id
    oneGram = [] #all 1-gram
    for i in range(0, dicL):
        a = ANgram(1)
        a.content = dici2s[i]
        a.len = len(dici2s[i])
        # print dici2s[i]
        # exit()
        oneGram.append(a)
    fn = './Processed/'+NewsName+'/words.txt'
    f = open(fn, 'r')
    for i in range(0, NewsNum):
        widl = []
        title = f.readline().strip().split()
        titlelen = len(title)
        for word in title:
            wid = dics2i[word]
            widl.append(wid)
        for j in range(0, titlelen):
            wid = widl[j]
            oneGram[wid].update(1, i-1)
            #添加上下文
            k = j - 1
            while k >= 0 and k >= j-windows:
                oneGram[wid].lcontent.append(widl[k])
                k -=1
            k = j + 1
            while k < titlelen and k <= j + windows:
                oneGram[wid].rcontent.append(widl[k])
                k+=1

        widl = []
        body = f.readline().strip().split()
        bodylen = len(body)
        for word in body:
            wid = dics2i[word]
            widl.append(wid)
        for j in range(0, bodylen):
            wid = widl[j]
            oneGram[wid].update(0, i-1)
            #添加上下文
            k = j - 1
            while k >= 0 and k >= j-windows:
                oneGram[wid].lcontent.append(widl[k])
                k-=1
            k = j + 1
            while k < bodylen and k <= j + windows:
                oneGram[wid].rcontent.append(widl[k])
                k+=1
    f.close()

    for i in range(0, dicL):
        word = oneGram[i].content
        if oneGram[i].tf >= 25 and word not in stoplist and len(word) > 3:# and hasNumbers(word) == False:
            OneGram.append(oneGram[i])
            OneGramId.append(i)

    print "1-gram: size = ", len(OneGram)
    for g in OneGram:
        g.downinNew()

    return OneGram, OneGramId, oneGram

def BuildnGram(n, NewsName, NewsNum,stoplist):
    BiGram = []
    biGram = []
    biGramDic = {}
    biCnt = 0
    fn = './Processed/'+NewsName+'/words.txt'
    f = open(fn, 'r')
    for i in range(0, NewsNum):
        #title
        title = f.readline().strip().split()
        titlelen = len(title)
        for j in range(0, titlelen - n+1):
            if title[j] not in stoplist:
                tmp = title[j]
                jl = j+n-1
                while title[jl] in stoplist:
                    jl -= 1
                for k in range(j+1, jl+1):
                    tmp += '+' + title[k]
                if tmp not in biGramDic:
                    a = ANgram(n)
                    a.content = tmp
                    a.len = len(tmp)
                    biGram.append(a)

                    biGramDic[tmp] = biCnt
                    biCnt += 1
                curid = biGramDic[tmp]
                biGram[curid].update(1, i-1)
                k = j - 1
                while k >= 0 and k >= j-windows:
                    biGram[curid].lcontent.append(title[k])
                    k-=1
                k = j + 1
                while k < titlelen and k <= j + windows:
                    biGram[curid].rcontent.append(title[k])
                    k+=1
        #body
        body = f.readline().strip().replace('。', '，').replace('！', '，').replace('?', '，')
        body = body.split('，')
        for sent in body:
            sent = sent.split()
            sentlen = len(sent)
            for j in range(0, sentlen-n+1):
                if sent[j] not in stoplist:
                    tmp = sent[j]
                    jl = j+n-1
                    while sent[jl] in stoplist:
                        jl -= 1
                    for k in range(j+1, jl+1):
                        tmp += '+' + sent[k]
                    if tmp not in biGramDic:
                        a = ANgram(n)
                        a.content = tmp
                        biGram.append(a)
                        biGramDic[tmp] = biCnt
                        biCnt+=1
                    curid = biGramDic[tmp]
                    biGram[curid].update(0,i-1)

                    k = j - 1
                    while k >= 0 and k >= j-windows:
                        biGram[curid].lcontent.append(sent[k])
                        k-=1
                    k = j + 1
                    while k < sentlen and k <= j + windows:
                        biGram[curid].rcontent.append(sent[k])
                        k+=1
    f.close()
    for agram in biGram:
        if agram.tf >= 10:
            tmp = agram.content.split('+')
            if len(tmp) == n and len(agram.content)>3:
                agram.downinNew()
                BiGram.append(agram)
    print ("%dgram:size = %d"%(n, len(BiGram)))

    return BiGram, biGram


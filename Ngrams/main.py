#coding:utf-8
import math
from news import *
from onegram import *
import re
def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))
def getStoplist():
    s = {}
    f = open("../stopword.txt", 'r')
    for line in f:
        line = line.strip()
        if line not in s:
            s[line] = 0
    f.close()
    return s
stoplist = getStoplist()


#本程序需要的文件：
#对于新闻NewsName，进行分词，得到两个文件：
#   dict.txt--字典
#   words.txt--每两行对应一个文件，第一行是标题，第二行是内容

# NewsName = 'iPhone X'
newsName = ['hpv疫苗','iPhone X', '乌镇互联网大会','九寨沟7.0级地震','俄罗斯世界杯',\
'双十一购物节', '德国大选', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',\
'王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',\
'萨德系统 中韩', '雄安新区', '功守道', '榆林产妇坠楼']
for NewsName in newsName:
    NewsName = unicode(NewsName, 'utf8')
    f = open('./Processed/'+NewsName+'/words.txt', 'r')
    NewsNum = int(len(f.readlines())/2) #words.txt中有2*NewsNum行

    def BuildDict():
        #从词典中得到两个词典：index2string和string2index，index从0开始
        d1 = {}
        d2 = {}
        fn = './Processed/'+NewsName+'/dict.txt'
        f = open(fn, 'r')
        wid = 0
        for word in f:
            word = word.strip()
            d1[word] = wid
            d2[wid] = word
            wid += 1
        # print len(d)
        return d1, d2
    dics2i, dici2s = BuildDict()
    dicL = len(dics2i)


    print 'Build 1gram..'
    # OneGram #1-gram tf >= 25
    # OneGramId  # 记录OneGram对应的在词典中的id
    # oneGram  #all 1-gram
    OneGram, OneGramId, oneGram = Build1Gram(NewsName, NewsNum, dics2i, dici2s, dicL,stoplist)
    OneGramLen = len(OneGram)

    print 'Build 2gram..'
    BiGram, biGram = BuildnGram(2, NewsName, NewsNum,stoplist) #构造bigram

    print 'Build 3gram..'
    TrGram, trGram = BuildnGram(3, NewsName, NewsNum,stoplist) #构造Trigram

    allGram = OneGram
    allGram.extend(BiGram)
    allGram.extend(TrGram)

    print 'Build News..'
    New = BuildNews(NewsName, NewsNum)

    #计算ce、ics需要用到oneGram、OneGramId
    print 'get tfidf and ce..'
    for g in allGram:
        g.gettfidf(NewsNum+1)
        g.getce(oneGram, OneGramId)

    #利用1-gram得到每篇新闻的向量表示
    # **需要在OneGram计算出tfidf后才能开始这一步
    print 'get news\'vector..'
    for anew in New:
        anew.SetOneGram(OneGramId, dics2i)
        #Setv需要n-gram的tfidf值
        anew.Setv(oneGram, OneGramId)

    #getics需要每篇新闻的向量表示，故在anew.Setv之后
    print 'get ics and ide..'
    for g in allGram:
        g.getics(New, OneGramLen)
        g.getide()


    # 打印特征值
    print 'get X..'
    f = open('./Processed/feature/'+NewsName+'.txt', 'w')
    for g in allGram:
        f.write(g.content+' ')
        f.write(str(g.tfidf)+' '+str(g.len)+' '+str(g.ics)+' '+str(g.ce)+' '+str(g.ide)+' '+str(g.inTitle)+' '+str(g.n))
        f.write('\n')
    f.close()

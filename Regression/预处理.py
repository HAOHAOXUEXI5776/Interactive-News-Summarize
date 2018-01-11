#coding:utf-8
# coding=gbk
import codecs
import sys
reload(sys)
sys.setdefaultencoding('gbk')
import os
LTP_DATA_DIR = 'D:/coding/Python2.7/ltp_data_v3.4.0'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
from pyltp import Segmentor
#分词
segmentor = Segmentor()  # 初始化实例
segmentor.load(cws_model_path)  # 加载模型


NewsName = ['hpv疫苗','iPhone X', '乌镇互联网大会','九寨沟7.0级地震','俄罗斯世界杯',\
'双十一购物节', '德国大选', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',\
'王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',\
'萨德系统 中韩', '雄安新区', '功守道', '榆林产妇坠楼']

for news in NewsName:
    print news
    howmuch = os.listdir(unicode('../News/'+news,'utf8'))
    howmuch = len(howmuch) - 2 #该新闻有多少篇
    DIR = '../News/'+news+'/'
    F1 = './Processed/'+news+'/words.txt'
    F2 = './Processed/'+news+'/dict.txt'
    dirpath = './Processed/'+news
    if os.path.exists(dirpath) == False:
        os.makedirs(unicode(dirpath, 'utf8'))
    f1 = open(unicode(F1,'utf8'), 'w')
    f2 = open(unicode(F2,'utf8'), 'w')
    dic = {}

    for i in range(1, howmuch+1):
        F0 = DIR + str(i) + '.txt'
        f0 = open(unicode(F0,'utf8'), 'r')

        title = f0.readline().strip() #第一行为标题
        words = segmentor.segment(title)
        for word in words:
            if word not in dic:
                dic[word] = 0

        f1.write(' '.join(words)+'\n')

        while True:
            line = f0.readline()
            #print line
            if len(line) == 0:
                break
            if line == '\n':
                continue
            words = segmentor.segment(line.strip())
            for word in words:
                if word not in dic:
                    dic[word] = 0
            f1.write(' '.join(words)+' ')

        f1.write('\n')
        f0.close()

    for word in dic:
        f2.write(word+'\n')
    f1.close()
    f2.close()

segmentor.release()  # 释放模型


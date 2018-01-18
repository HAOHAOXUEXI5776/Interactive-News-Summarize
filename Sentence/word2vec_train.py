# coding:utf-8

# 使用gensim的word2vec模块，以分词后的新闻作为语料，训练一个word2vec模型

from gensim.models import word2vec


news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']
data = []

for news in news_name:
    f = open(unicode('../Ngrams/Processed/' + news + '/words.txt','utf8'), 'r')
    for line in f:
        line = line.strip().split()
        data.append(line)
    f.close()
model = word2vec.Word2Vec(data, iter=100)
model.save('model')


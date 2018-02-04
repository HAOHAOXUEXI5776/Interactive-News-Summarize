# coding:utf-8

import gensim
from pyltp import Segmentor
from numpy import *  # 用于矩阵运算
import copy  # 用于深复制
import os

qin = 0  # 改成0是刘辉的路径，否则是秦文涛的路径
# 加载分词模型
segmentor = Segmentor()
if qin == 1:
    segmentor.load('D:/coding/Python2.7/ltp_data_v3.4.0/cws.model')
    model = gensim.models.Word2Vec.load('../Sentence/model_qin')
else:
    segmentor.load('/Users/liuhui/Desktop/实验室/LTP/ltp_data_v3.4.0/cws.model')
    model = gensim.models.Word2Vec.load('../Sentence/model')
vec_size = 100

stoplist = {}
f = open('../stopword.txt', 'r')
for line in f:
    word = line.strip()
    stoplist[word] = 1
f.close()


class Sent:
    def __init__(self, _newsid, _globalid, _paraid, _localid, _sentnum, _content, _vec):
        self.newsid = _newsid  # 该句所属新闻编号
        self.globalid = _globalid  # 该句在该篇新闻的第几句
        self.paraid = _paraid  # 该句在该篇新闻的第几段
        self.localid = _localid  # 该句在所属段的第几句
        self.sentnum = _sentnum  # 该句所在段有多少句
        self.content = _content
        self.vec = _vec


# 计算几个向量的平均向量
def mean_vec(vec_list):
    if len(vec_list) == 0:
        return [0.0 for k in range(0, vec_size)]
    result = [0.0 for k in range(0, len(vec_list[0]))]
    for vec in vec_list:
        for k in range(0, len(result)):
            result[k] += vec[k]
    for k in range(0, len(result)):
        result[k] /= len(vec_list)
    return result


# 计算两个向量的余弦相似度
def cos_similarity(vec1, vec2):
    result = 0.0
    vec1_size = 0.0
    vec2_size = 0.0
    for k in range(0, len(vec1)):
        result += vec1[k] * vec2[k]
        vec1_size += vec1[k] * vec1[k]
        vec2_size += vec2[k] * vec2[k]
    if vec1_size < 1e-10 or vec2_size < 1e-10:
        return 0.0
    result /= sqrt(vec1_size * vec2_size)
    return result


# 计算两个块之间的相似度：取块间句子的最大相似度
def block_simi(block1, block2):
    max_simi = 0.0
    for sent1 in block1:
        for sent2 in block2:
            max_simi = max(max_simi, cos_similarity(sent1.vec, sent2.vec))
    return max_simi


# 返回news下label对应的块，以及它们的mmr得分
def blockscore(blockDir, news, label, labelv):
    # 得到该标签下所有块
    f = open(unicode(blockDir + news + '/' + label + '.txt', 'utf8'), 'r')
    blocks = []
    while True:
        n = f.readline()  # 第一行记录了下面几个句子是一个块
        if len(n) == 0:
            break
        block = []
        n = int(n.strip())
        for i in range(0, n):
            nums = f.readline()
            nums = nums.strip().split()
            nums = [int(num) for num in nums]
            content = f.readline().strip()
            words = segmentor.segment(content)
            word_vec_list = []
            for word in words:
                if word not in stoplist and word in model:
                    word_vec_list.append(model[word])
            sent = Sent(nums[0], nums[1], nums[2], nums[3], nums[4], content, mean_vec(word_vec_list))
            block.append(sent)
        blocks.append(block)
    f.close()

    blockcnt = len(blocks)

    # pageRank部分

    unipai = [0.0 for i in range(0, blockcnt)]
    for i in range(0, blockcnt):
        # 取块中句子和标签相似度最大的为块与标签的相似度
        max_simi = 0.0
        for sent in blocks[i]:
            max_simi = max(max_simi, cos_similarity(labelv, sent.vec))
        unipai[i] = max_simi
    # 对unipai归一化
    sumi = sum(unipai)
    if sumi == 0.0:
        unipai = [1.0 / blockcnt for i in range(0, blockcnt)]
    else:
        unipai = [t / sumi for t in unipai]
    unipai = mat(unipai)  # 1*blockcnt维矩阵
    pai = copy.deepcopy(unipai)  # 每个块的初始得分

    # 根据相似度，计算初始的转移概率矩阵p0
    p0 = []
    for i in range(0, blockcnt):
        tmp = [0.0 for i in range(0, blockcnt)]
        p0.append(tmp)
    for i in range(0, blockcnt):
        for j in range(i + 1, blockcnt):
            simi = block_simi(blocks[i], blocks[j])
            p0[i][j] = p0[j][i] = simi

    # 对转移概率归一化
    for i in range(0, blockcnt):
        sumi = sum(p0[i])
        if sumi != 0.0:
            p0[i] = [p0[i][j] / sumi for j in range(0, blockcnt)]
    p0 = mat(p0)  # blockcnt*blockcnt维矩阵

    iters = 100
    a = 0.8
    for i in range(0, iters):
        oldpai = copy.deepcopy(pai)
        pai = a * oldpai * p0 + (1 - a) * unipai  # pageRank
        # pai几乎不变，则停止迭代
        stop = True
        for j in range(0, blockcnt):
            if fabs(oldpai[0, j] - pai[0, j]) > 1e-10:
                stop = False
                break
        if stop:
            break

    tpai = [pai[0, j] for j in range(0, blockcnt)]
    # mmr
    score = []
    index = []
    lambd = 0.7
    for i in range(0, blockcnt):
        maxmmr, maxj = -1e9, 0
        for j in range(0, blockcnt):
            if j not in index:
                max_simi = 0.0
                for k in index:
                    max_simi = max(max_simi, p0[j, k])
                mmr = (1 - lambd) * tpai[j] - lambd * max_simi
                if mmr > maxmmr:
                    maxmmr = mmr
                    maxj = j

        score.append(maxmmr)
        index.append(maxj)

    return blocks, score, index


blockDir = '../Sentence/assign/little_block/'
labelDir = '../Sentence/label/'
outDir = 'blockscore/'

news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']
for news in news_name:
    print news
    f = open(unicode(labelDir + news + '/label.txt', 'utf8'), 'r')
    labels = [line.strip().replace('+', '') for line in f]
    f.close()

    # 计算每个标签的word2vec向量
    labelv = []
    f = open(unicode(labelDir + news + '/label.txt', 'utf8'), 'r')
    for line in f:
        lable = line.strip().split('+')
        word_vec_list = []
        for word in lable:
            if word in model and word not in stoplist:
                word_vec_list.append(model[word])
        labelv.append(mean_vec(word_vec_list))
    f.close()

    for labelid, label in enumerate(labels):
        print label
        blocks, bscore, index = blockscore(blockDir, news, label, labelv[labelid])

        path = outDir + news
        if not os.path.exists(unicode(path, 'utf8')):
            os.mkdir(unicode(path, 'utf8'))

        f = open(unicode(path + '/' + label + '.txt', 'utf8'), 'w')
        blockcnt = len(blocks)
        for i in range(0, blockcnt):
            curi = index[i]
            f.write(str(len(blocks[curi])) + '\n')
            for sent in blocks[curi]:
                f.write(str(sent.newsid) + ' ' + str(sent.globalid) + ' ' + str(sent.paraid) + ' ' + str(
                    sent.localid) + ' ' + str(sent.sentnum) + '\n')
                f.write(sent.content + '\n')
        f.close()

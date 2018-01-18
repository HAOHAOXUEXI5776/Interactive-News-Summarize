# coding:utf-8

import gensim
from pyltp import Segmentor
from numpy import *  # 用于矩阵运算
import copy  # 用于深复制

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


# 返回news下label对应的块，以及它们的Rank得分，way = pageRank|divRank
def blockscore(blockDir, news, label, way):

    if way == 'divRank':
        way = 1
    else:
        way = 0

    # 得到该标签下所有块
    f = open(unicode(blockDir + news + '/' + label + '.txt', 'utf8'), 'r')
    blocks = []
    while True:
        n = f.readline()  # 第一行记录了下面几个句子是一个块
        if len(n) == 0:
            break
        n = int(n.strip())
        if n == 0:
            continue
        block = []
        for i in range(0, n):
            nums = f.readline()
            nums = nums.strip().split()
            content = f.readline().strip()
            words = segmentor.segment(content)
            word_vec_list = []
            for word in words:
                if word in model:
                    word_vec_list.append(model[word])
            sent = Sent(nums[0], nums[1], nums[2], nums[3], nums[4], content, mean_vec(word_vec_list))
            block.append(sent)
        blocks.append(block)
    f.close()

    blockcnt = len(blocks)

    # Rank部分

    unipai = [1 / float(blockcnt) for i in range(0, blockcnt)]
    unipai = mat(unipai)  # 1*blockcnt维矩阵
    pai = copy.deepcopy(unipai)  # 每个块的初始得分

    # 根据相似度，计算初始的转移概率矩阵p0
    p0 = []
    for i in range(0, blockcnt):
        tmp = [0.0 for j in range(0, blockcnt)]
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
    p0 = mat(p0)  # block*block维矩阵

    pt = copy.deepcopy(p0)  # 深复制，p0的值需要保留，pt每时刻都要变化

    iters = 200
    a = 0.8
    for i in range(0, iters):
        oldpai = copy.deepcopy(pai)

        # pageRank
        if way == 0:
            pai = a * oldpai * p0 + (1 - a) * unipai

        # divRank
        else:
            pai = a * oldpai * pt + (1 - a) * unipai
            # DivRank对pt的更新
            for u in range(0, blockcnt):
                for v in range(0, blockcnt):
                    pt[u, v] = p0[u, v] * pai[0, v]
                D = (pai * p0[u].T)[0, 0]
                if D != 0.0:
                    pt[u] = pt[u] / D

        # pai几乎不变，则停止迭代
        stop = True
        for j in range(0, blockcnt):
            if fabs(oldpai[0, j] - pai[0, j]) > 1e-10:
                stop = False
                break
        if stop:
            break
        if i == iters - 1:
            print 'Have not converged!'

    return blocks, pai


# 可调参数
way = 'divRank'
block_type = 'contain'
news = 'hpv疫苗'
label = '世界卫生组织'

blockDir = '../Sentence/assign/' + block_type + '/'
blocks, bscore = blockscore(blockDir, news, label, way)

# 按照rank分排序输出
l = len(blocks)
index = [i for i in range(0, l)]
for i in range(0, l):
    for j in range(i+1, l):
        if bscore[0, index[i]] < bscore[0, index[j]]:
            index[i], index[j] = index[j], index[i]

f = open('./see/' + label + '_' + block_type + '_' + way + '.txt', 'w')

for i in index:
    f.write(str(bscore[0, i]) + '\n')
    for sent in blocks[i]:
        f.write(sent.content)
    f.write('\n\n')
f.close()

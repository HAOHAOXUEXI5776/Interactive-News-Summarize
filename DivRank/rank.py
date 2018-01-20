#coding:utf-8

import gensim
from pyltp import Segmentor
from numpy import * #用于矩阵运算
import copy         #用于深复制
import os

qin = 1 #改成0是刘辉的路径，否则是秦文涛的路径
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
        self.newsid = _newsid        #该句所属新闻编号
        self.globalid = _globalid    #该句在该篇新闻的第几句
        self.paraid = _paraid        #该句在该篇新闻的第几段
        self.localid = _localid      #该句在所属段的第几句
        self.sentnum = _sentnum       #该句所在段有多少句
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


#计算两个块之间的相似度：取块间句子的最大相似度
def block_simi(block1, block2):
    max_simi = 0.0
    for sent1 in block1:
        for sent2 in block2:
            max_simi = max(max_simi, cos_similarity(sent1.vec, sent2.vec))
    return max_simi


def cut(P, i):
    #返回将P的第i行和第j列去掉的矩阵
    Q = copy.deepcopy(P)
    Q = delete(Q, i, axis = 1) #删除第i列
    Q = delete(Q, i, axis = 0)  #删除第i行
    return Q

#使用带吸收的pagerank
#返回news下label对应的块，以及它们降序的排分，以及对应的index
def blockscore(blockDir, news, label):

    #得到该标签下所有块
    f = open(unicode(blockDir+news+'/'+label+'.txt','utf8'), 'r')
    blocks = []
    while True:
        n = f.readline() #第一行记录了下面几个句子是一个块
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
                if word in model:
                    word_vec_list.append(model[word])
            sent = Sent(nums[0],nums[1],nums[2],nums[3],nums[4],content,mean_vec(word_vec_list))
            block.append(sent)
        blocks.append(block)
    f.close()

    blockcnt = len(blocks)

    #PageRank部分

    unipai = [1/float(blockcnt) for i in range(0, blockcnt)]
    unipai = mat(unipai) #1*blockcnt维矩阵
    pai = copy.deepcopy(unipai) #每个块的初始得分

    #根据相似度，计算初始的转移概率矩阵p0
    p0 = []
    for i in range(0, blockcnt):
        tmp = [0.0 for i in range(0, blockcnt)]
        p0.append(tmp)
    for i in range(0, blockcnt):
        for j in range(i+1, blockcnt):
            simi = block_simi(blocks[i], blocks[j])
            p0[i][j] = p0[j][i] = simi
    #对转移概率归一化
    for i in range(0, blockcnt):
        sumi = sum(p0[i])
        if sumi != 0.0:
            p0[i] = [p0[i][j]/sumi for j in range(0, blockcnt)]

    #写入图文件
    f = open(unicode('graph/'+label+'.txt', 'utf8'), 'w')
    for i in range(0, blockcnt):
        for j in range(0, blockcnt):
            f.write(str(p0[i][j])+' ')
        f.write('\n')
    f.close()


    p0 = mat(p0) #blockcnt*blockcnt维矩阵

    iters = 100
    a = 0.8
    for i in range(0, iters):
        oldpai = copy.deepcopy(pai)
        pai = a*oldpai*p0 + (1-a)*unipai #pageRank

        #pai几乎不变，则停止迭代
        stop = True
        for j in range(0, blockcnt):
            if fabs(oldpai[0,j]-pai[0,j]) > 1e-10:
                stop = False
                break
        if stop:
            break

    # 吸收部分

    # 选出pai值最大的那个
    maxpai, maxi = 0.0, 0
    for i in range(0, blockcnt):
        if pai[0, i] > maxpai:
            maxpai = pai[0, i]
            maxi = i
    score = [maxpai]
    index = [maxi]
    Q = cut(p0, maxi) #得到删除p0的第maxi行和第maxi列的矩阵
    for i in range(1, blockcnt):
        #迭代blockcnt - 1次，得到其余所有点的得分
        left = blockcnt - i
        N = (eye(left) - Q).I #eye(left)为left*left维单位矩阵，I为求逆
        onev = mat(ones(left)) #1*left维全1向量
        v = onev*N/left
        #找到v中最大的那个maxv，和它的原来的index-maxj
        maxv, maxj = 0.0, 0
        k, cutk = 0, 0
        for j in range(0, blockcnt):
            if j not in index:
                if v[0,k] > maxv:
                    maxv = v[0,k]
                    maxj = j
                    cutk = k
                k += 1
        score.append(maxv)
        index.append(maxj)
        Q = cut(Q, cutk)

    return blocks, score, index


#将outblock插入到inblock中，返回
def merge(outblock, inblock):
    #对于outblock的句子，如果与inblock中的每个句子的相似度都小于min_simi，则将其插入到inblock
    #因为inblock肯定是连贯的，不像论文中那样寻找inblock的一个空插进去，而是把句子插到末尾
    min_simi = 0.6
    for sent1 in outblock:
        ok = True
        for sent2 in inblock:
            if cos_similarity(sent1.vec, sent2.vec) >= min_simi:
                ok = False
                break
        if ok:
            inblock.append(sent1)
    return inblock

#根据标签的块，以及块的得分，得到关于该标签的综述
def summery(blocks, bscore):
    O = []
    l = len(blocks)
    #基数排序
    index = [i for i in range(0, l)]
    for i in range(0, l):
        for j in range(i+1, l):
            if bscore[index[i]] < bscore[index[j]]:
                index[i], index[j] = index[j], index[i]
    for i in range(0, l):
        curi = index[i]
        max_simi = 0.0
        for block in O:
            if block_simi(block, blocks[curi]) > max_simi:
                max_simi = block_simi(block, blocks[curi])
                most_simi_block = block
        if max_simi > 0.4:
            most_simi_block = merge(blocks[curi], most_simi_block)
        else:
            O.append(blocks[curi])

    return O

blockDir = '../Sentence/assign/contain/'
# blockDir = '../Sentence/assign/word2vec/'
labelDir = '../Sentence/label/'
outDir = 'blockscore/'

news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']
news_name = ['hpv疫苗']
for news in news_name:
    print news
    f = open(unicode(labelDir+news+'/label.txt', 'utf8'), 'r')
    labels = [line.strip().replace('+', '') for line in f]
    f.close()
    for label in labels:
        print label
        blocks, bscore, index = blockscore(blockDir, news, label)

        path = outDir+news
        if not os.path.exists(unicode(path, 'utf8')):
            os.mkdir(unicode(path, 'utf8'))

        f = open(unicode(path+'/'+label+'.txt', 'utf8'), 'w')
        blockcnt = len(blocks)
        for i in range(0, blockcnt):
            curi = index[i]
            f.write(str(bscore[curi])+'\n')
            for sent in blocks[curi]:
                f.write(sent.content+'\n')
            f.write('\n\n')
        f.close()

        '''
        O = summery(blocks, bscore)

        f = open(unicode(path+'/'+label+'_summary.txt', 'utf8'), 'w')
        for block in O:
            for sent in block:
                f.write(sent.content+'\n')
            f.write('\n')
        f.close()
        '''

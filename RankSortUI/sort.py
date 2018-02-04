# coding: utf-8

import gensim
from pyltp import Segmentor
import os
from math import *


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

def getTopicSum(news, label, std, model, stoplist, segmentor):
    #对新闻news的label生成std-40~std+40字数的综述，结果放在outDir+news+'/'+label+'.txt'文件里
    outDir = 'topic_sum/'
    print news
    path = outDir + news
    if not os.path.exists(unicode(path, 'utf8')):
        os.mkdir(unicode(path, 'utf8'))

    # 读入所有的标题,计算其向量置于title中
    title = []
    f = open(unicode('../Sentence/sentence/' + news + '/title.txt', 'utf8'), 'r')
    for line in f:
        words = segmentor.segment(line.strip())
        word_vec_list = []
        for word in words:
            if word not in stoplist and word in model:
                word_vec_list.append(model[word])
        title.append(mean_vec(word_vec_list))
    f.close()

    print label
    # 读取排序后的块
    blocks = []  # 记录该标签对应的块
    f = open(unicode('blockscore/' + news + '/' + label + '.txt', 'utf8'), 'r')
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
    blocklen = []
    for block in blocks:
        s = 0
        for sent in block:
            s += len(sent.content) / 3.0
        blocklen.append(s)
    # 选择blocks中的若干块，使得其字数在于530~580之间，如果找不到，则放松范围
    least = std - 40
    most = std + 40
    tol, end_block = 0, 0
    while tol < std and end_block < blockcnt:
        ttol = tol + blocklen[end_block]
        if ttol < least:
            tol = ttol
            end_block += 1
        elif least <= ttol <= most:
            tol = ttol
            end_block += 1
            break
        elif ttol > most:
            # 说明之前的字数少于least，加了这一个就超了most
            l, r = least - tol, most - tol
            nice = -1
            for i in range(end_block + 1, blockcnt):
                if l <= blocklen[i] <= r:
                    nice = i
                    break
            if nice == -1:
                # 往后找不到满足的，则找下一个
                tol += blocklen[end_block]
                end_block += 1
                break
            else:
                # 将第nice个作为下一个
                tol += blocklen[nice]
                blocks[nice], blocks[end_block] = blocks[end_block], blocks[nice]
                end_block += 1
                break
    assert end_block != 0
    # 按照标题的相似度将第0~endblock-1块分为几类
    print 'tol=', tol
    cluster = []
    use = [0 for i in range(0, end_block)]
    for i in range(0, end_block):
        if use[i] == 1:
            continue
        newid_i = blocks[i][0].newsid - 1
        tcluster = [blocks[i]]
        use[i] = 1
        for j in range(i + 1, end_block):
            newid_j = blocks[j][0].newsid - 1
            if use[j] == 0 and cos_similarity(title[newid_i], title[newid_j]) > 0.6:
                tcluster.append(blocks[j])
                use[j] = 1
        cluster.append(tcluster)
    f = open(unicode(outDir + news + '/' + label + '.txt', 'utf8'), 'w')
    # 每个类进行排序
    for tcluster in cluster:
        l = len(tcluster)
        sort = [i for i in range(0, l)]
        # 块在全文越靠前的位置，在段越靠前的位置，越要排到前头
        # 若位置因素影响不大，则考虑时间因素，新闻标号越小，发生的时间越晚，越往后排
        for i in range(0, l):
            for j in range(i + 1, l):
                senti, sentj = tcluster[sort[i]][0], tcluster[sort[j]][0]
                if senti.globalid > sentj.globalid or \
                    (senti.globalid == sentj.globalid and senti.localid > sentj.localid) or \
                    (senti.globalid == sentj.globalid and senti.localid == sentj.localid and senti.newsid < sentj.newsid):
                    sort[i], sort[j] = sort[j], sort[i]
        for i in range(0, l):
            for sent in tcluster[sort[i]]:
                f.write(sent.content)
            f.write('\n')
    f.close()


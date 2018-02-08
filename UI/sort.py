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
    vec_size = 100
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
    outDir = 'topic_sumtmp/'
    print news
    path = outDir + news
    if not os.path.exists(path):
        os.mkdir(path)

    print label
    # 读取排序后的块
    blocks = []  # 记录该标签对应的块
    f = open('blockscoretmp/' + news + '/' + label + '.txt', 'r')
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
    tollen = 0
    for block in blocks:
        s = 0
        for sent in block:
            s += len(sent.content) / 3.0
        tollen += s

    if tollen < std:
        #把块全部输出
        f = open(outDir + news + '/' + label + '.txt', 'w')
        for block in blocks:
            for sent in block:
                f.write(sent.content)
            f.write('\n')
        f.close()
    else:
        #最naive的方式
        curtol = 0
        f = open(outDir + news + '/' + label + '.txt', 'w')
        for block in blocks:
            for sent in block:
                tmpsent = sent.content.split('。')
                for tmp in tmpsent:
                    if tmp == '':
                        continue
                    curtol += len(tmp+'。')/3
                    f.write(tmp+'。')
                    if curtol > std:
                        break
            f.write('\n')
            if curtol > std:
                break
        f.close()

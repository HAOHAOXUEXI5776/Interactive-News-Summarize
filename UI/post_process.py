# coding:utf-8

# 对生成的summary进行后期处理，并选择好的标签生成最后的综述
# 后期处理包括删除块之前的报道信息，块一开始的连词

import gensim
from pyltp import Segmentor
import re
from math import sqrt
import codecs

# 将块开头的报道信息删去
def process(blk):
    blk = blk.decode('utf-8')
    pattern = r'[^腾通](电|讯)(（[^（）]*）|\([^\(\)]*\))'.decode('utf-8')
    matched = re.search(pattern, blk)
    if matched:
        match_str = matched.group()
        idx = blk.index(match_str) + len(match_str)
        blk = blk[idx:]
    pattern = r'([\w]日(电|讯)|新浪.{2}讯)'.decode('utf-8')
    matched = re.search(pattern, blk)
    if matched:
        match_str = matched.group()
        idx = blk.index(match_str) + len(match_str)
        blk = blk[idx:]
    pattern = r'【[^【】]*】|\[[^\[\]]*\]'.decode('utf-8')
    matched = re.search(pattern, blk)
    if matched:
        match_str = matched.group()
        idx = blk.index(match_str)
        if idx < 1:
            idx = idx + len(match_str)
            blk = blk[idx:]
    return blk.encode('utf-8')


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


def check_repeat(blocks, blk, model, stopword, segmentor):
    sim_threshold = 0.97  # 相似度大于此值的块不再被选入
    blk_words = segmentor.segment(blk)
    blk_vec_list = []
    for wd in blk_words:
        if wd not in stopword and wd in model:
            blk_vec_list.append(model[wd])
    blk_vec = mean_vec(blk_vec_list)
    for block in blocks:
        block_words = segmentor.segment(block)
        block_vec_list = []
        for wd in block_words:
            if wd not in stopword and wd in model:
                block_vec_list.append(model[wd])
        block_vec = mean_vec(block_vec_list)
        if cos_similarity(blk_vec, block_vec) > sim_threshold:
            print 'sim\n'
            print blk
            print block
            return False
    return True


def getSum(news, labels, model, stopword, segmentor):
    sum_dir = './topic_sumtmp/'
    out_dir = './sumtmp/'
    f_sum = open(out_dir + news + '.txt', 'w')

    #解决闹人的字体错误
    #但我仍然不知道是什么原因
    import sys
    default_encoding = 'utf-8'
    if sys.getdefaultencoding() != default_encoding:
        reload(sys)
        sys.setdefaultencoding(default_encoding)

    for label in labels:
        f_label_sum = open(sum_dir + news + '/' + label + '.txt', 'r')
        blocks = []
        for blk in f_label_sum:
            blk = process(blk)
            if check_repeat(blocks, blk, model, stopword, segmentor):
                blocks.append(blk)
        f_label_sum.close()
        cur_len = 0
        for blk in blocks:
            cur_len += len(blk.decode('utf-8'))
        f_sum.write('【' + label + '】\n')
        for blk in blocks:
            f_sum.write(blk)
        f_sum.write('\n')
    f_sum.close()

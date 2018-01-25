# coding:utf-8

# 对生成的summary进行后期处理，并选择好的标签生成最后的综述
# 后期处理包括删除块之前的报道信息，块一开始的连词

import gensim
from pyltp import Segmentor
import re
from math import sqrt

qin = 0  # 改成0是刘辉的路径，否则是秦文涛的路径
segmentor = Segmentor()
if qin == 1:
    segmentor.load('D:/coding/Python2.7/ltp_data_v3.4.0/cws.model')
    model = gensim.models.Word2Vec.load('../Sentence/model_qin')
else:
    segmentor.load('/Users/liuhui/Desktop/实验室/LTP/ltp_data_v3.4.0/cws.model')
    model = gensim.models.Word2Vec.load('../Sentence/model')
vec_size = 100

stopword = {}
f = open('../stopword.txt', 'r')
for line in f:
    word = line.strip()
    stopword[word] = 1
f.close()

label_dir = '../Sentence/label/'
sum_dir = './topic_sum/'
out_dir = './sum/'
label_num = 4  # 选取前几个标签构成综述
sim_threshold = 0.97  # 相似度大于此值的块不再被选入
least = 200  # 标签下的最小长度

news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']
"""
news_name = ['九寨沟7.0级地震']
"""


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


def check_repeat(blocks, blk):
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


def main():
    for news in news_name:
        labels = []
        f_label = open(unicode(label_dir + news + '/label.txt', 'utf8'), 'r')
        for label in f_label:
            label = label.strip().replace('+', '')
            labels.append(label)
        f_label.close()

        f_sum = open(unicode(out_dir + news + '.txt', 'utf8'), 'w')
        label_cnt = 0
        for label in labels:
            f_label_sum = open(unicode(sum_dir + news + '/' + label + '.txt', 'utf8'), 'r')
            blocks = []
            for blk in f_label_sum:
                blk = process(blk)
                if check_repeat(blocks, blk):
                    blocks.append(blk)
            f_label_sum.close()
            cur_len = 0
            for blk in blocks:
                cur_len += len(blk.decode('utf-8'))
            if cur_len >= least:
                f_sum.write('【' + label + '】\n')
                for blk in blocks:
                    f_sum.write(blk)
                f_sum.write('\n')
                label_cnt += 1
            if label_cnt == label_num:
                break

        f_sum.close()


if __name__ == '__main__':
    main()

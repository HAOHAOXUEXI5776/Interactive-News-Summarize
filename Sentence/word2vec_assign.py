# coding:utf-8

# 使用训练好的word2vec模型，计算每个标签的向量与每个句子的向量，从而得到余弦相似度
# 如果相似度超过一定的阈值，则将该句和该句的前一句、后一句（如果在同一段中）划分到标签下


from math import sqrt
from pyltp import Segmentor
import gensim
import os

# 加载word2vec模型
model = gensim.models.Word2Vec.load('model')
vec_size = 100

# 加载分词模型
segmentor = Segmentor()
# segmentor.load('/Users/liuhui/Desktop/实验室/LTP/ltp_data_v3.4.0/cws.model')
segmentor.load('D:/coding/Python2.7/ltp_data_v3.4.0/cws.model')

# 相似度超过此值的都会分配到对应标签下
gate = 0.6
# 如果在gate下没有得到的句子数小于10，选择下面的gate1
gate_1 = 0.4


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


# 句子类
class Sentence:

    def __init__(self, content, news_idx, sen_idx, para_idx, para_off, para_size, vec):
        self.content = content
        self.news_idx = news_idx
        self.sen_idx = sen_idx
        self.para_idx = para_idx
        self.para_off = para_off
        self.para_size = para_size
        self.vec = vec  # 该句话的向量表示


news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

for news in news_name:

    print news

    # 得到所有标签
    label_list = []
    f = open('label/' + news + '/label.txt', 'r')
    for line in f:
        label_list.append(line.strip())
    f.close()

    # 得到所有标签的向量表示
    label_vec_list = []
    for label in label_list:
        label = label.split('+')
        word_vec_list = []
        for word in label:
            if word in model:
                word_vec_list.append(model[word])
        label_vec_list.append(mean_vec(word_vec_list))

    # 读取该新闻的所有句子，得到句子的向量表示
    sentence_list = []
    f = open('sentence/' + news + '/sentence.txt', 'r')
    while True:
        info = f.readline()
        if len(info) < 2:
            break
        info = info.strip().split()
        sen = f.readline().strip()
        sen_cut = segmentor.segment(sen)
        word_vec_list = []
        for word in sen_cut:
            if word in model:
                word_vec_list.append(model[word])
        sen_vec = mean_vec(word_vec_list)
        sentence_list.append(Sentence(sen, info[0], info[1], info[2], info[3], info[4], sen_vec))
    f.close()

    # 给每一个标签分配句子
    for i, label in enumerate(label_list):
        sen_assign = []  # 存储已分配句子的编号
        for j, sen in enumerate(sentence_list):
            cur_sim = cos_similarity(label_vec_list[i], sen.vec)
            if cur_sim < gate:
                continue
            if j > 0 and sentence_list[j - 1].para_idx == sen.para_idx \
                     and sentence_list[j - 1].news_idx == sen.news_idx and j - 1 not in sen_assign:
                sen_assign.append(j - 1)
            if j not in sen_assign:
                sen_assign.append(j)
            if j < len(sentence_list) - 1 and sentence_list[j + 1].para_idx == sen.para_idx \
                and sentence_list[j + 1].news_idx == sen.news_idx and j + 1 not in sen_assign:
                sen_assign.append(j + 1)
        if len(sen_assign) < 10:
            for j, sen in enumerate(sentence_list):
                cur_sim = cos_similarity(label_vec_list[i], sen.vec)
                if cur_sim < gate1:
                    continue
                if j > 0 and sentence_list[j - 1].para_idx == sen.para_idx \
                         and sentence_list[j - 1].news_idx == sen.news_idx and j - 1 not in sen_assign:
                    sen_assign.append(j - 1)
                if j not in sen_assign:
                    sen_assign.append(j)
                if j < len(sentence_list) - 1 and sentence_list[j + 1].para_idx == sen.para_idx \
                    and sentence_list[j + 1].news_idx == sen.news_idx and j + 1 not in sen_assign:
                    sen_assign.append(j + 1)
        path = 'assign/word2vec/' + news
        if not os.path.exists(path):
            os.mkdir(path)
        f = open(path + '/' + label.replace('+', '') + '.txt', 'w')
        f.write(str(len(sen_assign))+'\n')
        for j in sen_assign:
            f.write(sentence_list[j].news_idx + ' ' + sentence_list[j].sen_idx + ' ' + sentence_list[j].para_idx + ' '
                    + sentence_list[j].para_off + ' ' + sentence_list[j].para_size + ' '
                    + str(round(cos_similarity(label_vec_list[i], sentence_list[j].vec), 3)) + '\n')
            f.write(sentence_list[j].content + '\n')
        f.close()

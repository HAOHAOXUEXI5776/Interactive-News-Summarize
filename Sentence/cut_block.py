# coding:utf-8

# 使用TextTiling算法将原新闻分段，分为以下三步
# 1.分句与分词。
# 2.两句话中间称作一个gap，为每个gap计算两侧的文本的相似度，计算完成后将相似度与周围gap的相似度平滑
# 3.根据每个gap的相似度以及周围的gap的相似度，计算该gap的depth score，最后选取depth score大于s - σ的gap作为分割点

from math import sqrt
from pyltp import Segmentor
import matplotlib.pyplot as plt
import gensim

qin = 0  # 改成0是刘辉的路径，否则是秦文涛的路径
window = 50  # 考虑一个gap前后50个词（包括标点，停用词），如果gap前后不足50词，不作为候选gap
vec_space = 2  # 相似度计算方法，0表示使用tf，1表示使用tf-idf，2表示使用word2vec平均，3表示使用tf-idf对word2vec加权平均
smooth_window = 2  # 对gap的similarity平滑时，只考虑左右相邻点
smooth_depth = 1  # 平滑深度

"""
news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']
"""
news_name = ['hpv疫苗']

# 加载分词模型，word2vec模型
segmentor = Segmentor()
if qin == 1:
    segmentor.load('D:/coding/Python2.7/ltp_data_v3.4.0/cws.model')
    model = gensim.models.Word2Vec.load('model_qin')
else:
    segmentor.load('/Users/liuhui/Desktop/实验室/LTP/ltp_data_v3.4.0/cws.model')
    model = gensim.models.Word2Vec.load('model')

# 获得停用词
stopwords = []
f = open('../stopword.txt', 'r')
for line in f:
    line = line.strip()
    if line not in stopwords:
        stopwords.append(line)


class Sentence:

    def __init__(self, content, news_idx, sen_idx, para_idx, para_off, para_size):
        self.content = content
        self.news_idx = news_idx
        self.sen_idx = sen_idx
        self.para_idx = para_idx
        self.para_off = para_off
        self.para_size = para_size
        self.word_off = 0       # 这句话在文章的词序列中的偏移


class Gap:
    # id为gap左侧的第一个句子编号，left，right记录左右文本
    def __init__(self, idx, left, right, similarity=0, depth_score=0):
        self.idx = idx
        self.left = left
        self.right = right
        self.similarity = similarity
        self.depth_score = depth_score


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
def mean_vec(vec_list, vec_size):
    if len(vec_list) == 0:
        return [0.0 for k in range(0, vec_size)]
    result = [0.0 for k in range(0, len(vec_list[0]))]
    for vec in vec_list:
        for k in range(0, len(result)):
            result[k] += vec[k]
    for k in range(0, len(result)):
        result[k] /= len(vec_list)
    return result


# TextTiling算法
def text_titling(news, news_id, sen_list):

    # 得到词典，词-idx映射关系，文章的词序列
    word_list = []
    dic = []
    for i, sentence in enumerate(sen_list):
        sen_list[i].word_off = len(word_list)
        words = segmentor.segment(sentence.content)
        for word in words:
            word_list.append(word)
            if word not in word_list:
                dic.append(word)
    idx2word = {}
    word2idx = {}
    for i, word in enumerate(dic):
        idx2word[i] = word
        word2idx[word] = i

    # 得到gap（候选边界）列表
    gap_list = []
    for i, sentence in enumerate(sen_list):
        if i == 0:
            continue
        left_word_num = sentence.word_off
        right_word_num = len(word_list) - left_word_num
        # 如果当前边界左右词的个数不能满足window，不作为gap
        if left_word_num < window or right_word_num < window:
            continue
        gap_list.append(Gap(i, word_list[sentence.word_off - window:sentence.word_off],
                            word_list[sentence.word_off:sentence.word_off + window]))

    # 计算gap的similarity值
    for i, gap in enumerate(gap_list):
        vec_list = []
        for word in gap.left:
            if word in stopwords or word not in model:
                continue
            vec_list.append(model[word])
        vec_left = mean_vec(vec_list, 100)
        vec_list = []
        for word in gap.right:
            if word in stopwords or word not in model:
                continue
            vec_list.append(model[word])
        vec_right = mean_vec(vec_list, 100)
        gap.similarity = cos_similarity(vec_left, vec_right)

    if news_id == 1:
        x, y = [], []
        for gap in gap_list:
            x.append(gap.idx)
            y.append(gap.similarity)
            print gap.idx, round(gap.similarity, 3)


def main():
    for news in news_name:
        f = open('./sentence/' + news + '/sentence.txt', 'r')
        sen_list = []  # 用来保存当前新闻的所有句子
        cur_news_id = 1  # 当前新闻的编号
        while True:
            info = f.readline()
            if len(info) < 2:
                break
            info = info.strip().split()
            sen = f.readline().strip()
            cur_sen = Sentence(sen, info[0], info[1], info[2], info[3], info[4])
            if int(info[0]) == cur_news_id:
                sen_list.append(cur_sen)
            else:
                text_titling(news, cur_news_id, sen_list)
                cur_news_id += 1
                sen_list = []
        f.close()


if __name__ == '__main__':
    main()
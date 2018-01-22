# coding:utf-8

# 使用TextTiling算法将原新闻分段，分为以下三步
# 1.分句与分词。
# 2.两句话中间称作一个gap，为每个gap计算两侧的文本的相似度，计算完成后将相似度与周围gap的相似度平滑
# 3.根据每个gap的相似度以及周围的gap的相似度，计算该gap的depth score，最后选取depth score大于s - 3σ的gap作为分割点

from math import sqrt, pow
from pyltp import Segmentor
import os
import matplotlib.pyplot as plt
import gensim

qin = 0        # 改成0是刘辉的路径，否则是秦文涛的路径
window = 25    # 考虑一个gap前后50个词（包括标点，停用词），如果gap前后不足50词，不作为候选gap
sim_kind = 0   # 相似度计算方法，0表示使用tf，1表示使用word2vec平均
smooth_window = 2  # 对gap的similarity平滑时，只考虑左右相邻点
smooth_depth = 0   # 平滑深度，使用平滑策略导致块过大，效果也不理想，所有当前没有使用


news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

out_dir = './block/'

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
f.close()


class Sentence:
    # word_off表示这句话在文章的词序列中的偏移
    def __init__(self, content, news_idx, sen_idx, para_idx, para_off, para_size):
        self.content = content
        self.news_idx = news_idx
        self.sen_idx = sen_idx
        self.para_idx = para_idx
        self.para_off = para_off
        self.para_size = para_size
        self.word_off = 0


class Gap:
    # idx为gap左侧的第一个句子编号，left，right记录左右文本
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
def text_titling(sen_list, f_out):

    # 得到词典，词-idx映射关系，文章的词序列
    word_list = []
    dic = []
    for i, sentence in enumerate(sen_list):
        sen_list[i].word_off = len(word_list)
        words = segmentor.segment(sentence.content)
        for word in words:
            word_list.append(word)
            if word not in dic:
                dic.append(word)
    word2idx = {}
    for i, word in enumerate(dic):
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
        # 注意这里gap的idx为i，即gap左侧句子的编号（同时也是gap右侧句子在sen_list中的序号）
        gap_list.append(Gap(i, word_list[sentence.word_off - window:sentence.word_off],
                            word_list[sentence.word_off:sentence.word_off + window]))

    # 计算gap的similarity值
    if sim_kind == 0:  # tf方法
        for i, gap in enumerate(gap_list):
            vec_left = [0.0 for k in range(0, len(dic))]
            vec_right = [0.0 for k in range(0, len(dic))]
            for word in gap.left:
                if word in stopwords:
                    continue
                vec_left[word2idx[word]] += 1
            for word in gap.right:
                if word in stopwords:
                    continue
                vec_right[word2idx[word]] += 1
            gap.similarity = cos_similarity(vec_left, vec_right)

    else:  # word2vec方法
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

    # 对sim进行平滑
    for t in range(0, smooth_depth):
        new_sim = [0.0 for i in range(0, len(gap_list))]
        for i, gap in enumerate(gap_list):
            smooth_num = 0.0
            new_sim[i] = 0
            for j in range(i - smooth_window/2, i + smooth_window/2 + 1):
                if j < 0 or j >= len(gap_list):
                    continue
                smooth_num += 1
                new_sim[i] += gap_list[j].similarity
            new_sim[i] /= smooth_num
        for i, gap in enumerate(gap_list):
            gap.similarity = new_sim[i]

    # 计算gap的depth_score
    valley_num = 0.0
    depth_score_ave = 0.0
    for i, gap in enumerate(gap_list):
        peak_left = 0.0   # 记录当前gap左侧的最近的峰值
        peak_right = 0.0  # 记录右侧峰值
        for j in range(i-1, -1, -1):
            if gap_list[j].similarity >= gap_list[j + 1].similarity:
                peak_left = gap_list[j].similarity
            else:
                break
        for j in range(i+1, len(gap_list)):
            if gap_list[j].similarity >= gap_list[j - 1].similarity:
                peak_right = gap_list[j].similarity
            else:
                break
        if peak_left >= gap.similarity and peak_right >= gap.similarity:
            gap.depth_score = peak_left + peak_right - 2 * gap.similarity
            depth_score_ave += gap.depth_score
            valley_num += 1
        else:
            gap.depth_score = -1.0  # -1表示这个gap不是谷底，不作为边界

    # 根据depth_score确定最终的边界
    boundary = []
    if valley_num != 0.0:
        depth_score_ave /= valley_num
        depth_score_dev = 0.0
        for i, gap in enumerate(gap_list):
            if gap.depth_score < 0.0:
                continue
            depth_score_dev += pow((gap.depth_score - depth_score_ave), 2)
        depth_score_dev = sqrt(depth_score_dev / valley_num)
        gate = max(depth_score_ave - 3 * depth_score_dev, 0.0)
        for i, gap in enumerate(gap_list):
            if gap.depth_score >= gate:
                boundary.append(gap.idx)
    boundary.append(len(sen_list))

    # 将块写入文件
    block_start = 0
    for block_end in boundary:
        f_out.write(str(block_end - block_start) + '\n')
        for i in range(block_start, block_end):
            sen = sen_list[i]
            f_out.write(sen.news_idx + ' ' + sen.sen_idx + ' ' + sen.para_idx + ' ' + sen.para_off + ' ' +
                        sen.para_size + '\n')
            f_out.write(sen.content + '\n')
        block_start = block_end

    """
    # 输出给定新闻的图形表示
    if news == 'hpv疫苗' and news_id == 100:
        x = []
        y = []
        for gap in gap_list:
            x.append(gap.idx)
            y.append(gap.similarity)
        plt.figure()
        plt.plot(x, y)
        for i in boundary:
            x = [i, i]
            y = [0.0, 1.0]
            plt.plot(x, y)
        plt.savefig('/Users/liuhui/Desktop/' + news + '_' + str(news_id))
    """
    return len(boundary)


def main():
    sum_sen_num = 0.0
    sum_blk_num = 0.0
    for news in news_name:
        cur_dir = out_dir + news + '/'
        if not os.path.exists(cur_dir):
            os.mkdir(cur_dir)
        cur_file = cur_dir + 'block.txt'
        f_out = open(cur_file, 'w')
        f_in = open('./sentence/' + news + '/sentence.txt', 'r')
        sen_num = 0.0       # 关于该事件的所有新闻的总句数
        block_num = 0.0     # 关于该事件的所有新闻的总块数
        sen_list = []  # 用来保存当前一篇新闻的所有句子
        cur_news_id = 1  # 当前新闻的编号
        while True:
            info = f_in.readline()
            if len(info) < 2:
                cur_blk_num = text_titling(sen_list, f_out)
                sen_num += len(sen_list)
                block_num += cur_blk_num
                break
            info = info.strip().split()
            sen = f_in.readline().strip()
            cur_sen = Sentence(sen, info[0], info[1], info[2], info[3], info[4])
            if int(info[0]) == cur_news_id:
                sen_list.append(cur_sen)
            else:
                cur_blk_num = text_titling(sen_list, f_out)
                sen_num += len(sen_list)
                block_num += cur_blk_num
                cur_news_id += 1
                sen_list = [cur_sen]
        f_in.close()
        f_out.close()
        print news, round(sen_num/block_num, 3)
        sum_sen_num += sen_num
        sum_blk_num += block_num
    print '总计', round(sum_sen_num/sum_blk_num, 3)


if __name__ == '__main__':
    main()

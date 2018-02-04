# coding:utf-8

# 最开始的方法，使用lda无监督学习，给每个候选标签在各lda主题下打分，选取得分高的标签(n-gram)，具体步骤如下：
#
# 1. 使用LDA得到主题-词分布，K = 10，iters = 100，learning_method = 'batch'，与计算特征时设置相同
#
# 2. 计算PMI(w,l) = log P(w|l)/P(w)，选取一个窗口，计算标签l出现时w出现的概率P(w|l)，P(w)使用词w出现频率
#
# 3. 计算score0(l,θ) = ∑ P(w|θ) * PMI(w,l)， P(w|θ)指主题-词分布，在第一步计算得到
#
# 4. 计算score(l,θi) = (1+μ/(K-1)) * score0(l,θi) - μ/(K-1) * ∑ score0(l, θj)，这一步是为了让每个主题下选择的标签不同
#
# 5. score(l) = max{score(l,θi)}，根据score(l)选出排名前20的标签，并计算P@5，P@10，P@20

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
import math
import sys

reload(sys)
sys.setdefaultencoding('utf8')

news_name = ['德国大选', '俄罗斯世界杯', '功守道', '九寨沟7.0级地震', '权力的游戏',
             '双十一购物节', '乌镇互联网大会', '战狼2', 'hpv疫苗', 'iPhone X',
             '李晨求婚范冰冰', '江歌刘鑫', '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园',
             '绝地求生 吃鸡', '英国脱欧', '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

news_dir = '../Ngrams/Processed/'
label_dir = '../Ngrams/feature_12cut/'
K = 10          # lda主题数
iters = 100     # lda迭代次数
window = 0      # pmi计算窗口大小的一半，设为0是为了突出2-gram，3-gram
miu = 0.5       # 计算score时的参数，值越大越强调不同topic之间选择标签的差异
repeat_num = 10 # 整个算法的重复次数，为了消除lda的随机不稳定性


# 读入分词后的文档集合，得到word-idx映射关系，通过lda得到topic-word分布
def lda(news, stopword):
    # 读入分词后的新闻
    doc_set = []
    news_file = open(news_dir + news + '/words.txt', 'r')
    news_content = news_file.readlines()
    for i in range(0, len(news_content), 2):
        doc_set.append(news_content[i].strip() + ' ' + news_content[i + 1].strip())
    news_file.close()
    docs = ''
    for doc in doc_set:
        docs += doc + ' '

    # 将分词后的新闻变成tf向量，同时去除停用词，去掉低频词
    tf_vectorizer = CountVectorizer(min_df=3, stop_words=stopword)
    tf = tf_vectorizer.fit_transform(doc_set)
    idx_word = tf_vectorizer.get_feature_names()  # 从id找到word
    word_idx = {}  # 从word找到id
    for idx, word in enumerate(idx_word):
        word_idx[word] = idx

    # LDA建模，返回两个分布
    model = LatentDirichletAllocation(n_components=K, max_iter=iters, learning_method='batch')
    model.fit_transform(tf)
    topic_word = model.components_ / model.components_.sum(axis=1)[:, np.newaxis]

    return topic_word, word_idx, idx_word, docs


# 读入标签
def read_label(news):
    labels = []
    signed_labels = []
    f = open(label_dir + news + '.txt', 'r')
    for line in f:
        line = line.strip().split()
        labels.append(line[0])
        if float(line[1]) > 1e-10:
            signed_labels.append(line[0])
    f.close()
    return labels, signed_labels


# 计算PMI
def compute_pmi(docs, word_idx, idx_word, labels):
    pmi = []  # pmi是一个二维数组，第i,j个元素表示一个i号label和j号word的pmi

    # 计算P(w)，即每个word出现的频率
    p_w = []
    for idx, word in enumerate(idx_word):
        w_cnt = docs.count(word, 0, len(docs))
        sum_cnt = len(docs)
        p_w.append(float(w_cnt) / float(sum_cnt))

    # 计算PMI(l,w)
    for i, label in enumerate(labels):
        l_w_cnt = [0 for j in range(0, len(idx_word))]  # label和word的共现次数
        label = label.replace('+', ' ')
        l_cnt = 0.0
        start_idx = 0
        while True:
            idx = docs.find(label, start_idx)
            if idx == -1:
                break
            co_words = []  # 记录在此处与label共现的word

            # 首先把label自己含有的word加进去
            for word in label.split():
                co_words.append(word)

            # 左侧
            left = docs[:idx]
            left_cnt = 0
            cur_end = len(left)
            while left_cnt < window:
                space = left.rfind(' ', 0, cur_end)
                if space == -1:
                    break
                if space + 1 < cur_end:
                    co_words.append(left[space + 1:cur_end])
                    left_cnt += 1
                cur_end = space

            # 右侧
            right = docs[idx + len(label):]
            right_cnt = 0
            cur_start = 0
            while right_cnt < window:
                space = right.find(' ', cur_start)
                if space == -1:
                    break
                if cur_start < space:
                    co_words.append(right[cur_start:space])
                    right_cnt += 1
                cur_start = space + 1
            start_idx = idx + 1

            l_cnt += 1
            for word in co_words:
                word = word.decode('utf-8')
                if word in word_idx:
                    l_w_cnt[word_idx[word]] += 1
        p_w_l = [0.0 for j in range(0, len(idx_word))]

        for j in range(0, len(idx_word)):
            if l_w_cnt[j] == 0:
                p_w_l[j] = 0.0
            else:
                p_w_l[j] = math.log((float(l_w_cnt[j]) / float(l_cnt)) / p_w[j])
        pmi.append(p_w_l)

    return pmi


# 根据LDA得到的主题-词分布以及标签-单词的PMI，计算每个标签在不同主题下的得分
def compute_score(topic_word, pmi):
    score0 = []
    l_label = len(pmi)
    l_topic = len(topic_word)
    l_word = len(topic_word[0])

    # 计算score0(l, θ) = ∑ P(w | θ) * PMI(w, l)
    for i in range(0, l_label):
        cur_score0 = [0.0 for j in range(0, l_topic)]
        for j in range(0, l_topic):
            for k in range(0, l_word):
                cur_score0[j] += topic_word[j][k] * pmi[i][k]
        score0.append(cur_score0)

    # 计算score(l,θi) = (1+μ/(K-1)) * score0(l,θi) - μ/(K-1) * ∑ score0(l, θj)
    score = [[0.0 for i in range(0, l_topic)] for j in range(0, l_label)]
    for i in range(0, l_label):
        for j in range(0, l_topic):
            for k in range(0, l_topic):
                score[i][j] -= score0[i][k]
            score[i][j] = (1 + miu / float(K - 1)) * score0[i][j] + miu / float(K - 1) * score[i][j]

    return score


# 根据score为每个主题选择标签
def choose_label(labels, score, signed_labels):
    score_l = [0.0 for i in range(0, len(labels))]
    l_label = len(labels)
    l_topic = len(score[0])
    for i in range(0, l_label):
        for j in range(0, l_topic):
            if score[i][j] > score_l[i]:
                score_l[i] = score[i][j]
    index = [i for i in range(0, l_label)]
    for i in range(0, l_label):
        for j in range(i + 1, l_label):
            if score_l[index[i]] < score_l[index[j]]:
                index[i], index[j] = index[j], index[i]
    p_5, p_10, p_20 = 0.0, 0.0, 0.0
    for i in range(0, 5):
        if labels[index[i]] in signed_labels:
            p_5 += 1
    p_5 /= 5
    for i in range(0, 10):
        if labels[index[i]] in signed_labels:
            p_10 += 1
    p_10 /= 10
    for i in range(0, 20):
        if labels[index[i]] in signed_labels:
            p_20 += 1
    p_20 /= 20
    return p_5, p_10, p_20


def main():
    # 从文件导入停用词表
    stopword = []
    stopword_file = open('../stopword.txt', 'r')
    for line in stopword_file:
        line = line.strip()
        if line not in stopword:
            stopword.append(line)
    stopword_file.close()

    P_5, P_10, P_20 = 0.0, 0.0, 0.0
    iter_cnt = 0
    for i in range(0, 5):
        print '第' + str(i + 1) + '次迭代：'
        for news in news_name:
            # 读入新闻，进行lda建模
            topic_word, word_idx, idx_word, docs = lda(news, stopword)

            # 读入标签，找到带标记的标签
            labels, signed_labels = read_label(news)

            # 计算不同label，word之间的pmi
            pmi = compute_pmi(docs, word_idx, idx_word, labels)

            # 计算每个label在不同主题下的分数
            score = compute_score(topic_word, pmi)

            # 输出结果并计算P@5，P@10，P@20
            p_5, p_10, p_20 = choose_label(labels, score, signed_labels)

            print news, p_5, p_10, p_20

            P_5 += p_5
            P_10 += p_10
            P_20 += p_20
            iter_cnt += 1
        print '\n'

    P_5 /= iter_cnt
    P_10 /= iter_cnt
    P_20 /= iter_cnt
    print 'result:', P_5, P_10, P_20


if __name__ == '__main__':
    main()

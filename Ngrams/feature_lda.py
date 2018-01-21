# coding:utf-8

# 将每个新闻事件下的新闻进行LDA建模，简化起见K值固定为10，得到doc-topic分布和topic-word分布，对每个ngram提取三个特征：
#
# lda_f1：该ngram能够表示LDA下某个topic的程度
# 计算方法：在每个topic下，计算该ngram的概率P，如果是unigram，P = P(unigram)，如果是2，3gram，P = ∑ P(unigram_i)，最后取一个最大
# 的概率作为lda_f1
#
# lda_f2：与该ngram相关的文档集合主题的紧凑性
# 计算方法：设包含该ngram的文档集合为C，统计C中出现的topic数目n，lda_f2 = 1/n
#
# lda_f3：该ngram的df
#
# 直观来看，好的ngram前两个特征应该比较大，第三个特征应该不是特别大也不是特别小

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np

newsName = ['德国大选', '俄罗斯世界杯', '功守道', '九寨沟7.0级地震', '权力的游戏',
            '双十一购物节', '乌镇互联网大会', '战狼2', 'hpv疫苗', 'iPhone X',
            '李晨求婚范冰冰', '江歌刘鑫', '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园',
            '绝地求生 吃鸡', '英国脱欧', '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

ori_dir = 'feature/'
out_dir = 'feature_lda/'
n_components = 10  # lda主题数
max_iter = 100  # lda迭代次数


# 从feature文件夹读入ngram，人工打分，原始特征
def read_feature(news):
    ngram = []
    score = []
    feature = []
    f = open(ori_dir + news + '.txt', 'r')
    for line in f:
        line = line.strip().split()
        ngram.append(line[0].split('+'))
        score.append(line[1])
        feature.append(line[2:])
    f.close()
    return ngram, score, feature


# LDA建模，返回doc-topic分布，topic-word分布，word和id的映射关系，分词后的文档集合
def lda(news):
    # 从文件导入停用词表
    stopword = []
    stopword_file = open('../stopword.txt', 'r')
    for line in stopword_file:
        line = line.strip()
        stopword.append(line)
    stopword_file.close()

    # 读入分词后的新闻
    doc_set = []
    news_file = open('Processed/' + news + '/words.txt', 'r')
    news_content = news_file.readlines()
    for i in range(0, len(news_content), 2):
        doc_set.append(news_content[i].strip() + ' ' + news_content[i + 1].strip())
    news_file.close()

    # 将分词后的新闻变成tf向量，同时去除停用词，去掉低频词
    tf_vectorizer = CountVectorizer(min_df=3, stop_words=stopword)
    tf = tf_vectorizer.fit_transform(doc_set)
    idx_word = tf_vectorizer.get_feature_names()  # 从id找到word
    word_idx = {}  # 从word找到id
    for idx, word in enumerate(idx_word):
        word_idx[word] = idx

    # LDA建模，返回两个分布
    model = LatentDirichletAllocation(n_components=n_components, max_iter=max_iter, learning_method='online', )
    doc_topic = model.fit_transform(tf)
    topic_word = model.components_ / model.components_.sum(axis=1)[:, np.newaxis]

    return doc_topic, topic_word, word_idx, doc_set


# 将特征归一化
def normalize(f):
    min_f = 1e20
    max_f = -1e20
    for fi in f:
        if fi < min_f:
            min_f = fi
        if fi > max_f:
            max_f = fi
    for i in range(0, len(f)):
        f[i] = (f[i] - min_f) / (max_f - min_f)
    return f


# 计算lda_f1
def compute_f1(ngram_list, topic_word, word_idx):
    lda_f1 = [0.0 for i in range(0, len(ngram_list))]

    # 依次考虑每个ngram
    for i, ngram in enumerate(ngram_list):
        idx = []  # 存放ngram中所含word编号
        for word in ngram:
            if word_idx.has_key(unicode(word, 'utf-8')):
                idx.append(word_idx[unicode(word, 'utf-8')])

        for topic in topic_word:
            cur_p = 0.0
            for word_id in idx:
                cur_p += topic[word_id]
            if cur_p > lda_f1[i]:
                lda_f1[i] = cur_p

    return normalize(lda_f1)


# 找出包含特定ngram的新闻集合
def find_related_doc(doc_set, ngram):
    ngram_doc_set = []
    ngram_content = ''
    for word in ngram:
        ngram_content += word + ' '
    ngram_content = ngram_content.strip()
    for i, doc in enumerate(doc_set):
        if ngram_content in doc:
            ngram_doc_set.append(i)
    return ngram_doc_set


# 计算lda_f2和lda_f3
def compute_f23(doc_set, ngram_list, doc_topic):
    lda_f2 = [0.0 for i in range(0, len(ngram_list))]
    lda_f3 = [0.0 for i in range(0, len(ngram_list))]

    # 选择概率最大的topic作为文档的topic
    doc_topic_most = []
    for doc in doc_topic:
        doc_topic_most.append(doc.argmax())

    # 依次考虑每个ngram
    for i, ngram in enumerate(ngram_list):
        ngram_doc_set = find_related_doc(doc_set, ngram)
        cur_topic_set = []
        for doc in ngram_doc_set:
            if doc_topic_most[doc] not in cur_topic_set:
                cur_topic_set.append(doc_topic_most[doc])
        lda_f2[i] = 1.0 / float(len(cur_topic_set))
        lda_f3[i] = float(len(ngram_doc_set))
    return normalize(lda_f2), normalize(lda_f3)


# 将新增的三个特征与原来的特征合并，写入out_dir文件夹
def write_feature(news, ngram, score, feature, lda_f1, lda_f2, lda_f3):
    l = len(ngram)
    f = open(out_dir + news + '.txt', 'w')
    for i in range(0, l):
        nl = len(ngram[i])
        f.write(ngram[i][0])
        for j in range(1, nl):
            f.write('+' + str(ngram[i][j]))
        f.write(' ' + str(score[i]))
        for fea in feature[i]:
            f.write(' ' + str(fea))
        f.write(' ' + str(lda_f1[i]))
        f.write(' ' + str(lda_f2[i]))
        f.write(' ' + str(lda_f3[i]))
        f.write('\n')
    f.close()


def main():
    for news in newsName:
        print news
        ngram, score, feature = read_feature(news)
        doc_topic, topic_word, word_idx, doc_set = lda(news)
        lda_f1 = compute_f1(ngram, topic_word, word_idx)
        lda_f2, lda_f3 = compute_f23(doc_set, ngram, doc_topic)
        write_feature(news, ngram, score, feature, lda_f1, lda_f2, lda_f3)


if __name__ == '__main__':
    main()

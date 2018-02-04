# coding:utf-8

# 使用TextRank算法从候选标签中选取label。
# 原算法只针对unigram，倾向于选择出现频次高的词作为关键词，所以如果把bi-gram,3-gram和uni-gram等同处理，则会因为出现频次低而被
# unigram比下去，所以选择如下方式：
# 先计算单个词的投票（包括unigram以及bi-gram，3-gram中出现的单个词），对于bi-gram和3-gram，再把两个顶点合并，得到最终的图。

from numpy import *  # 用于矩阵运算
import copy  # 用于深复制

news_name = ['德国大选', '俄罗斯世界杯', '功守道', '九寨沟7.0级地震', '权力的游戏',
             '双十一购物节', '乌镇互联网大会', '战狼2', 'hpv疫苗', 'iPhone X',
             '李晨求婚范冰冰', '江歌刘鑫', '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园',
             '绝地求生 吃鸡', '英国脱欧', '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

news_dir = '../Ngrams/Processed/'  # 分词后的新闻
label_dir = '../Ngrams/feature_12cut/'  # 候选label
window = 5  # 计入共现的窗口大小

# 从文件导入停用词表
stopword = []
stopword_file = open('../stopword.txt', 'r')
for stop_line in stopword_file:
    stop_line = stop_line.strip()
    if stop_line not in stopword:
        stopword.append(stop_line)
stopword_file.close()


# 读入候选标签，并根据标签得到词典
def read_labels(news):
    labels = []
    signed_labels = []
    f = open(label_dir + news + '.txt', 'r')
    for line in f:
        line = line.strip().split()
        labels.append(line[0])
        if float(line[1]) > 1e-10:
            signed_labels.append(line[0])
    f.close()
    word_list = []
    for label in labels:
        words = label.split('+')
        for word in words:
            if word not in stopword and word not in word_list:
                word_list.append(word)
    word_idx = {}
    for i, word in enumerate(word_list):
        word_idx[word] = i
    return labels, signed_labels, word_list, word_idx


# 根据共现关系构建推荐关系图
def build_graph(news, labels, word_list, word_idx):
    # 读入分词后新闻
    content = []
    f = open(news_dir + news + '/words.txt', 'r')
    for line in f:
        line = line.strip().split()
        content.append(line)
    f.close()

    # 构建单个词的投票图
    word_graph = [[0 for i in range(0, len(word_list))] for j in range(0, len(word_list))]
    for sentence in content:
        for i, word in enumerate(sentence):
            if word in word_list:
                for j in range(max(i - window, 0), i):
                    if sentence[j] in word_list:
                        word_graph[word_idx[word]][word_idx[sentence[j]]] += 1
                for j in range(i + 1, min(i + window + 1, len(sentence))):
                    if sentence[j] in word_list:
                        word_graph[word_idx[word]][word_idx[sentence[j]]] += 1

    # 由单个词的投票图计算label之间的投票图
    graph = [[0.0 for i in range(0, len(labels))] for j in range(0, len(labels))]
    middle = []
    for label in labels:
        cur_label = [0 for i in range(0, len(word_list))]
        words = label.split('+')
        for word in words:
            if word not in word_list:
                continue
            cur_idx = word_idx[word]
            for k in range(0, len(word_list)):
                cur_label[k] += word_graph[cur_idx][k]
        middle.append(cur_label)
    for i, label in enumerate(labels):
        words = label.split('+')
        for word in words:
            if word not in word_list:
                continue
            cur_idx = word_idx[word]
            for k in range(0, len(labels)):
                graph[k][i] += middle[k][cur_idx]
    return graph


# 现在得到了标签推荐图，使用page_rank算法得到标签排名
def page_rank(graph, labels):
    n = len(graph)
    unipai = [1.0 / n for i in range(0, n)]
    unipai = mat(unipai)
    pai = copy.deepcopy(unipai)

    # 对标签推荐图归一化
    for i in range(0, n):
        sumi = sum(graph[i])
        if sumi != 0.0:
            graph[i] = [graph[i][j] / sumi for j in range(0, n)]
    graph = mat(graph)

    iters = 100
    a = 0.85
    for i in range(0, iters):
        old_pai = copy.deepcopy(pai)
        pai = a * old_pai * graph + (1 - a) * unipai  # pageRank
        # pai几乎不变，则停止迭代
        stop = True
        for j in range(0, n):
            if fabs(old_pai[0, j] - pai[0, j]) > 1e-10:
                stop = False
                break
        if stop:
            break
        if i == iters - 1:
            print 'fail!'
    score = [pai[0, j] for j in range(0, n)]
    index = [i for i in range(0, n)]
    for i in range(0, n):
        for j in range(i + 1, n):
            if score[index[i]] < score[index[j]]:
                index[i], index[j] = index[j], index[i]
    return index


def main():
    P_5, P_10, P_20 = 0.0, 0.0, 0.0
    for news in news_name:
        labels, signed_labels, word_list, word_idx = read_labels(news)
        graph = build_graph(news, labels, word_list, word_idx)
        rank_idx = page_rank(graph, labels)
        p_5, p_10, p_20 = 0.0, 0.0, 0.0
        for i in range(0, 5):
            if labels[rank_idx[i]] in signed_labels:
                p_5 += 1
        for i in range(0, 10):
            if labels[rank_idx[i]] in signed_labels:
                p_10 += 1
        for i in range(0, 20):
            if labels[rank_idx[i]] in signed_labels:
                p_20 += 1
        p_5 /= 5
        p_10 /= 10
        p_20 /= 20
        P_5 += p_5
        P_10 += p_10
        P_20 += p_20
        print news, p_5, p_10, p_20
    P_5 /= len(news_name)
    P_10 /= len(news_name)
    P_20 /= len(news_name)
    print 'In total', P_5, P_10, P_20


if __name__ == '__main__':
    main()

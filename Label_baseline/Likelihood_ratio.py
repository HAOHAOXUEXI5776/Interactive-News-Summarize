# coding:utf-8

# 使用likelihood ratio方法提取label
# 计算所有候选2-gram和3-gram的-2logλ并排序，前20个就是最终得到的标签

import math


news_name = ['德国大选', '俄罗斯世界杯', '功守道', '九寨沟7.0级地震', '权力的游戏',
             '双十一购物节', '乌镇互联网大会', '战狼2', 'hpv疫苗', 'iPhone X',
             '李晨求婚范冰冰', '江歌刘鑫', '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园',
             '绝地求生 吃鸡', '英国脱欧', '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']


news_dir = '../Ngrams/Processed/'  # 分词后的新闻
label_dir = '../Ngrams/feature_12cut/'  # 候选label


# 读入标签
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
    return labels, signed_labels


# 读入分词后的新闻
def read_news(news):
    content = []
    f = open(news_dir + news + '/words.txt', 'r')
    for line in f:
        line = line.strip().split()
        content.append(line)
    f.close()
    return content


def logL(p, k, n):
    if p < 1e-10:
        return - k * 1e20
    elif p > 1 - 1e-10:
        return -(n - k) * 1e20
    return k * math.log(p) + (n - k) * math.log(1 - p)


def logL2(P, K):
    result = 0.0
    for i in range(0, 4):
        if P[i] < 1e-20:
            result += K[i] * (-1e20)
        else:
            result += K[i] * math.log(P[i])
    return result


# 计算2-gram的likelihood ratio
def calculate_2_gram(content, A, B):
    k1, k2, k3, k4 = 0.0, 0.0, 0.0, 0.0
    for words in content:
        for i in range(0, len(words) - 1):
            if words[i] == A and words[i + 1] == B:
                k1 += 1
            elif words[i] != A and words[i + 1] == B:
                k2 += 1
            elif words[i] == A and words[i + 1] != B:
                k3 += 1
            else:
                k4 += 1
    n1 = k1 + k2
    n2 = k3 + k4
    p1 = k1 / n1
    p2 = k3 / n2
    p = (k1 + k3) / (n1 + n2)
    return 2 * (logL(p1, k1, n1) + logL(p2, k3, n2) - logL(p, k1, n1) - logL(p, k3, n2))


# 计算3-gram的likelihood ratio
def calculate_3_gram(content, A, B, C):
    K1 = [0.0, 0.0, 0.0, 0.0]
    K2 = [0.0, 0.0, 0.0, 0.0]
    for words in content:
        for i in range(0, len(words) - 2):
            if words[i] == A and words[i + 1] == B and words[i + 2] == C:
                K1[0] += 1
            elif words[i] != A and words[i + 1] == B and words[i + 2] == C:
                K1[1] += 1
            elif words[i] == A and words[i + 1] != B and words[i + 2] == C:
                K1[2] += 1
            elif words[i] != A and words[i + 1] != B and words[i + 2] == C:
                K1[3] += 1
            elif words[i] == A and words[i + 1] == B and words[i + 2] != C:
                K2[0] += 1
            elif words[i] != A and words[i + 1] == B and words[i + 2] != C:
                K2[1] += 1
            elif words[i] == A and words[i + 1] != B and words[i + 2] != C:
                K2[2] += 1
            elif words[i] != A and words[i + 1] != B and words[i + 2] != C:
                K2[3] += 1
    n1 = K1[0] + K1[1] + K1[2] + K1[3]
    n2 = K2[0] + K2[1] + K2[2] + K2[3]
    P1 = [K1[0] / n1, K1[1] / n1, K1[2] / n1, K1[3] / n1]
    P2 = [K2[0] / n2, K2[1] / n2, K2[2] / n2, K2[3] / n2]
    P = [(K1[0] + K2[0]) / (n1 + n2), (K1[1] + K2[1]) / (n1 + n2), (K1[2] + K2[2]) / (n1 + n2),
         (K1[3] + K2[3]) / (n1 + n2)]

    return 2 * (logL2(P1, K1) + logL2(P2, K2) - logL2(P, K1) - logL2(P, K2))


def main():
    P_5, P_10, P_20 = 0.0, 0.0, 0.0
    for news in news_name:
        labels, signed_labels = read_labels(news)
        content = read_news(news)
        score = [0.0 for i in range(0, len(labels))]
        for i, label in enumerate(labels):
            label = label.split('+')
            if len(label) == 2:
                score[i] = calculate_2_gram(content, label[0], label[1])
            elif len(label) == 3:
                score[i] = calculate_3_gram(content, label[0], label[1], label[2])
        index = [i for i in range(0, len(labels))]
        for i in range(0, len(labels)):
            for j in range(i + 1, len(labels)):
                if score[index[i]] < score[index[j]]:
                    index[i], index[j] = index[j], index[i]
        p_5, p_10, p_20 = 0.0, 0.0, 0.0
        for i in range(0, 5):
            if labels[index[i]] in signed_labels:
                p_5 += 1
        for i in range(0, 10):
            if labels[index[i]] in signed_labels:
                p_10 += 1
        for i in range(0, 20):
            print labels[index[i]], score[index[i]]
            if labels[index[i]] in signed_labels:
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

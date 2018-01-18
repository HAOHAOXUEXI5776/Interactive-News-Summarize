# coding:utf-8

# 根据word（字面信息）来合并标签，规则如下：
# 1.如果两个ngram(n >= 3)能对接起来，且中间公共部分>=2个词，且对接后的词在原文中出现超过5次，则进行对接
# 2.如果存在包含关系（一个ngram的每个字都在另一个ngram中出现），则合并为打分靠前的ngram
# 3.如果很相似（一个ngram的65%以上的字在另一个ngram中出现），则合并为打分靠前的ngram
# 4.其他情况不进行合并

import os

root_dir = '../Regression/see/svr/'  # 选择一个效果最佳的回归结果
news_dir = '../Ngrams/Processed/'  # 新闻原文（分词后）
out_dir = './label/'
min_count = 5  # 对接后的词的最小出现次数
min_contain_value = 0.65

news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']


# 计算两个ngram的包含度 = max{a在b中出现比例, b在a中出现比例}，如果有包含关系，包含度为1
def contain_value(gram1, gram2):
    gram1 = gram1.replace('+', '').decode('utf-8')
    gram2 = gram2.replace('+', '').decode('utf-8')
    v1 = 0.0
    for word in gram1:
        if word in gram2:
            v1 += 1
    v1 /= len(gram1)
    v2 = 0.0
    for word in gram2:
        if word in gram1:
            v2 += 1
    v2 /= len(gram2)
    return max(v1, v2)


# 尝试将两个ngram进行对接，要求公共部分至少包含两个词
def try_joint(gram1, gram2):
    gram1 = gram1.split('+')
    gram2 = gram2.split('+')
    if len(gram1) < 3 or len(gram2) < 3:
        return False, ''
    l = min(len(gram1), len(gram2))
    for i in range(2, l):  # 重合部分的长度，如果等于len(gram1)的话在2.中得到处理
        tmp1 = gram1[-i:]
        tmp2 = gram2[:i]
        if tmp1 == tmp2:
            return True, '+'.join(gram1[:-i] + gram2)
        tmp1 = gram1[:i]
        tmp2 = gram2[-i:]
        if tmp1 == tmp2:
            return True, '+'.join(gram2[:-i] + gram1)
    return False, ''


for news in news_name:

    # 先读入分词后的新闻
    content = ''
    f = open(news_dir + news + '/words.txt', 'r')
    for line in f:
        content += line + '\n'
    f.close()

    # 读入标签
    chosen = []  # 已经得到的label集合
    rest = []  # 剩余label集合
    cur_file = open(root_dir + news + '.txt', 'r')
    for line in cur_file:
        line = line.strip().split()
        rest.append(line[0].strip())  # 一开始所有都是rest
    cur_file.close()

    # 第一轮合并，解决情况1.，尝试对接
    for la in rest:
        choose_la = True
        for i, lb in enumerate(chosen):
            flag, la_lb = try_joint(la, lb)
            if not flag:
                continue
            if content.count(la_lb.replace('+', ' '), 0, len(content)) >= min_count:
                chosen[i] = la_lb
                choose_la = False
                break
        if choose_la:
            chosen.append(la)

    # 第二轮合并，解决情况2.3.，处理相似、包含关系
    rest = chosen
    chosen = []
    for la in rest:
        choose_la = True
        for i, lb in enumerate(chosen):
            if contain_value(la, lb) >= min_contain_value:
                choose_la = False
                break
        if choose_la:
            chosen.append(la)

    cur_path = out_dir + news
    if not os.path.exists(cur_path):
        os.mkdir(cur_path)

    out_file = open(cur_path + '/label.txt', 'w')
    for l in chosen:
        out_file.write(l + '\n')
    out_file.close()

# coding:utf-8

# 通过回归计算，已经得到了各新闻下排名前20的标签，现在对排名前20的标签进行合并，规则如下：
# 1.如果存在包含关系，则合并为打分靠前的ngram
# 2.如果两个ngram内容相同，顺序不一致，合并为打分靠前的ngram
# 3.如果两个3-gram分别是abc和bcd，且abcd在原文中出现过5次以上，则合并为abcd
# 4.其他情况不进行合并

import os

root_dir = '../Regression/see/svr/'
news_dir = '../Ngrams/Processed/'
out_dir = './label/'
min_count = 5

news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']


def different_order(l1, l2):
    if len(l1) != len(l2):
        return False
    for ll in l1:
        if ll not in l2:
            return False
    return True


for news in news_name:
    # 先读入分词后的新闻
    content = ''
    f = open(news_dir + news + '/words.txt', 'r')
    for line in f:
        content += line + '\n'
    f.close()
    label = []  # 已经得到的label集合
    rest = []  # 剩余label集合
    cur_file = open(root_dir + news + '.txt', 'r')
    for line in cur_file:
        line = line.strip().split()
        rest.append(line[0])
    cur_file.close()
    for la in rest:
        flag = True
        la_s = la.split('+')
        for i, lb in enumerate(label):
            if (la.replace('+', '') in lb.replace('+', '')) or (lb.replace('+', '') in la.replace('+', '')):
                flag = False
                break
            lb_s = lb.split('+')
            if different_order(la_s, lb_s):
                flag = False
                break
            if len(la_s) == 3 and len(lb_s) == 3:
                tmp_l = '!@#$'
                if la_s[1] == lb_s[0] and la_s[2] == lb_s[1]:
                    tmp_l = la_s[0] + ' ' + lb.replace('+', ' ')
                elif la_s[0] == lb_s[1] and la_s[1] == lb_s[2]:
                    tmp_l = lb_s[0] + ' ' + la.replace('+', ' ')
                if content.count(tmp_l, 0, len(content)) >= min_count:
                    label[i] = tmp_l.replace(' ', '+')
                    flag = False
                    break
        if flag:
            label.append(la)
    cur_path = out_dir + news
    if not os.path.exists(cur_path):
        os.mkdir(cur_path)
    out_file = open(cur_path + '/label.txt', 'w')
    for l in label:
        out_file.write(l + '\n')
    out_file.close()

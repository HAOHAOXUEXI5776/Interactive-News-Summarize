# coding:utf-8

# 将原新闻切分成句子，保存到文件中，切分原则：
# 新闻标题保存到另外的title文件中，
# 新闻的每一行当作一段，段内以句号为边界切分句子，如果句号出现在引号之中，则不作为边界

import re
import os

news_dir = '../News/'
out_dir = 'sentence/'

news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']


def replace(matched):
    return matched.group().replace('。'.decode('utf-8'), '@@')


def replace_back(string):
    return string.replace('@@', '。'.decode('utf-8'))


class Sentence:
    def __init__(self, content, s_idx, p_idx, p_off):
        self.content = content
        self.sen_idx = s_idx
        self.para_idx = p_idx
        self.para_off = p_off


# 依次处理每个新闻事件
for news in news_name:
    print news
    cur_dir = out_dir + news
    if not os.path.exists(cur_dir):
        os.mkdir(cur_dir)
    f1 = open(cur_dir + '/sentence.txt', 'w')  # 保存分割后的句子
    f2 = open(cur_dir + '/title.txt', 'w')  # 保存标题

    # 读取每个事件的所有新闻，最多100篇
    for i in range(1, 101):
        cur_news = news_dir + news + '/' + str(i) + '.txt'
        if not os.path.exists(cur_news):
            break
        f = open(cur_news, 'r')
        f2.write(f.readline())
        sen_idx = 0  # 当前句子是全文的第几个句子
        para_idx = 0  # 当前句子属于全文第几个段落
        para_len = 0  # 当前段落共有几个句子
        for para in f:
            if '。' not in para:
                continue
            para_idx += 1
            para = para.decode('utf-8')

            # 分别处理中文和英文双引号，将双引号中的。替换
            pattern = r'“([^“”]*。[^“”]*)”'.decode('utf-8')
            para = re.sub(pattern, replace, para)
            pattern = r'"([^"]*。[^"]*)"'.decode('utf-8')
            para = re.sub(pattern, replace, para)

            # 以。分割句子
            para = para.replace('。'.decode('utf-8'), '。##'.decode('utf-8'))
            para = para.split('##'.decode('utf-8'))

            sentence_list = []
            para_off = 0
            for sen in para:
                if len(sen) < 5:
                    continue
                sen_idx += 1
                para_off += 1
                sentence_list.append(Sentence(replace_back(sen).strip(), sen_idx, para_idx, para_off))
            for sen in sentence_list:
                f1.write(str(i) + ' ' + str(sen.sen_idx) + ' ' + str(sen.para_idx) + ' ' + str(sen.para_off)
                         + ' ' + str(para_off) + '\n')
                f1.write(sen.content.encode('utf-8') + '\n')
        f.close()
    f1.close()
    f2.close()

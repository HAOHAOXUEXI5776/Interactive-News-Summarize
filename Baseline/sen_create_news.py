# coding:utf-8

# Baseline生成第一步
# PKUSUMSUM是以句子为单位进行处理的，而现在需要按照块进行处理，所以要把一个块变成"伪句子"（把块中句号，问号，叹号变成逗号）
# 此代码利用../Sentence/sentence/下的内容重新生成了一遍原始新闻，结果存在./sen_news/中

import os
import re

sen_dir = '../Sentence/sentence/'
out_dir = './sen_news/'


news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']


# 处理块，将其中的句号，问号，叹号变成逗号，末尾加一个句号，同时删除一开始的报道信息（对baseline也要一视同仁）
def process(sen):
    return sen.replace('。', '，').replace('？', '，').replace('！', '，') + '。'


def write_news(news, idx, sen_set):
    cur_dir = out_dir + news
    if not os.path.exists(cur_dir):
        os.mkdir(cur_dir)
    f = open(cur_dir + '/' + str(idx) + '.txt', 'w')
    for sen in sen_set:
        f.write(process(sen) + '\n')
    f.close()


def main():
    for news in news_name:
        f_sen = open(sen_dir + news + '/sentence.txt', 'r')
        cur_news_id = 1
        cur_sen_set = []
        while True:
            info = f_sen.readline()
            if len(info) < 1:
                break
            info = info.strip().split()
            if int(info[0]) != cur_news_id:
                write_news(news, cur_news_id, cur_sen_set)
                cur_news_id = int(info[0])
                cur_sen_set = []
            cur_sen_set.append(f_sen.readline().strip())
        write_news(news, cur_news_id, cur_sen_set)
        f_sen.close()


if __name__ == '__main__':
    main()

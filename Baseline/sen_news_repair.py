# coding:utf-8

# Baseline生成第三步
# 已经使用PKUSUMSUM得到了摘要，现在要把摘要中的标点符号还原成原来的样子

import re
import os

sen_dir = '../Sentence/sentence/'
sum_dir = './sen_sum_raw/'
out_dir = './sen_sum/'

methods = ['Coverage', 'Lead', 'Centroid', 'LexPageRank', 'TextRank', 'Submodular', 'ClusterCMRW']
news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']


def read_sen(news):
    f_sen = open(sen_dir + news + '/sentence.txt', 'r')
    sen_set = []
    while True:
        info = f_sen.readline()
        if len(info) < 1:
            break
        sen_set.append(f_sen.readline().strip())
    f_sen.close()
    return sen_set


def main():
    for news in news_name:
        sen_set = read_sen(news)
        for m in methods:
            cur_file = open(sum_dir + m + '/' + news + '.txt', 'r')
            cur_dir = out_dir + m + '/'
            if not os.path.exists(cur_dir):
                os.mkdir(cur_dir)
            out_file = open(out_dir + m + '/' + news + '.txt', 'w')
            for sen in cur_file:
                sen = sen.strip()
                for sentence in sen_set:
                    if sen == sentence.replace('。', '，').replace('？', '，').replace('！', '，') + '。':
                        out_file.write(sentence + '\n')
                        break
            out_file.close()
            cur_file.close()


if __name__ == '__main__':
    main()

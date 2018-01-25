# coding:utf-8

# Baseline生成第三步
# 已经使用PKUSUMSUM得到了摘要，现在要把摘要中的标点符号还原成原来的样子

import re
import os

blk_dir = '../Sentence/block/'
sum_dir = './sum_raw/'
out_dir = './sum/'

methods = ['Coverage', 'Lead', 'Centroid', 'LexPageRank', 'TextRank', 'Submodular', 'ClusterCMRW']
news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']


def process(blk):
    blk = blk.decode('utf-8')
    pattern = r'[^腾通](电|讯)(（[^（）]*）|\([^\(\)]*\))'.decode('utf-8')
    matched = re.search(pattern, blk)
    if matched:
        match_str = matched.group()
        idx = blk.index(match_str) + len(match_str)
        blk = blk[idx:]
    pattern = r'([\w]日(电|讯)|新浪.{2}讯)'.decode('utf-8')
    matched = re.search(pattern, blk)
    if matched:
        match_str = matched.group()
        idx = blk.index(match_str) + len(match_str)
        blk = blk[idx:]
    pattern = r'【[^【】]*】|\[[^\[\]]*\]'.decode('utf-8')
    matched = re.search(pattern, blk)
    if matched:
        match_str = matched.group()
        idx = blk.index(match_str)
        if idx < 1:
            idx = idx + len(match_str)
            blk = blk[idx:]
    blk = blk.encode('utf-8')
    return blk


def read_blk(news):
    f_blk = open(blk_dir + news + '/block.txt', 'r')
    blk_set = []
    while True:
        blk_size = f_blk.readline()
        if len(blk_size) == 0:
            break
        blk_size = int(blk_size.strip())
        cur_blk = ''
        for i in range(0, blk_size):
            f_blk.readline()
            cur_blk += f_blk.readline().strip()
        blk_set.append(process(cur_blk))
    f_blk.close()
    return blk_set


def main():
    for news in news_name:
        blk_set = read_blk(news)
        for m in methods:
            cur_file = open(sum_dir + m + '/' + news + '.txt', 'r')
            cur_dir = out_dir + m + '/'
            if not os.path.exists(cur_dir):
                os.mkdir(cur_dir)
            out_file = open(out_dir + m + '/' + news + '.txt', 'w')
            for blk in cur_file:
                blk = blk.strip()
                for block in blk_set:
                    if blk == block.replace('。', '，').replace('？', '，').replace('！', '，') + '。':
                        out_file.write(block + '\n')
                        break
            out_file.close()
            cur_file.close()


if __name__ == '__main__':
    main()

# coding:utf-8

# Baseline生成第一步
# PKUSUMSUM是以句子为单位进行处理的，而现在需要按照块进行处理，所以要把一个块变成"伪句子"（把块中句号，问号，叹号变成逗号）
# 此代码利用../Sentence/block/下的内容重新生成了一遍原始新闻，结果存在./news/中

import os
import re

blk_dir = '../Sentence/block/'
out_dir = './news/'


news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']


# 处理块，将其中的句号，问号，叹号变成逗号，末尾加一个句号，同时删除一开始的报道信息（对baseline也要一视同仁）
def process(blk):
    blk = blk.decode('utf-8')
    pattern = r'[^腾通](电|讯)(（[^（）]*）|\([^\(\)]*\))'.decode('utf-8')
    matched = re.search(pattern, blk)
    if matched:
        match_str = matched.group()
        idx = blk.index(match_str) + len(match_str)
        blk = blk[idx:]
    pattern = r'[\w]日(电|讯)'.decode('utf-8')
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
    return blk.replace('。', '，').replace('？', '，').replace('！', '，') + '。'


# 将以块为单位生成的新闻写回文件
def write_news(news, idx, blk_set):
    cur_dir = out_dir + news
    if not os.path.exists(cur_dir):
        os.mkdir(cur_dir)
    f = open(cur_dir + '/' + str(idx) + '.txt', 'w')
    for blk in blk_set:
        f.write(process(blk) + '\n')
    f.close()


def main():
    for news in news_name:
        f_blk = open(blk_dir + news + '/block.txt', 'r')
        cur_news_id = 1
        cur_blk_set = []
        while True:
            blk_size = f_blk.readline()
            if len(blk_size) == 0:
                break
            blk_size = int(blk_size.strip())
            cur_blk = ''
            for i in range(0, blk_size):
                info = f_blk.readline().strip().split()
                if int(info[0]) != cur_news_id:
                    write_news(news, cur_news_id, cur_blk_set)
                    cur_news_id = int(info[0])
                    cur_blk_set = []
                cur_blk += f_blk.readline().strip()
            cur_blk_set.append(cur_blk)
        write_news(news, cur_news_id, cur_blk_set)
        f_blk.close()


if __name__ == '__main__':
    main()

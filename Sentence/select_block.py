# coding:utf-8
import os

# 根据一个标签，找到包含它的块

label_dir = './label/'
block_dir = './block/'
out_dir = './assign/little_block/'


# 句子类
class Sentence:

    def __init__(self, content, news_idx, sen_idx, para_idx, para_off, para_size):
        self.content = content
        self.news_idx = news_idx
        self.sen_idx = sen_idx
        self.para_idx = para_idx
        self.para_off = para_off
        self.para_size = para_size

    def has_label(self, label):
        return label in self.content


# block集合类，存储一个新闻事件的所有block，每一个block又是一个Sentence的数组
class BlockSet:
    def __init__(self):
        self.blk_list = []
        self.blk_num = 0
        self.blk_ave_size = 0.0

    def set(self, blk_file):
        f = open(blk_file, 'r')
        while True:
            blk_size = f.readline()
            if len(blk_size) == 0:
                break
            blk_size = int(blk_size)  # 第一行存储该块儿有几个句子
            cur_blk = []
            for t in range(0, blk_size):
                info = f.readline().strip().split()
                content = f.readline().strip()
                sen = Sentence(content, info[0], info[1], info[2], info[3], info[4])
                cur_blk.append(sen)
            self.blk_list.append(cur_blk)
            self.blk_ave_size += len(cur_blk)
        self.blk_num = len(self.blk_list)
        self.blk_ave_size /= float(self.blk_num)
        f.close()


news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']


# 找到包含标签的blk_set的子集
def find_blk(label, blk_set):
    result = []
    for block in blk_set.blk_list:
        flag = False
        for sen in block:
            if sen.has_label(label):
                flag = True
                break
        if flag:
            result.append(block)
    return result


def main():
    for news in news_name:
        # 得到标签
        labels = []
        f = open(unicode(label_dir + news + '/label.txt', 'utf8'), 'r')
        for line in f:
            labels.append(line.strip().replace('+', ''))
        f.close()

        # 得到所有块
        blk_set = BlockSet()
        blk_set.set(unicode(block_dir + news + '/block.txt', 'utf8'))

        print news, '总块数 =', blk_set.blk_num, '平均块长度 =', blk_set.blk_ave_size

        cur_path = unicode(out_dir + news, 'utf8')
        if not os.path.exists(cur_path):
            os.mkdir(cur_path)

        for label in labels:
            blocks = find_blk(label, blk_set)
            f = open(unicode(out_dir + news + '/' + label + '.txt', 'utf8'), 'w')
            for block in blocks:
                f.write(str(len(block)) + '\n')
                for sen in block:
                    f.write(
                        str(sen.news_idx) + ' ' + str(sen.sen_idx) + ' ' + str(sen.para_idx) + ' ' + str(sen.para_off)
                        + ' ' + str(sen.para_size) + '\n')
                    f.write(sen.content + '\n')
            f.close()


if __name__ == '__main__':
    main()

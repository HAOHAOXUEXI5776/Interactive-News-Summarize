# coding:utf-8

# Baseline生成第二步
# 以不同的参数运行PKUSUMSUM.jar，将不同方法，不同事件的结果存在不同的文件中
# mark:新发现了os.system(command)指令，非常好用，以后基本可以告别直接写shell脚本了
import os

pkusumsum_path = '/Users/liuhui/Desktop/PKUSUMSUM/PKUSUMSUM.jar'  # jar包位置
length = 1050
methods = ['Coverage', 'Lead', 'Centroid', 'ILP', 'LexPageRank', 'TextRank', 'Submodular', 'ClusterCMRW']
chosen = [0, 1, 2, 4, 5, 6, 7]   # 选择的方法，ILP暂时没使用
in_dir = './news/'
out_dir = './sum_raw/'

news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

for m in chosen:
    print methods[m] + ' ing...'
    cur_out_dir = out_dir + methods[m]
    if not os.path.exists(cur_out_dir):
        os.mkdir(cur_out_dir)
    for news in news_name:
        news = news.replace(' ', r'\ ')
        command = 'java -jar ' + pkusumsum_path + ' -T 2 -input ' + in_dir + news + ' -output ' + cur_out_dir + '/' \
                  + news + '.txt' + ' -L 1 -n ' + str(length) + ' -m ' + str(m) + ' -stop ../stopword.txt'
        print command
        os.system(command)


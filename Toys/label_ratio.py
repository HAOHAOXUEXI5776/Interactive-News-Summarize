# coding:utf-8

# 统计标记过的uni-gram, bi-gram, 3-gram的占比

newsName = ['德国大选', '俄罗斯世界杯', '功守道', '九寨沟7.0级地震', '权力的游戏',
            '双十一购物节', '乌镇互联网大会', '战狼2', 'hpv疫苗', 'iPhone X',
            '李晨求婚范冰冰', '江歌刘鑫', '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园',
            '绝地求生 吃鸡', '英国脱欧', '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

root_dir = '../Ngrams/feature_12cut/'

Sum1, Sum2, Sum3 = 0.0, 0.0, 0.0
Sum = 0.0
print "liu's label"
for n in range(0, 10):
    cnt1 = 0.0
    cnt2 = 0.0
    cnt3 = 0.0
    all_cnt = 0.0
    curFile = root_dir + newsName[n] + '.txt'
    curFile = unicode(curFile, 'utf-8')
    f = open(curFile)
    for line in f:
        label = line.strip().split()[1]
        label = float(label)
        if label < 0.5:
            continue
        all_cnt += 1
        label = len(line.strip().split()[0].split('+'))
        if label == 1:
            cnt1 += 1
        elif label == 2:
            cnt2 += 1
        elif label == 3:
            cnt3 += 1
    print round(cnt1/all_cnt, 3), round(cnt2/all_cnt, 3), round(cnt3/all_cnt, 3)
    Sum += all_cnt
    Sum1 += cnt1
    Sum2 += cnt2
    Sum3 += cnt3
print
print "qin's label"
for n in range(11, 20):
    cnt1 = 0.0
    cnt2 = 0.0
    cnt3 = 0.0
    all_cnt = 0.0
    curFile = root_dir + newsName[n] + '.txt'
    curFile = unicode(curFile, 'utf-8')
    f = open(curFile)
    for line in f:
        label = line.strip().split()[1]
        label = float(label)
        if label < 0.5:
            continue
        all_cnt += 1
        label = len(line.strip().split()[0].split('+'))
        if label == 1:
            cnt1 += 1
        elif label == 2:
            cnt2 += 1
        elif label == 3:
            cnt3 += 1
    print round(cnt1 / all_cnt, 3), round(cnt2 / all_cnt, 3), round(cnt3 / all_cnt, 3)
    Sum += all_cnt
    Sum1 += cnt1
    Sum2 += cnt2
    Sum3 += cnt3
print '\n', round(Sum1/Sum, 3), round(Sum2/Sum, 3), round(Sum3/Sum, 3)

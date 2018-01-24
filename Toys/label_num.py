# coding:utf-8

newsName = ['德国大选', '俄罗斯世界杯', '功守道', '九寨沟7.0级地震', '权力的游戏',
            '双十一购物节', '乌镇互联网大会', '战狼2', 'hpv疫苗', 'iPhone X',
            '李晨求婚范冰冰', '江歌刘鑫', '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园',
            '绝地求生 吃鸡', '英国脱欧', '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

root_dir = '../Ngrams/feature_12cut/'

all_cnt = 0.0
all_label = 0.0

print "liu's label"
for n in range(0, 10):
    cnt1 = 0
    cnt2 = 0
    cnt3 = 0
    all = 0
    curFile = root_dir + newsName[n] + '.txt'
    curFile = unicode(curFile, 'utf-8')
    f = open(curFile)
    for line in f:
        label = line.strip().split()[1]
        label = float(label)
        if label == 1.0:
            cnt1 += 1
        elif label == 2.0:
            cnt2 += 1
        elif label == 3.0:
            cnt3 += 1
        all += 1
    ratio = float(cnt1 + cnt2 + cnt3) / all
    all_cnt += cnt1 + cnt2 + cnt3
    all_label += all
    print newsName[n], all, cnt1 + cnt2 + cnt3, ratio
print
print "qin's label"
for n in range(11, 20):
    cnt1 = 0
    cnt2 = 0
    cnt3 = 0
    all = 0
    curFile = root_dir + newsName[n] + '.txt'
    curFile = unicode(curFile, 'utf-8')
    f = open(curFile)
    for line in f:
        label = line.strip().split()[1]
        label = float(label)
        if label == 1.0:
            cnt1 += 1
        elif label == 2.0:
            cnt2 += 1
        elif label == 3.0:
            cnt3 += 1
        all += 1
    ratio = float(cnt1 + cnt2 + cnt3) / all
    all_cnt += cnt1 + cnt2 + cnt3
    all_label += all
    print newsName[n], all, cnt1 + cnt2 + cnt3, ratio

print
print 'Sum label:', int(all_label), 'Sum signed:', int(all_cnt), 'Sum ratio:', round(all_cnt/all_label, 3)

#coding:utf8

labelDir = '../Ngrams/feature/'
contDir = 'continuity/'
news = ['hpv疫苗','iPhone X', '乌镇互联网大会','九寨沟7.0级地震','俄罗斯世界杯',\
'双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',\
'王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',\
'萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

for newsName in news:
    print newsName
    f1 = open(unicode(labelDir+newsName+'.txt', 'utf8'), 'r')
    f2 = open(unicode(contDir+newsName+'.txt', 'utf8'), 'r')
    dic = {}
    tag = {}
    for line in f2:
        line = line.strip().split()
        gram = line[0]
        dic[gram] = 1
        tag[gram] = line[1]

    cnt1 = [.0,.0,.0]
    cnt1in =  [.0,.0,.0]
    cnt0 = [.0,.0,.0]
    cnt0in = [.0,.0,.0]
    for line in f1:
        line = line.strip().split()
        gram = ''.join(line[0].split('+'))
        n = len(line[0].split('+')) - 1
        if float(line[1]) > 0.5:
            cnt1[n] += 1
            if gram in dic and 'n' in tag[gram]:
                cnt1in[n] += 1
        else:
            cnt0[n] += 1
            if gram in dic and 'n' in tag[gram]:
                cnt0in[n] += 1
    f1.close()
    f2.close()
    print cnt1, cnt1in
    print cnt0, cnt0in
    print (cnt1[0]+cnt1[1]+cnt1[2])/(cnt1[0]+cnt1[1]+cnt1[2]+cnt0[0]+cnt0[1]+cnt0[2]),\
        (cnt1in[0]+cnt1in[1]+cnt1in[2])/(cnt1in[0]+cnt1in[1]+cnt1in[2]+cnt0in[0]+cnt0in[1]+cnt0in[2])



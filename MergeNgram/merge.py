#coding:utf-8

modelname = '随机森林'
topnDir = '../Regression/see/'+modelname+'/'

news = ['hpv疫苗','iPhone X', '乌镇互联网大会','九寨沟7.0级地震','俄罗斯世界杯',\
'双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',\
'王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',\
'萨德系统 中韩', '雄安新区', '榆林产妇坠楼']
# news = ['战狼2']
for newsName in news:
    f = open(unicode(topnDir+newsName+'.txt', 'utf8'), 'r')
    topic = []
    kind = []
    for line in f:
        line = line.strip().split()
        gram = ''.join(line[0].split('+')) #去掉+号
        topic.append(gram)
        kind.append(1)
    f.close()

    #如果被包含，则去掉
    l = len(topic)
    for i in range(0, l):
        for j in range(0, l):
            if j != i:
                if topic[i] in topic[j]:
                    kind[i] = 0
                if topic[j] in topic[i]:
                    kind[j] = 0
    print newsName
    print (' '.join('%s-%d'%(topic[i], kind[i]) for i in range(0, l)) )

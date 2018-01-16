#coding:utf-8

news = ['hpv疫苗','iPhone X', '乌镇互联网大会','九寨沟7.0级地震','俄罗斯世界杯',
'双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
'王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
'萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

for newsName in news:
    f = open(unicode(newsName+'.txt', 'utf8'), 'r')
    tol = 0
    cnt = [0,0,0]
    for line in f:
        line = line.strip().split()
        score = int(float(line[1]))
        tol += 1
        if score != 0:
            cnt[score-1] += 1
    print ("%s:%d,%d+%d+%d=%d,%f"%(newsName,tol,cnt[0],cnt[1],cnt[2],\
        cnt[0]+cnt[1]+cnt[2],(cnt[0]+cnt[1]+cnt[2])/float(tol)))
    f.close()

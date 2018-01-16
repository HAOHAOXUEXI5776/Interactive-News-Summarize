#coding:utf8

tagDir = 'tag/'
labelDir = '../Ngrams/feature/'

news = ['hpv疫苗','iPhone X', '乌镇互联网大会','九寨沟7.0级地震','俄罗斯世界杯',\
'双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',\
'王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',\
'萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

#ngram中有新闻名称，不用
#1gram中，只保留名词
#表示时间的ngram，，量词型结构，去掉
#如果2gram在3gram中出现，也去掉，去掉。


for newsName in news:
    print newsName

    #初始的比例
    f1 = open(unicode(labelDir+newsName+'.txt', 'utf8'), 'r')
    tol, scotol = 0.0, 0.0
    for line in f1:
        line = line.strip().split()
        tol += 1
        scotol += (line[1] != '0.0')
    print '原始的比例：', scotol/tol
    f1.close()

    #记录2/3gram中的词
    f1 = open(unicode(labelDir+newsName+'.txt', 'utf8'), 'r')
    dic23 = {}
    for line in f1:
        line = line.strip().split()
        if len(line[0].split('+')) >= 2:
            for word in line[0].split('+'):
                dic23[word] = 0
    f1.close()

    #得到所有词的词性（少数没有）
    alltag = {}
    f2 = open(unicode(tagDir+newsName+'.txt', 'utf8'), 'r')
    for line in f2:
        line = line.strip().split()
        if len(line) > 1:
            alltag[line[0]] = line[1]
    f2.close()

    #去掉没有名词的ngram和不在2/3gram中的1gram，统计丢弃的数目(也记录丢弃的里面打分的个数)
    diutol, diusco = 0.0, 0.0
    f1 = open(unicode(labelDir+newsName+'.txt', 'utf8'), 'r')
    for line in f1:
        line = line.strip().split()
        ngram = line[0].split('+')
        tag = ''
        for g in ngram:
            if g in alltag:
                tag += '+'+ alltag[g]
            else:
                tag += '+' + ''

        #丢弃不在2/3gram中的1gram，和不是名词的1gram
        if len(ngram) == 1:
            diutol += 1
            if line[1] != '0.0':
                diusco += 1
            # if ngram[0] in dic23 or 'n' not in tag or tag == '+nt':
            #     diutol += 1
            #     if line[1] != '0.0':
            #         diusco += 1
        else:
            if 'n' not in tag:
                diutol += 1
                if line[1] != '0.0':
                    diusco += 1
    f1.close()

    # #去除出现在3gram中的2gram
    # diu2, diu2sco = 0., 0.
    # dic3 = {}
    # f1 = open(unicode(labelDir+newsName+'.txt', 'utf8'), 'r')
    # for line in f1:
    #     line = line.strip().split()
    #     gram = line[0].split('+')
    #     n = len(gram)
    #     if n == 3:
    #         t1 = gram[0]+gram[1]
    #         t2 = gram[1]+gram[2]
    #         if t1 not in dic3:
    #             dic3[t1] = 1
    #         if t2 not in dic3:
    #             dic3[t2] = 1
    # f1.close()
    # f1 = open(unicode(labelDir+newsName+'.txt', 'utf8'), 'r')
    # for line in f1:
    #     line = line.strip().split()
    #     gram = line[0].split('+')
    #     n = len(gram)
    #     if n == 2:
    #         if gram[0]+gram[1] in dic3:
    #             diu2 += 1
    #             if line[1] != '0.0':
    #                 diu2sco += 1
    # f1.close()



    print '去掉上述的1gram和没有名词的ngram后的比例：', (scotol-diusco)/(tol-diutol), scotol, scotol-diusco, tol, tol-diutol
    # print '去掉上述的1gram和没有名词的ngram后的比例：', (scotol-diusco-diu2sco)/(tol-diutol-diu2)

'''
根据词性做删除
'''

'''
news = ['乌镇互联网大会']
tagDir = 'tag/'
labelDir = '../Ngrams/feature/'
for newsName in news:
    alltag = {}
    f1 = open(unicode(labelDir+newsName+'.txt', 'utf8'), 'r')
    f2 = open(unicode(tagDir+newsName+'.txt', 'utf8'), 'r')

    for line in f2:
        line = line.strip().split()
        alltag[line[0]] = line[1]
    f2.close()

    cnt0 = [0.0,0.0,0.0]
    cnt1 = [0.0,0.0,0.0]
    cnt2 = [0.0,0.0,0.0]
    cnt3 = [0.0,0.0, 0.0]
    aho = 0
    for line in f1:
        line = line.strip().split()
        ngram = line[0].split('+')
        n = len(ngram)
        tag = ""
        fail = False
        for i in range(0, n):
            if ngram[i] in alltag:
                tag+=alltag[ngram[i]]
            else:
                fail = True

        if fail == True:
            aho += 1
        cnt0[n-1] += 1
        if 'n' in tag:
            cnt2[n-1] += 1

        if line[1] != '0.0':
            cnt1[n-1] += 1
            if 'n' in tag:
                cnt3[n-1] += 1

    f1.close()
    # print aho
    print cnt0, cnt1
    print cnt2, cnt3
    print sum(cnt1)/sum(cnt0), sum(cnt3)/sum(cnt2)
'''

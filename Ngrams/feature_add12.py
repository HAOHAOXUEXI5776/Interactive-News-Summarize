# coding:utf-8

# 增加了两维，一是是否在连贯的词组中，二是名词的个数
# ../ForBetter/continuity/中记录了连贯的词组
# ../ForBetter/tag/记录了大部分ngram的词性
# 利用这两个文件还砍掉了部分ngram


labelDir = 'feature_lda/'
outDir = 'feature_12/'
tagDir = '../ForBetter/tag/'
contDir = '../ForBetter/continuity/'
news = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
        '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
        '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
        '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

for newsName in news:
    print newsName
    f1 = open(unicode(labelDir + newsName + '.txt', 'utf8'), 'r')
    f2 = open(unicode(contDir + newsName + '.txt', 'utf8'), 'r')
    fw = open(unicode(outDir + newsName + '.txt', 'utf8'), 'w')
    dic = {}
    tag = {}
    for line in f2:
        line = line.strip().split()
        gram = line[0]
        dic[gram] = 1
        tag[gram] = line[1]
    f2.close()

    alltag = {}
    f3 = open(unicode(tagDir + newsName + '.txt', 'utf8'), 'r')
    for line in f3:
        line = line.strip().split()
        if len(line) == 2:
            alltag[line[0]] = line[1]
    f3.close()

    # 将gram中名词的个数作为一个参数，将是否在dic中也作为一个参数
    for line in f1:
        tline = line.strip().split()
        gram = ''.join(tline[0].split('+'))
        ncnt = 0.0
        curtag = ''
        for g in tline[0].split('+'):
            if g in alltag:
                curtag += alltag[g]
                if 'n' in alltag[g]:
                    ncnt += 1
        ncnt /= 3

        # if gram in newsName:
        #    continue
        # if 'nt' in curtag or 'm' in curtag or 'd' in curtag:
        #     continue
        # if 'nt' in curtag or 'd' in curtag:
        #    continue
        # if len(tline[0].split('+')) == 1 and tline[0] in alltag and (
        #        'n' not in alltag[tline[0]] or alltag[tline[0]] != 'v'):
        #    continue
        if gram in dic:
            indic = '1.0'
        else:
            indic = '0.0'
        tline.append(indic)
        tline.append(str(ncnt))
        fw.write(' '.join(tline) + '\n')
    fw.close()
    f1.close()

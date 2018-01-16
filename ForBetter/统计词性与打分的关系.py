#coding:utf-8

class T:
    def __init__(self):
        self.po = 0.0
        self.ne = 0.0
    def up(self, p):
        if p == 1:
            self.po += 1
        else:
            self.ne += 1

news = ['hpv疫苗','iPhone X', '乌镇互联网大会','九寨沟7.0级地震','俄罗斯世界杯',\
'双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',\
'王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',\
'萨德系统 中韩', '雄安新区', '榆林产妇坠楼']
tagDir = 'tag/'
labelDir = '../Ngrams/feature/'

tagh = {}
cscore = 0.0
cunscore = 0.0
for newsName in news:
    print newsName
    f1 = open(unicode(labelDir+newsName+'.txt', 'utf8'), 'r')
    f2 = open(unicode(tagDir+newsName+'.txt', 'utf8'), 'r')
    alltag = {}
    for line in f2:
        line = line.strip().split()
        if len(line) != 1:
            alltag[line[0]] = line[1]

    for line in f1:
        line = line.strip().split()
        ngram = line[0].split('+')
        score = line[1]
        if score != '0.0':
            cscore += 1
        else:
            cunscore += 1
        for g in ngram:
            if g in alltag:
                t = alltag[g]
                if t not in tagh:
                    tagh[t] = T()
                tagh[t].up(score!='0.0')
    f1.close()
    f2.close()

for t in tagh:
    print t, tagh[t].po, tagh[t].ne, tagh[t].po/cscore, tagh[t].ne/cunscore


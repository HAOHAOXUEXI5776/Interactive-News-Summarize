#coding:utf-8
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from scipy.stats import pearsonr
from numpy import array

news = ['hpv疫苗','iPhone X', '乌镇互联网大会','九寨沟7.0级地震','俄罗斯世界杯',\
'双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',\
'王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',\
'萨德系统 中韩', '雄安新区', '榆林产妇坠楼']
X, Y= [], []
for newsName in news:
    featureSize = 12
    featureDir = "../feature_add2d/"
    f = open(unicode(featureDir+newsName+'.txt','utf8'),'r')
    for line in f:
        line = line.strip().split()
        for i in range(1, featureSize+2):
            line[i] = float(line[i])
        X.append(line[2:])
        Y.append(line[1])
    f.close()

X = array(X)
Y = array(Y)

ok = 8
X1 = SelectKBest(chi2, k=ok).fit_transform(X, Y)
X2 = SelectKBest(lambda X, Y: list(array([pearsonr(x, Y) for x in X.T]).T), k=ok).fit_transform(X, Y)

print X[0]
print X1[0]
print X2[0]

i = 0
j = 0
while i < 12:
    if X[0][i] == X1[0][j]:
        j += 1
        i += 1
    else:
        print i+1
        i += 1

i = 0
j = 0
while i < 12:
    if X[0][i] == X2[0][j]:
        j += 1
        i += 1
    else:
        print i+1
        i += 1

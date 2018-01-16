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
    featureDir = ""
    f = open(unicode(featureDir+newsName+'.txt','utf8'),'r')
    for line in f:
        line = line.strip().split()
        for i in range(1, 9):
            line[i] = float(line[i])
        X.append(line[2:9])
        Y.append(line[1])
    f.close()

X = array(X)
Y = array(Y)

X1 = SelectKBest(chi2, k=6).fit_transform(X, Y)
X2 = SelectKBest(lambda X, Y: list(array([pearsonr(x, Y) for x in X.T]).T), k=6).fit_transform(X, Y)
for i in range(0, 5):
    print X[i]
    print X1[i]
    print X2[i]

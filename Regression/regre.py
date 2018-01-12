#coding:utf-8

from sklearn import svm
from sklearn import linear_model
import math

def linearRegre(X, Y, tX):
    #最小二乘法的线性回归
    #min ||Xw-f(X)||^2
    reg = linear_model.LinearRegression()
    reg.fit(X, Y)
    return reg.predict(tX)

def ridgeRegre(X, Y, tX):
    #岭回归，防止过拟合
    #min ||Xw-f(x)||^2 + a||w||^2 (L2范数)
    reg = linear_model.Ridge(alpha = 0.5)
    reg.fit(X, Y)
    return reg.predict(tX)

def svr(X, Y, tX):
    clf = svm.SVR(cache_size=500)
    # SVR(C=1.0, cache_size=200, coef0=0.0, degree=3, epsilon=0.1, gamma='auto',
    # kernel='rbf', max_iter=-1, shrinking=True, tol=0.001, verbose=False)
    clf.fit(X, Y)
    return clf.predict(tX)

def diff(tY, Y):
    #用于计算预测值tY与真实值Y的相差度
    #Y中的分数有30,20,10,0，分别为n3,n2,n1,n0个，对tY进行排序
    #   统计前n3个有多少对应着30；
    #   统计前n3+n2个有多少个对应着30和20
    #   统计前n3+n2+n1个有多少对应着30、20和10
    l = len(Y)
    id30, id20, id10 = [], [], []
    for i in range(0, l):
        if int(Y[i]) == 30:
            id30.append(i)
        elif int(Y[i]) == 20:
            id20.append(i)
        elif int(Y[i]) == 10:
            id10.append(i)
    n3, n2, n1 = len(id30), len(id20), len(id10)
    print 'n1,n2,n3',n1,n2,n3
    #对tY进行基数排序
    index = [i for i in range(0, l)]
    for i in range(0, l):
        for j in range(i+1, l):
            if tY[index[i]] < tY[index[j]]:
                index[i], index[j] = index[j], index[i]
    cnt3, cnt2, cnt1 = 0,0,0
    for i in range(0, n3):
        if index[i] in id30:
            cnt3 += 1
    for i in range(0, n2+n3):
        if index[i] in id20:
            cnt2 += 1
    for i in range(0, n1+n2+n3):
        if index[i] in id10:
            cnt1 += 1
    return cnt3, cnt2+cnt3, cnt1+cnt2+cnt3


newsName = ['hpv疫苗','iPhone X', '乌镇互联网大会','九寨沟7.0级地震','俄罗斯世界杯',\
'双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',\
'王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',\
'萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

#使用前9个进行训练
X = []
Y = []
for k in range(0, 9):
    print newsName[k]
    #每行的结构为：ngram的内容+人工标注的分数+7个特征
    NewsName = unicode('feature/'+newsName[k]+'.txt','utf8')
    f = open(NewsName, 'r')
    for line in f:
        line = line.strip().split()
        for i in range(1, 9):
            line[i] = float(line[i])
        X.append(line[2:9])
        Y.append(line[1])
    f.close()

print len(X), len(Y)

#使用第10个作为验证集
vX = []
vY = []
content = []
for k in range(9, 10):
    print newsName[k]
    NewsName = unicode('feature/'+newsName[k]+'.txt','utf8')
    f = open(NewsName, 'r')
    for line in f:
        line = line.strip().split()
        for i in range(1, 9):
            line[i] = float(line[i])
        vX.append(line[2:9])
        vY.append(line[1])
        content.append(line[0])
    f.close()

    pY1 = linearRegre(X, Y, vX)
    print diff(pY1, vY)
    pY2 = ridgeRegre(X, Y, vX)
    print diff(pY2, vY)
    pY3 = svr(X, Y, vX)
    print diff(pY3, vY)

    # f = open(unicode('feature/查看预测值_'+newsName[k]+'.txt', 'utf8'), 'w')
    # l = len(content)
    # for i in range(0, l):
    #     f.write(content[i]+' '+str(vY[i])+' '+str(pY1[i])+' '+str(pY2[i])+' '+str(pY3[i])+'\n')
    # f.close()






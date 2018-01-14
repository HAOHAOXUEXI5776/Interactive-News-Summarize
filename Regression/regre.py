#coding:utf-8

from sklearn import svm
from sklearn import linear_model
import math

def linearRegre(X, Y):
    #最小二乘法的线性回归
    #min ||Xw-f(X)||^2
    reg = linear_model.LinearRegression()
    reg.fit(X, Y)
    return reg

def ridgeRegre(X, Y, _alpha = 0.5):
    #岭回归，防止过拟合
    #min ||Xw-f(x)||^2 + a||w||^2 (L2范数)
    reg = linear_model.Ridge(alpha = _alpha)
    reg.fit(X, Y)
    return reg

def svr(X, Y, _C = 1.0):
    reg = svm.SVR(cache_size=500, C = _C)
    # SVR(C=1.0, cache_size=200, coef0=0.0, degree=3, epsilon=0.1, gamma='auto',
    # kernel='rbf', max_iter=-1, shrinking=True, tol=0.001, verbose=False)
    reg.fit(X, Y)
    return reg

def diff(tY, Y):
    #用于计算预测值tY与真实值Y的相近度的得分
    #对tY进行排序，统计前topn个元素中，对应在Y中是3,2,1的个数cnt3,cnt2,cnt1
    #返回得分score = Σcnti*i
    topn = 20
    l = len(Y)
    id30, id20, id10 = [], [], []
    for i in range(0, l):
        if int(Y[i]) == 3:
            id30.append(i)
        elif int(Y[i]) == 2:
            id20.append(i)
        elif int(Y[i]) == 1:
            id10.append(i)
    n3, n2, n1 = len(id30), len(id20), len(id10)
    # print 'n1,n2,n3',n1,n2,n3
    #对tY进行基数排序
    index = [i for i in range(0, l)]
    for i in range(0, l):
        for j in range(i+1, l):
            if tY[index[i]] < tY[index[j]]:
                index[i], index[j] = index[j], index[i]
    cnt1, cnt2, cnt3 = 0, 0, 0
    for i in range(0, topn):
        if index[i] in id10:
            cnt1 += 1
        elif index[i] in id20:
            cnt2 += 1
        elif index[i] in id30:
            cnt3 += 1
    score = cnt1 + 2*cnt2 + 3*cnt3
    return score


newsName = ['hpv疫苗','iPhone X', '乌镇互联网大会','九寨沟7.0级地震','俄罗斯世界杯',
'双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
'王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
'萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

#采用十折交叉验证，迭代iters次，每次迭代，轮流将9个作为训练集，1个作为测试集
#得到十个分数，将10个分数平均得到该次迭代的分数。最后再对iter进行平均，作为
#该模型的得分。得分越高，说明越准确。
def tenfcv(regfun, alpha = 0.5, C = 1):
    iters = 2
    featureDir = '../Ngrams/feature/' #特征所在的目录
    score = 0.0
    for ite in range(0, iters):
        scorei = 0.0
        for vid in range(0, 20):
            #0~9中的第vid个作为验证集，其余的作为训练集
            X, Y = [], []
            for k in range(0, 20):
                if k != vid:
                    #每行的结构为：ngram的内容+人工标注的分数+7个特征
                    NewsName = unicode(featureDir+newsName[k]+'.txt','utf8')
                    f = open(NewsName, 'r')
                    for line in f:
                        line = line.strip().split()
                        for i in range(1, 9):
                            line[i] = float(line[i])
                        X.append(line[2:9])
                        Y.append(line[1])
                    f.close()

            #使用第vid个作为验证集
            vX, vY = [], []
            content = []
            NewsName = unicode(featureDir+newsName[vid]+'.txt','utf8')
            f = open(NewsName, 'r')
            for line in f:
                line = line.strip().split()
                for i in range(1, 9):
                    line[i] = float(line[i])
                vX.append(line[2:9])
                vY.append(line[1])
                content.append(line[0])
            f.close()

            if id(regfun) == id(linearRegre):
                reg = linearRegre(X, Y)
            elif id(regfun) == id(ridgeRegre):
                reg = ridgeRegre(X, Y, alpha)
            elif id(regfun) == id(svr):
                reg = svr(X, Y, C)
            pY = reg.predict(vX)
            tmpscore = diff(pY, vY)
            scorei +=  tmpscore

        score += scorei/20.0

    score /= float(iters)
    return score

def main():
    #普通的线性回归
    score = tenfcv(linearRegre)
    print 'linear_regression的分数为：', score

    #岭回归，对正则化系数a进行调参
    a = [0.1*i for i in range(1, 10)]
    for _a in a:
        score = tenfcv(ridgeRegre, alpha = _a)
        print ('ridge_regreesion, a = %f的分数为：%f'%(_a, score))

    #svr回归，对惩罚系数C进行调参
    C = [0.2*i for i in range(1, 10)]
    for _C in C:
        score = tenfcv(svr, C = _C)
        print ('sv_regreesion, C = %f的分数为：%f'%(_C, score))

if __name__== "__main__":
    main()





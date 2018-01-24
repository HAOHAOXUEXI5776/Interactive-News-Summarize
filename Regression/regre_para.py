# coding:utf-8

# 回归模型参数调整
# 回归方法：线性回归，岭回归，svr，决策树，knn，随机森林
# 需要调整的参数：
# 1.标注数据和未标注数据的比例
# 2.各回归方法自己的参数

import random
from sklearn import linear_model
from sklearn import svm
from sklearn import tree
from sklearn import neighbors
from sklearn import ensemble


# 线性回归
def linearRegre(X, Y):
    reg = linear_model.LinearRegression()
    reg.fit(X, Y)
    return reg


# 岭回归，一个参数alpha
def ridgeRegre(X, Y, _alpha):
    reg = linear_model.Ridge(alpha=_alpha)
    reg.fit(X, Y)
    return reg


# svr，三个参数kernel，C，gamma，其他参数使用默认
def svr(X, Y, _C, _gamma, _kernel):
    reg = svm.SVR(cache_size=500, C=_C, gamma=_gamma, kernel=_kernel)
    reg.fit(X, Y)
    return reg


# 决策树回归，一个参数criterion，其他使用默认
def decisionTree(X, Y, _criterion):
    reg = tree.DecisionTreeRegressor(criterion=_criterion)
    reg.fit(X, Y)
    return reg


# knn回归，两个参数K，weights，其他使用默认
def knnRegre(X, Y, K, _weights):
    reg = neighbors.KNeighborsRegressor(n_neighbors=K, weights=_weights, n_jobs=-1)
    reg.fit(X, Y)
    return reg


# 随机森林回归，两个参数N，criterion，其他使用默认
def randomForestRegre(X, Y, N, _criterion):
    reg = ensemble.RandomForestRegressor(n_estimators=N, criterion=_criterion)
    reg.fit(X, Y)
    return reg


# 用于评价回归效果，tY是预测分数，Y是人工打分，返回P@5，P@10，P@20
def evaluate(tY, Y):
    # 统计人工标记过的ngram
    l = len(Y)
    id3, id2, id1 = [], [], []
    for i in range(0, l):
        if int(Y[i]) == 3:
            id3.append(i)
        elif int(Y[i]) == 2:
            id2.append(i)
        elif int(Y[i]) == 1:
            id1.append(i)
    id = id1 + id2 + id3

    # 对tY进行基数排序
    index = [i for i in range(0, l)]
    for i in range(0, l):
        for j in range(i + 1, l):
            if tY[index[i]] < tY[index[j]]:
                index[i], index[j] = index[j], index[i]

    # 计算P@5，P@10，P@20
    P_5, P_10, P_20 = 0.0, 0.0, 0.0
    for i in range(0, 5):
        if index[i] in id:
            P_5 += 1
    P_5 /= 5
    for i in range(0, 10):
        if index[i] in id:
            P_10 += 1
    P_10 /= 10
    for i in range(0, 20):
        if index[i] in id:
            P_20 += 1
    P_20 /= 20

    return P_5, P_10, P_20


newsName = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
            '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
            '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
            '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']


# 采用二十折交叉验证，迭代iters次，计算P@5，P@10，P@20
# regfun：回归方法，feature：特征文件，delete：删除的特征，ratio：训练集中标注和未标注的比例，iters：迭代次数
def tenfcv(regfun, feature='feature', delete=[], ratio=0.5, alpha=0.5, kernel='rbf', C=1, gamma='auto',
           criterion='mse', K=5, weights='uniform', N=10, iters=1):
    featureDir = '../Ngrams/' + feature + '/'  # 特征所在的目录
    featureSize = 12

    # 计算标注的ngram和未标注的ngram的个数
    label = 0.0
    unlabel = 0.0
    for i in range(0, 20):
        NewsName = unicode(featureDir + newsName[i] + '.txt', 'utf8')
        f = open(NewsName, 'r')
        for line in f:
            line = line.strip().split()
            if float(line[1]) > 0.5:
                label += 1
            else:
                unlabel += 1
        f.close()
    gate = 1  # 使用gate变量删去训练集中的一些未标注数据
    if label / unlabel < ratio:
        gate = label / (ratio * unlabel)

    P_5, P_10, P_20 = 0.0, 0.0, 0.0
    for ite in range(0, iters):
        p_5, p_10, p_20 = 0.0, 0.0, 0.0
        for vid in range(0, 20):
            # 0~20中的第vid个作为验证集，其余的作为训练集
            X, Y = [], []
            for k in range(0, 20):
                if k != vid:
                    # 每行的结构为：ngram的内容+人工标注的分数+特征
                    NewsName = unicode(featureDir + newsName[k] + '.txt', 'utf8')
                    f = open(NewsName, 'r')
                    for line in f:
                        line = line.strip().split()
                        for i in range(1, featureSize + 2):
                            line[i] = float(line[i])
                        if line[1] < 0.5 and random.random() > gate:
                            continue
                        tmpx = []
                        for xi in range(0, featureSize):
                            if xi not in delete:
                                tmpx.append(line[xi + 2])
                        X.append(tmpx)
                        Y.append(line[1])
                    f.close()

            # 使用第vid个作为验证集
            vX, vY = [], []
            content = []
            NewsName = unicode(featureDir + newsName[vid] + '.txt', 'utf8')
            f = open(NewsName, 'r')
            for line in f:
                line = line.strip().split()
                for i in range(1, featureSize + 2):
                    line[i] = float(line[i])
                tmpx = []
                for xi in range(0, featureSize):
                    if xi not in delete:
                        tmpx.append(line[xi + 2])
                vX.append(tmpx)
                vY.append(line[1])
                content.append(line[0])
            f.close()

            if id(regfun) == id(linearRegre):
                reg = linearRegre(X, Y)
            elif id(regfun) == id(ridgeRegre):
                reg = ridgeRegre(X, Y, alpha)
            elif id(regfun) == id(svr):
                reg = svr(X, Y, _kernel=kernel, _C=C, _gamma=gamma)
            elif id(regfun) == id(decisionTree):
                reg = decisionTree(X, Y, _criterion=criterion)
            elif id(regfun) == id(knnRegre):
                reg = knnRegre(X, Y, K=K, _weights=weights)
            elif id(regfun) == id(randomForestRegre):
                reg = randomForestRegre(X, Y, N=N, _criterion=criterion)
            pY = reg.predict(vX)
            tmp5, tmp10, tmp20 = evaluate(pY, vY)
            p_5 += tmp5
            p_10 += tmp10
            p_20 += tmp20

        P_5 += p_5 / 20.0
        P_10 += p_10 / 20.0
        P_20 += p_20 / 20.0

    P_5 /= float(iters)
    P_10 /= float(iters)
    P_20 /= float(iters)
    return P_5, P_10, P_20


def main():
    feature = 'feature_12cut'
    delete = [3, 8]
    ratio = [0]
    alpha = [1,2,4,8,16,32]
    kernel = 'rbf'
    C = [4]
    gama = [1, 2]
    criterion = 'mse'
    N = [20, 25, 30, 35, 40]

    r1, a1, c1, g1, cr1, n1 = 0, 0, 0, 0, 0, 0
    P_5, P_10, P_20 = 0.0, 0.0, 0.0

    """
    print '线性回归调参'
    # 全部12个特征，不使用cut
    # 最优参数：ratio = 0
    # 全部12个特征，用cut
    # 最优参数：ratio = 0.6
    # 10个特征，用cut，去掉ce和lda2
    # 最优参数：ratio = 0.8
    for r in range(0, len(ratio)):
        cur5, cur10, cur20 = tenfcv(linearRegre, feature=feature, delete=delete, ratio=ratio[r], iters=1)
        print 'ratio:', ratio[r], '\tP@5:', cur5, '\tP@10:', cur10, '\tP@20:', cur20
        if cur5 > P_5 or (cur5 == P_5 and cur10 > P_10) or (cur5 == P_5 and cur10 == P_10 and cur20 > P_20):
            P_5 = cur5
            P_10 = cur10
            P_20 = cur20
            r1 = r
    print '最优参数：ratio:', ratio[r1]
    print '最优结果：P@5:', P_5, ' P@10:', P_10, ' P@20:', P_20
    """


    print '岭回归调参'
    # 全部12个特征，不使用cut
    # 最优参数：ratio = 0, alpha = 8
    # 全部12个特征，使用cut
    # 最优参数：ratio = 0, alpha = 16
    # 10个特征，使用cut，去掉ce和lda2
    # 最优参数：ratio = 0，alpha = 16
    for r in range(0, len(ratio)):
        for a in range(0, len(alpha)):
            cur5, cur10, cur20 = tenfcv(ridgeRegre, feature=feature, delete=delete, ratio=ratio[r], alpha=alpha[a], iters=10)
            print 'ratio:', ratio[r], 'alpha:', alpha[a], '\tP@5:', cur5, '\tP@10:', cur10, '\tP@20:', cur20
            if cur5 > P_5 or (cur5 == P_5 and cur10 > P_10) or (cur5 == P_5 and cur10 == P_10 and cur20 > P_20):
                P_5 = cur5
                P_10 = cur10
                P_20 = cur20
                r1 = r
                a1 = a
    print '最优参数：ratio:', ratio[r1], 'alpha:', alpha[a1]
    print '最优结果：P@5:', P_5, ' P@10:', P_10, ' P@20:', P_20


    """
    print 'svr调参'
    # 全部12个特征，不使用cut
    # 最优参数：ratio = 0.4, c = 1, g = 1
    # 全部12个特征，用cut
    # 最优参数：ratio = 0.8, c = 1, g = 1
    # 10个特征，用cut，去掉ce和lda2
    # 最优参数：ratio = 0.8, c = 4, g = 1
    for r in range(0, len(ratio)):
        for c in range(0, len(C)):
            for g in range(0, len(gama)):
                cur5, cur10, cur20 = tenfcv(svr, feature=feature, delete=delete, ratio=ratio[r], kernel=kernel,
                                            C=C[c], gamma=gama[g], iters=10)
                print 'ratio:', ratio[r], '\tkernel:', '\tC:', C[c], 'gamma:', gama[g], \
                    '\tP@5:', cur5, '\tP@10:', cur10, '\tP@20:', cur20
                if cur5 > P_5 or (cur5 == P_5 and cur10 > P_10) or (
                        cur5 == P_5 and cur10 == P_10 and cur20 > P_20):
                    P_5 = cur5
                    P_10 = cur10
                    P_20 = cur20
                    r1 = r
                    c1 = c
                    g1 = g
    print '最优参数：ratio:', ratio[r1], ' C:', C[c1], 'gamma:', gama[g1]
    print '最优结果：P@5:', P_5, ' P@10:', P_10, ' P@20:', P_20
    """


if __name__ == '__main__':
    main()

# coding:utf-8

# 回归模型参数调整
# 回归方法：线性回归，岭回归，svr，决策树，knn，随机森林
# 需要调整的参数：
# 1.标注数据和未标注数据的比例
# 2.feature文件夹（feature||feature1||feature2）
# 3.各回归方法自己的参数

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
    reg = linear_model.Ridge(alpha = _alpha)
    reg.fit(X, Y)
    return reg

# svr，三个参数kernel，C，gamma，其他参数使用默认
def svr(X, Y, _C, _gamma, _kernel):
    reg = svm.SVR(cache_size = 500, C = _C, gamma = _gamma, kernel = _kernel)
    reg.fit(X, Y)
    return reg

# 决策树回归，一个参数criterion，其他使用默认
def decisionTree(X, Y, _criterion):
    reg = tree.DecisionTreeRegressor(criterion = _criterion)
    reg.fit(X, Y)
    return reg

# knn回归，两个参数K，weights，其他使用默认
def knnRegre(X, Y, K, _weights):
    reg = neighbors.KNeighborsRegressor(n_neighbors = K, weights = _weights, n_jobs = -1)
    reg.fit(X, Y)
    return reg

# 随机森林回归，两个参数N，criterion，其他使用默认
def randomForestRegre(X, Y, N, _criterion):
    reg = ensemble.RandomForestRegressor(n_estimators = N, criterion = _criterion)
    reg.fit(X, Y)
    return reg

# 用于计算预测值tY与真实值Y的相近度的得分
# 对tY进行排序，统计前topn个元素中，对应在Y中是3,2,1的个数cnt3,cnt2,cnt1
# 返回得分score = Σcnti*i，命中个数number
def diff(tY, Y):
    topn = 20
    l = len(Y)
    id3, id2, id1 = [], [], []
    for i in range(0, l):
        if int(Y[i]) == 3:
            id3.append(i)
        elif int(Y[i]) == 2:
            id2.append(i)
        elif int(Y[i]) == 1:
            id1.append(i)
    n3, n2, n1 = len(id3), len(id2), len(id1)
    #对tY进行基数排序
    index = [i for i in range(0, l)]
    for i in range(0, l):
        for j in range(i+1, l):
            if tY[index[i]] < tY[index[j]]:
                index[i], index[j] = index[j], index[i]
    cnt1, cnt2, cnt3 = 0, 0, 0
    for i in range(0, topn):
        if index[i] in id1:
            cnt1 += 1
        elif index[i] in id2:
            cnt2 += 1
        elif index[i] in id3:
            cnt3 += 1
    score = cnt1 + 2 * cnt2 + 3 * cnt3
    number = cnt1 + cnt2 + cnt3
    return score, number

newsName = ['hpv疫苗','iPhone X', '乌镇互联网大会','九寨沟7.0级地震','俄罗斯世界杯',\
'双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',\
'王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',\
'萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

# 采用十折交叉验证，迭代iters次，计算得分，命中数目
# regfun指定回归方法，feature指定特征文件，ratio指定标注和未标注的比例，iters指定迭代次数，后面都是各模型自己的参数
def tenfcv(regfun, feature = 'feature', ratio = 0.5, alpha = 0.5, kernel = 'rbf', C = 1, gamma = 'auto',
           criterion = 'mse', K = 5, weights = 'uniform', N = 10, iters = 10):
    featureDir = '../Ngrams/' + feature + '/' #特征所在的目录

    # 计算标注的ngram和未标注的ngram的个数
    label = 0.0
    unlabel = 0.0
    for i in range(0,10):
        NewsName = unicode(featureDir + newsName[i] + '.txt', 'utf8')
        f = open(NewsName, 'r')
        for line in f:
            line = line.strip().split()
            if float(line[1]) > 0.5:
                label += 1
            else:
                unlabel += 1
        f.close()
    gate = 1    # 使用gate变量删去训练集中的一些未标注数据
    if label/unlabel < ratio:
        gate = label / (ratio * unlabel)

    score = 0.0
    number = 0.0
    for ite in range(0, iters):
        scorei = 0.0
        numberi = 0.0
        for vid in range(0, 10):
            #0~9中的第vid个作为验证集，其余的作为训练集
            X, Y = [], []
            for k in range(0, 10):
                if k != vid:
                    #每行的结构为：ngram的内容+人工标注的分数+7个特征
                    NewsName = unicode(featureDir+newsName[k]+'.txt','utf8')
                    f = open(NewsName, 'r')
                    for line in f:
                        line = line.strip().split()
                        for i in range(1, 9):
                            line[i] = float(line[i])
                        if line[1] < 0.5 and random.random() > gate:
                            continue
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
                reg = svr(X, Y, _kernel = kernel, _C = C, _gamma = gamma)
            elif id(regfun) == id(decisionTree):
                reg = decisionTree(X, Y, _criterion = criterion)
            elif id(regfun) == id(knnRegre):
                reg = knnRegre(X, Y, K = K, _weights = weights)
            elif id(regfun) == id(randomForestRegre):
                reg = randomForestRegre(X, Y, N = N, _criterion = criterion)
            pY = reg.predict(vX)
            tmpscore, tmpnumber = diff(pY, vY)
            scorei +=  tmpscore
            numberi += tmpnumber

        score += scorei/10.0
        number += numberi/10.0

    score /= float(iters)
    number /= float(iters)
    return score, number

def main():
    feature = ['feature']
    ratio = [0, 0.2, 0.3, 0.4, 0.5]
    alpha = [0.2*i for i in range(0,5)]
    kernel = ['rbf']
    C = [1,2,4,8,16]
    gama = ['auto']
    criterion = ['mse','friedman_mse']
    K = [3,4,5,6,7]
    weights = ['uniform','distance']
    N = [10,20,30]

    f1 = 0
    r1 = 0
    a1 = 0
    k1 = 0
    c1 = 0
    g1 = 0
    cr1 = 0
    k1 = 0
    w1 = 0
    n1 = 0
    score = 0.0
    number = 0.0


    print '线性回归调参'
    # 最优参数：feature: feature  ratio: 0
    # 最优结果：score: 14.5  number: 6.4
    for f in range(0,len(feature)):
        for r in range(0, len(ratio)):
            curScore, curNumber = tenfcv(linearRegre, feature = feature[f], ratio = ratio[r])
            print 'feature:',feature[f],'\tratio:',ratio[r],'\tscore:',curScore,'\tnumber:',curNumber
            if curScore > score:
                score = curScore
                number = curNumber
                f1 = f
                r1 = r
    print '最优参数：feature:',feature[f1],' ratio:',ratio[r1]
    print '最优结果：score:',score,' number:',number



    print '岭回归调参'
    # 最优参数：feature  ratio: 0.4  alpha: 0.6
    # 最优结果：score: 15.5  number: 6.8
    for f in range(0, len(feature)):
        for r in range(0, len(ratio)):
            for a in range(0, len(alpha)):
                curScore, curNumber = tenfcv(ridgeRegre, feature=feature[f], ratio=ratio[r],
                                             alpha = alpha[a], iters = 1)
                print 'feature:', feature[f], '\tratio:', ratio[r],'\talpha:', alpha[a], \
                    '\tscore:', curScore, '\tnumber:', curNumber
                if curScore > score:
                    score = curScore
                    number = curNumber
                    f1 = f
                    r1 = r
                    a1 = a
    print '最优参数：feature:', feature[f1], ' ratio:', ratio[r1], ' alpha:',alpha[a1]
    print '最优结果：score:', score, ' number:', number



    print 'svr调参'
    # 最优参数：feature: feature  ratio: 0.2  kernel: rbf  C: 8 gamma: auto
    # 最优结果：score: 19.0  number: 8.56
    for f in range(0, len(feature)):
        for r in range(1, len(ratio)):
            for k in range(0, len(kernel)):
                for c in range(0, len(C)):
                    for g in range(0, len(gama)):
                        curScore, curNumber = tenfcv(svr, feature=feature[f], ratio=ratio[r],kernel = kernel[k],
                                                     C = C[c], gamma = gama[g], iters = 1)
                        print 'feature:', feature[f], '\tratio:', ratio[r], '\tkernel:', kernel[k], '\tC:', C[c],\
                            'gamma:', gama[g], '\tscore:', curScore, '\tnumber:', curNumber
                        if curScore > score:
                            score = curScore
                            number = curNumber
                            f1 = f
                            r1 = r
                            k1 = k
                            c1 = c
                            g1 = g
    print '最优参数：feature:', feature[f1], ' ratio:', ratio[r1], ' kernel:', kernel[k1], ' C:', C[c1], 'gamma:', gama[g1]
    print '最优结果：score:', score, ' number:', number



    print '决策树调参'
    # 最优参数：feature: feature  ratio: 0  criterion: friedman_mse
    # 最优结果：score: 14.4  number: 6.76
    for f in range(0, len(feature)):
        for r in range(0, len(ratio)):
            for cr in range(0, len(criterion)):
                curScore, curNumber = tenfcv(decisionTree, feature=feature[f], ratio=ratio[r], criterion = criterion[cr], iters = 10)
                print 'feature:', feature[f], '\tratio:', ratio[r], '\tcriterion:', criterion[cr], \
                    '\tscore:', curScore, '\tnumber:', curNumber
                if curScore > score:
                    score = curScore
                    number = curNumber
                    f1 = f
                    r1 = r
                    cr1 = cr
    print '最优参数：feature:', feature[f1], ' ratio:', ratio[r1], ' criterion:', criterion[cr1]
    print '最优结果：score:', score, ' number:', number



    print 'knn调参'
    # 最优参数：feature: feature  ratio: 0.5  K: 7  weights: distance
    # 最优结果：score: 18.3  number: 8.2
    for f in range(0, len(feature)):
        for r in range(0, len(ratio)):
            for k in range(0, len(K)):
                for w in range(0, len(weights)):
                    curScore, curNumber = tenfcv(knnRegre, feature=feature[f], ratio=ratio[r], K = K[k], weights = weights[w])
                    print 'feature:', feature[f], '\tratio:', ratio[r], '\tK:', K[k], '\tweights:', weights[w], \
                        '\tscore:', curScore, '\tnumber:', curNumber
                    if curScore > score:
                        score = curScore
                        number = curNumber
                        f1 = f
                        r1 = r
                        k1 = k
                        w1 = w
    print '最优参数：feature:', feature[f1], ' ratio:', ratio[r1], ' K:', K[k1], ' weights:', weights[w1]
    print '最优结果：score:', score, ' number:', number



    print '随机森林调参'
    # 最优参数：feature: feature  ratio: 0  N: 30  criterion: friedman_mse
    # 最优结果：score: 18.25  number: 8.3
    for f in range(0, len(feature)):
        for r in range(0, len(ratio)):
            for n in range(0, len(N)):
                for cr in range(0, len(criterion)):
                    curScore, curNumber = tenfcv(randomForestRegre, feature=feature[f], ratio=ratio[r], N=N[n],
                                                 criterion=criterion[cr], iters=1)
                    print 'feature:', feature[f], '\tratio:', ratio[r], '\tN:', N[n], '\tcriterion:', criterion[cr], \
                        '\tscore:', curScore, '\tnumber:', curNumber
                    if curScore > score:
                        score = curScore
                        number = curNumber
                        f1 = f
                        r1 = r
                        n1 = n
                        cr1 = cr
    print '最优参数：feature:', feature[f1], ' ratio:', ratio[r1], ' N:', N[n1], ' criterion:', criterion[cr1]
    print '最优结果：score:', score, ' number:', number


if __name__ == '__main__':
    main()

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

# 用于评价回归效果，tY是预测分数，Y是人工打分
# 返回score(前20个的总得分)，P@5，P@10，P@20以及回归分数排序后的列表
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
        for j in range(i+1, l):
            if tY[index[i]] < tY[index[j]]:
                index[i], index[j] = index[j], index[i]

    # 计算score
    cnt1, cnt2, cnt3 = 0, 0, 0
    for i in range(0, 20):
        if index[i] in id1:
            cnt1 += 1
        elif index[i] in id2:
            cnt2 += 1
        elif index[i] in id3:
            cnt3 += 1
    score = cnt1 + 2*cnt2 + 3*cnt3

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

    return score, P_5, P_10, P_20

newsName = ['hpv疫苗','iPhone X', '乌镇互联网大会','九寨沟7.0级地震','俄罗斯世界杯',\
'双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',\
'王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',\
'萨德系统 中韩', '雄安新区', '榆林产妇坠楼']


# 采用二十折交叉验证，迭代iters次，计算得分，命中数目
# regfun指定回归方法，feature指定特征文件，ratio指定标注和未标注的比例，iters指定迭代次数，后面都是各模型自己的参数
# oneg为1，则训练集中包括onegram，否则不包括。
def tenfcv(regfun, feature = 'feature', cho = [1], ratio = 0.5, alpha = 0.5, kernel = 'rbf', C = 1, gamma = 'auto',
           criterion = 'mse', K = 5, weights = 'uniform', N = 10, iters = 5):
    featureDir = '../Ngrams/' + feature + '/' #特征所在的目录
    featureSize = 12

    # 计算标注的ngram和未标注的ngram的个数
    label = 0.0
    unlabel = 0.0
    for i in range(0,20):
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

    score, P_5, P_10, P_20 = 0.0, 0.0, 0.0, 0.0
    for ite in range(0, iters):
        scorei, p_5, p_10, p_20 = 0.0, 0.0, 0.0, 0.0
        for vid in range(0, 20):
            #0~20中的第vid个作为验证集，其余的作为训练集
            X, Y = [], []
            for k in range(0, 20):
                if k != vid:
                    #每行的结构为：ngram的内容+人工标注的分数+7个特征
                    NewsName = unicode(featureDir+newsName[k]+'.txt','utf8')
                    f = open(NewsName, 'r')
                    for line in f:
                        line = line.strip().split()
                        for i in range(1, featureSize+2):
                            line[i] = float(line[i])
                        if line[1] < 0.5 and random.random() > gate:
                            continue
                        #去除特征3,4,10维，对应下标4,5,11
                        tmpx = []
                        for xi in range(0, featureSize):
                            if (xi+1) in cho:
                                tmpx.append(line[xi+2])
                        X.append(tmpx)
                        Y.append(line[1])
                    f.close()

            #使用第vid个作为验证集
            vX, vY = [], []
            content = []
            NewsName = unicode(featureDir+newsName[vid]+'.txt','utf8')
            f = open(NewsName, 'r')
            for line in f:
                line = line.strip().split()
                for i in range(1, featureSize+2):
                    line[i] = float(line[i])
                #去除特征3,4,10维，对应下标4,5,11
                tmpx = []
                for xi in range(0, featureSize):
                    if (xi+1) in cho:
                        tmpx.append(line[xi+2])
                vX.append(tmpx)
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
            tmpscore, tmp5, tmp10, tmp20 = evaluate(pY, vY)
            scorei +=  tmpscore
            p_5 += tmp5
            p_10 += tmp10
            p_20 += tmp20

        score += scorei/20.0
        P_5 += p_5/20.0
        P_10 += p_10/20.0
        P_20 += p_20/20.0

    score /= float(iters)
    P_5 /= float(iters)
    P_10 /= float(iters)
    P_20 /= float(iters)
    return score, P_5, P_10, P_20

def main():
    # 注：不去掉onegram，iters = 1， 最优的情况为：
    # 线性回归：    最优参数：feature: feature  ratio: 0.2
    #               最优结果：score: 18.7  P@5: 0.43  P@10: 0.415  P@20: 0.3875
    # 岭回归：      最优参数：feature: feature  ratio: 0.2  alpha: 0.4
    #               最优结果：score: 18.6  P@5: 0.43  P@10: 0.42  P@20: 0.3875
    # svr：         最优参数：feature: feature  ratio: 0.4  kernel: rbf  C: 16 gamma: auto
    #               最优结果：score: 23.2  P@5: 0.47  P@10: 0.485  P@20: 0.49
    # 决策树：      最优参数：feature: feature  ratio: 0.2  criterion: friedman_mse
    #               最优结果：score: 13.54  P@5: 0.286  P@10: 0.3005  P@20: 0.3105
    # knn：         最优参数：feature: feature  ratio: 0.6  K: 6  weights: uniform
    #               最优结果：score: 18.25  P@5: 0.4  P@10: 0.4  P@20: 0.4
    # 随机森林：    最优参数：feature: feature  ratio: 0.6  N: 30  criterion: friedman_mse
    #               最优结果：score: 21.55  P@5: 0.59  P@10: 0.55  P@20: 0.48
    # 删除ce特征，最优化情况为：
    # svr:最优参数：feature: feature  ratio: 0.8  kernel: rbf  C: 16 gamma: auto
    #     最优结果：score: 24.25  P@5: 0.48  P@10: 0.495  P@20: 0.5025
    # knn:最优参数：feature: feature  ratio: 0  K: 4  weights: uniform
    #     最优结果：score: 17.55  P@5: 0.44  P@10: 0.44  P@20: 0.3975
    # 随机森林：最优参数：feature: feature  ratio: 0.2  N: 30  criterion: friedman_mse
    # 最优结果：score: 21.25  P@5: 0.55  P@10: 0.55  P@20: 0.4675


    # feature = ['feature_add2d']
    feature = ['feature_12', 'feature_12cut']
    choose = [[1,2,3,4,5,6,7],
              [1,2,3,4,5,6,7,8,9],
              [1,2,3,4,5,6,7,11,12],
              [1,2,3,4,5,6,7,8,9,11,12]]
    # ratio = [0, 0.2, 0.4, 0.6, 0.8]
    ratio = [0.3, 0.4, 0.5]
    alpha = [0.2*i for i in range(0,5)]
    kernel = ['rbf','poly']
    C = [1,2,4,6,8]
    gama = ['auto']
    # criterion = ['mse','friedman_mse']
    criterion = ['mse']
    K = [3,4,5,6,7]
    weights = ['uniform','distance']
    N = [20,25,30,35,40]
    '''
    f1, r1, a1, k1, c1, g1, cr1, k1, w1, n1 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    score, P_5, P_10, P_20 = 0.0, 0.0, 0.0, 0.0

    print '线性回归调参'
    # 最优参数：
    # 最优结果：
    for f in range(0,len(feature)):
        for r in range(0, len(ratio)):
            curScore, cur5, cur10, cur20 = tenfcv(linearRegre, feature = feature[f], ratio = ratio[r])
            print 'feature:',feature[f],'\tratio:',ratio[r],'\tscore:',curScore,'\tP@20:',cur20
            if cur5 > P_5 or (cur5 == P_5 and cur10 > P_10) or (cur5 == P_5 and cur10 == P_10 and cur20 > P_20):
                score = curScore
                P_5 = cur5
                P_10 = cur10
                P_20 = cur20
                f1 = f
                r1 = r
    print '最优参数：feature:',feature[f1],' ratio:',ratio[r1]
    print '最优结果：score:',score,' P@5:',P_5,' P@10:',P_10,' P@20:', P_20

    f1, r1, a1, k1, c1, g1, cr1, k1, w1, n1 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    score, P_5, P_10, P_20 = 0.0, 0.0, 0.0, 0.0

    print '岭回归调参'
    # 最优参数：
    # 最优结果：
    for f in range(0, len(feature)):
        for r in range(0, len(ratio)):
            for a in range(0, len(alpha)):
                curScore, cur5, cur10, cur20 = tenfcv(ridgeRegre, feature=feature[f], ratio=ratio[r],
                                             alpha = alpha[a], iters = 1)
                print 'feature:', feature[f], '\tratio:', ratio[r],'\talpha:', alpha[a], \
                    '\tscore:', curScore,'\tP@20:',cur20
                if cur5 > P_5 or (cur5 == P_5 and cur10 > P_10) or (cur5 == P_5 and cur10 == P_10 and cur20 > P_20):
                    score = curScore
                    P_5 = cur5
                    P_10 = cur10
                    P_20 = cur20
                    f1 = f
                    r1 = r
                    a1 = a
    print '最优参数：feature:', feature[f1], ' ratio:', ratio[r1], ' alpha:',alpha[a1]
    print '最优结果：score:', score,' P@5:',P_5,' P@10:',P_10,' P@20:', P_20
    '''

    f1, r1, a1, k1, c1, g1, cr1, k1, w1, n1, ch1 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    score, P_5, P_10, P_20 = 0.0, 0.0, 0.0, 0.0

    print 'svr调参'
    # 最优参数：
    # 最优结果：
    for f in range(0, len(feature)):
        for chi in range(0, len(choose)):
            for r in range(0, len(ratio)):
                for k in range(0, len(kernel)):
                    for c in range(0, len(C)):
                        for g in range(0, len(gama)):
                            curScore, cur5, cur10, cur20 = tenfcv(svr, feature=feature[f], cho = choose[chi], ratio=ratio[r],kernel = kernel[k],
                                                         C = C[c], gamma = gama[g])
                            print 'feature:', feature[f], 'choose:', chi, '\tratio:', ratio[r], '\tkernel:', kernel[k], '\tC:', C[c],\
                                'gamma:', gama[g], '\tscore:', curScore,'\tP@20:',cur20
                            if cur5 > P_5 or (cur5 == P_5 and cur10 > P_10) or (cur5 == P_5 and cur10 == P_10 and cur20 > P_20):
                                score = curScore
                                P_5 = cur5
                                P_10 = cur10
                                P_20 = cur20
                                f1 = f
                                r1 = r
                                k1 = k
                                c1 = c
                                g1 = g
                                ch1 = chi
    print '最优参数：feature:', feature[f1], 'choose:', ch1, ' ratio:', ratio[r1], ' kernel:', kernel[k1], ' C:', C[c1], 'gamma:', gama[g1]
    print '最优结果：score:', score,' P@5:',P_5,' P@10:',P_10,' P@20:', P_20

    '''
    f1, r1, a1, k1, c1, g1, cr1, k1, w1, n1 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    score, P_5, P_10, P_20 = 0.0, 0.0, 0.0, 0.0

    print '决策树调参'
    # 最优参数：
    # 最优结果：
    for f in range(0, len(feature)):
        for r in range(0, len(ratio)):
            for cr in range(0, len(criterion)):
                curScore, cur5, cur10, cur20 = tenfcv(decisionTree, feature=feature[f], ratio=ratio[r], criterion = criterion[cr], iters = 10)
                print 'feature:', feature[f], '\tratio:', ratio[r], '\tcriterion:', criterion[cr], \
                    '\tscore:', curScore,'\tP@20:',cur20
                if cur5 > P_5 or (cur5 == P_5 and cur10 > P_10) or (cur5 == P_5 and cur10 == P_10 and cur20 > P_20):
                    score = curScore
                    P_5 = cur5
                    P_10 = cur10
                    P_20 = cur20
                    f1 = f
                    r1 = r
                    cr1 = cr
    print '最优参数：feature:', feature[f1], ' ratio:', ratio[r1], ' criterion:', criterion[cr1]
    print '最优结果：score:', score,' P@5:',P_5,' P@10:',P_10,' P@20:', P_20
    '''
    '''
    f1, r1, a1, k1, c1, g1, cr1, k1, w1, n1 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    score, P_5, P_10, P_20 = 0.0, 0.0, 0.0, 0.0

    print 'knn调参'
    # 最优参数：
    # 最优结果：
    for f in range(0, len(feature)):
        for r in range(0, len(ratio)):
            for k in range(0, len(K)):
                for w in range(0, len(weights)):
                    curScore, cur5, cur10, cur20 = tenfcv(knnRegre, feature=feature[f], ratio=ratio[r], K = K[k], weights = weights[w])
                    print 'feature:', feature[f], '\tratio:', ratio[r], '\tK:', K[k], '\tweights:', weights[w], \
                        '\tscore:', curScore,'\tP@20:',cur20
                    if cur5 > P_5 or (cur5 == P_5 and cur10 > P_10) or (cur5 == P_5 and cur10 == P_10 and cur20 > P_20):
                        score = curScore
                        P_5 = cur5
                        P_10 = cur10
                        P_20 = cur20
                        f1 = f
                        r1 = r
                        k1 = k
                        w1 = w
    print '最优参数：feature:', feature[f1], ' ratio:', ratio[r1], ' K:', K[k1], ' weights:', weights[w1]
    print '最优结果：score:', score,' P@5:',P_5,' P@10:',P_10,' P@20:', P_20
    '''

    f1, r1, a1, k1, c1, g1, cr1, k1, w1, n1, ch1 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    score, P_5, P_10, P_20 = 0.0, 0.0, 0.0, 0.0

    print '随机森林调参'
    # 最优参数：
    # 最优结果：
    for f in range(0, len(feature)):
        for chi in range(0, len(choose)):
            for r in range(0, len(ratio)):
                for n in range(0, len(N)):
                    for cr in range(0, len(criterion)):
                        curScore, cur5, cur10, cur20 = tenfcv(randomForestRegre, feature=feature[f], cho = choose[chi], ratio=ratio[r], N=N[n],
                                                     criterion=criterion[cr])
                        print 'feature:', feature[f], '\tratio:', ratio[r], '\tchoose:', chi, '\tN:', N[n], '\tcriterion:', criterion[cr], \
                            '\tscore:', curScore,'\tP@20:',cur20
                        if cur5 > P_5 or (cur5 == P_5 and cur10 > P_10) or (cur5 == P_5 and cur10 == P_10 and cur20 > P_20):
                            score = curScore
                            P_5 = cur5
                            P_10 = cur10
                            P_20 = cur20
                            f1 = f
                            r1 = r
                            n1 = n
                            cr1 = cr
                            ch1 = chi
    print '最优参数：feature:', feature[f1], 'choose:', ch1, ' ratio:', ratio[r1], ' N:', N[n1], ' criterion:', criterion[cr1]
    print '最优结果：score:', score,' P@5:',P_5,' P@10:',P_10,' P@20:', P_20


if __name__ == '__main__':
    main()

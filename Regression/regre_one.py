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
           criterion = 'mse', K = 5, weights = 'uniform', N = 10, iters = 10):
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
                            if xi in cho:
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
                    if xi in cho:
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

    s = ['tfidf', 'len', 'ics', 'ce', 'ide', 'inTitle', 'n', 'lda1', 'lda2', 'df', 'cont', 'ncnt']
    for i in range(0, 12):
        print s[i]
        ch = [i]
        curScore, cur5, cur10, cur20 = tenfcv(linearRegre, feature = 'feature_12', cho = ch, ratio = 0.0)
        print 'linear', cur5, cur10, cur20

        curScore, cur5, cur10, cur20 = tenfcv(svr, feature='feature_12', cho = ch, ratio=0.2,kernel = 'rbf',
                                     C = 4, gamma = 1.0)
        print 'svr', cur5, cur10, cur20

        curScore, cur5, cur10, cur20 = tenfcv(randomForestRegre, feature='feature_12', cho = ch, ratio=0.4, N=30,
                                     criterion='mse')
        print 'randomforest', cur5, cur10, cur20

if __name__ == '__main__':
    main()

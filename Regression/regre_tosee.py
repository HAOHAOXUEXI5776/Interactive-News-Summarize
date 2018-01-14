#coding:utf-8

# 使用调好的参数进行回归，将回归结果排序后输出到文件中
# 目前的回归方法与对应参数：
# 线性回归：feature: feature  ratio: 0
# svr：feature: feature  ratio: 0.2  kernel: rbf  C: 8 gamma: 0.5
# knn回归：feature: feature  ratio: 0.5  K: 7  weights: distance
# 随机森林回归：feature: feature  ratio: 0  N: 30  criterion: friedman_mse

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
# 返回得分score = Σcnti*i
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
    score = cnt1 + 2*cnt2 + 3*cnt3
    return score, index[0:topn]


newsName = ['hpv疫苗','iPhone X', '乌镇互联网大会','九寨沟7.0级地震','俄罗斯世界杯',\
'双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏']

#采用十折交叉验证，迭代iters次，每次迭代，轮流将9个作为训练集，1个作为测试集
#得到十个分数，将10个分数平均得到该次迭代的分数。最后再对iter进行平均，作为
#该模型的得分。得分越高，说明越准确。
def tenfcv(regfun, feature = 'feature', ratio = 0.5, alpha = 0.5, kernel = 'rbf', C = 1, gamma = 'auto',
           criterion = 'mse', K = 5, weights = 'uniform', N = 10):
    featureDir = '../Ngrams/' + feature + '/' #特征所在的目录

    # 计算标注的ngram和未标注的ngram的个数
    label = 0.0
    unlabel = 0.0
    for i in range(0, 10):
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

    scorei = 0.0
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

        outname = ""
        if id(regfun) == id(linearRegre):
            reg = linearRegre(X, Y)
            outname = './see/线性回归/'+newsName[vid]+'.txt'
        elif id(regfun) == id(ridgeRegre):
            reg = ridgeRegre(X, Y, alpha)
            outname = './see/岭回归/'+newsName[vid]+'.txt'
        elif id(regfun) == id(svr):
            reg = svr(X, Y, _kernel=kernel, _C=C, _gamma=gamma)
            outname = './see/svr/'+newsName[vid]+'.txt'
        elif id(regfun) == id(decisionTree):
            reg = decisionTree(X, Y, _criterion=criterion)
            outname = './see/决策树/' + newsName[vid] + '.txt'
        elif id(regfun) == id(knnRegre):
            reg = knnRegre(X, Y, K=K, _weights=weights)
            outname = './see/knn/' + newsName[vid] + '.txt'
        elif id(regfun) == id(randomForestRegre):
            reg = randomForestRegre(X, Y, N=N, _criterion=criterion)
            outname = './see/随机森林/' + newsName[vid] + '.txt'

        pY = reg.predict(vX)
        tmpscore, topnid = diff(pY, vY)
        scorei +=  tmpscore

        f = open(unicode(outname, 'utf8'), 'w')
        topn = 20
        for i in range(0, topn):
            curid = topnid[i]
            f.write(content[curid]+' '+str(pY[curid])+' '+str(vY[curid])+'\n')
        f.close()
    return scorei/10.0

def main():

    feature = ['feature','feature1','feature2']
    ratio = [0, 0.2, 0.3, 0.4, 0.5]
    alpha = [0.2 * i for i in range(0, 5)]
    kernel = ['poly','rbf']
    C = [1, 2, 4, 8, 16]
    gama = ['auto']
    criterion = ['mse', 'friedman_mse']
    K = [3, 5, 9, 15, 20]
    weights = ['uniform', 'distance']
    N = [10, 20, 30]

    # 线性回归
    score = tenfcv(linearRegre, feature = feature[0], ratio = ratio[0])
    print 'linear_regression的分数为：', score

    # svr回归
    score = tenfcv(svr, feature=feature[0], ratio=ratio[1],kernel = kernel[1], C = C[3], gamma = 0.5)
    print 'svr分数为：', score

    # knn回归
    score = tenfcv(knnRegre, feature=feature[0], ratio=ratio[4], K = K[4], weights = weights[1])
    print 'knn分数为：', score

    #随机森林回归
    score = tenfcv(randomForestRegre, feature=feature[0], ratio=ratio[0], N=N[2],criterion=criterion[1])
    print 'random_forest分数为：', score

if __name__== "__main__":
    main()





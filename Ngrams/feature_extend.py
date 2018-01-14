# coding:utf-8

# 相似的n-gram应有相近的分数，相近的特征，所以在原特征的基础上进行修改（平滑），两种平滑方式：
# 1.对于一个n-gram，将与之最相似的几个n-gram的特征加权平均后放到原特征之后，特征维数 * 2，结果存于/feature1
# 2.将一个n-gram和与之最相似的几个n-gram的特征一起加权平均，作为最终特征，特征维数不变，结果存于/feature2

newsName = ['德国大选', '俄罗斯世界杯', '功守道', '九寨沟7.0级地震', '权力的游戏',
            '双十一购物节', '乌镇互联网大会', '战狼2', 'hpv疫苗', 'iPhone X',
            '李晨求婚范冰冰', '江歌刘鑫','王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园',
            '绝地求生 吃鸡', '英国脱欧','萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

smoothRange = 4     # 只考虑最相似的4个词（包括这个词本身）

# 读原特征以及相关信息
def readFeature(news):
    ngram = []      # 该新闻的所有ngram，每个ngram是一个字符串数组，1-3个元素
    ngramLen = []   # 每个ngram的长度（不是n）
    score = []      # 人工标注的分数
    feature = []    # 特征
    f = open('feature/' + news + '.txt','r')
    for line in f:
        line = line.strip().split()
        ngram.append(line[0].split('+'))
        ngramLen.append(len(line[0].replace('+','')))
        score.append(line[1])
        feature.append(line[2:])
    f.close()
    return ngram,ngramLen,score,feature

# 计算两个ngram的相似度，基于uni-gram的共现，sim(abc,bcd) = (len(bc)/len(abc) + len(bc)/len(bcd))/2
def computeSim(ngram1,l1,ngram2,l2):
    l1 = float(l1)
    l2 = float(l2)
    l3 = 0
    for w1 in ngram1:
        for w2 in ngram2:
            if w1 == w2:
                l3 += len(w1)
    sim = (l3/l1 + l3/l2)/2
    return  sim

# 根据原特征和相似度计算修改后的特征
def computeFeature(idx,ori_feature,sortedSim):
    vecDim = len(ori_feature[idx])  # 原始特征维数
    extend = [.0 for i in range(0,vecDim)]
    sumSim = .0     # 归一化分母
    for i in range(0,smoothRange):
        curIdx = sortedSim[i][0]
        curSim = sortedSim[i][1]
        sumSim += curSim
        for j in range(0,vecDim):
            extend[j] += curSim * float(ori_feature[curIdx][j])
    for i in range(0,vecDim):
        extend[i] /= sumSim
    return ori_feature[idx] + extend, extend

# 将新特征值写回文件
def writeBack(news,ngram,score,feature1,feature2):
    l = len(ngram)
    f1 = open('feature1/' + news + '.txt','w')
    for i in range(0,l):
        nl = len(ngram[i])
        f1.write(ngram[i][0])
        for j in range(1,nl):
            f1.write('+' + str(ngram[i][j]))
        f1.write(' ' + str(score[i]))
        for fea in feature1[i]:
            f1.write(' ' + str(fea))
        f1.write('\n')
    f1.close()
    f2 = open('feature2/' + news + '.txt', 'w')
    for i in range(0, l):
        nl = len(ngram[i])
        f2.write(ngram[i][0])
        for j in range(1, nl):
            f2.write('+' + str(ngram[i][j]))
        f2.write(' ' + str(score[i]))
        for fea in feature2[i]:
            f2.write(' ' + str(fea))
        f2.write('\n')
    f2.close()

# main，依次处理每一个新闻
for news in newsName:
    print news
    ngram,ngramLen,score,ori_feature = readFeature(news)
    l = len(ngram)
    feature1 = []
    feature2 = []
    for i in range(0,l):    # 依次计算每个ngram
        curSim = {}         # 记录i号ngram和其他所有ngram的相似度
        for j in range(0,l):
            curSim[j] = computeSim(ngram[i],ngramLen[i],ngram[j],ngramLen[j])
        sortedSim = sorted(curSim.iteritems(), key=lambda d:d[1], reverse=True) # 相似度由高到低排序，相似度最高的就是自己
        curFeature1,curFeature2 = computeFeature(i,ori_feature,sortedSim)       # 计算修改后的特征
        feature1.append(curFeature1)
        feature2.append(curFeature2)
    writeBack(news,ngram,score,feature1,feature2)

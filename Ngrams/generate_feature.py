#coding:utf-8

def main():
    f = open('punc.txt', 'r')
    punc = {}
    for line in f:
        punc[line.strip()] = 0
    f.close()

    featureDir = 'Processed/feature/'
    labelDir = 'Processed/label/'
    outDir = 'feature/'
    news = ['hpv疫苗','iPhone X', '乌镇互联网大会','九寨沟7.0级地震','俄罗斯世界杯',
        '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
        '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
        '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']
    for i in range(0, 20):
        newsName = news[i]
        ff = open(unicode(featureDir+newsName+'.txt', 'utf8'), 'r')
        fl = open(unicode(labelDir+newsName+'.txt', 'utf8'), 'r')
        fw = open(unicode(outDir+newsName+'.txt', 'utf8'), 'w')
        ngram = []
        score = []
        ffs, fls = ff.readlines(), fl.readlines()
        assert len(ffs) == len(fls)
        for ngram_score in fls:
            ngram_score = ngram_score.strip().split()
            ngram.append(ngram_score[0])
            score.append(ngram_score[1])

        features = []
        for ngram_features in ffs:
            ngram_features = ngram_features.strip().split()
            tmp = []
            for j in range(1, 8):
                tmp.append(float(ngram_features[j]))
            features.append(tmp)

        #规范化特征
        vecSize = 7
        minf = [1e20 for j in range(0, vecSize)]
        maxf = [1e-20 for j in range(0, vecSize)]
        l = len(fls)
        for j in range(0, 7):
            for k in range(0, l):
                if features[k][j] < minf[j]:
                    minf[j] = features[k][j]
                if features[k][j] > maxf[j]:
                    maxf[j] = features[k][j]
        for j in range(0, 7):
            if maxf[j]-minf[j] == 0:
                print i
                exit()
        for j in range(0, 7):
            for k in range(0, l):
                features[k][j] = (features[k][j]-minf[j])/(maxf[j]-minf[j])

        #输出到feature/中
        for k in range(0, l):
            tmp_ngram = ngram[k].split('+')
            if len(tmp_ngram) == 3 and tmp_ngram[1] in punc:
                continue
            if tmp_ngram[0] == '★':
                continue
            fw.write(ngram[k]+' '+score[k])
            for j in range(0, 7):
                fw.write(' '+str(features[k][j]))
            fw.write('\n')
        ff.close()
        fl.close()
        fw.close()

if __name__ == '__main__':
    main()

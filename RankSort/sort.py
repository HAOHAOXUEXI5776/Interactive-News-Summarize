#coding: utf-8

import gensim
from pyltp import Segmentor
import os
from math import *

qin = 1 #改成0是刘辉的路径，否则是秦文涛的路径
# 加载分词模型
segmentor = Segmentor()
if qin == 1:
    segmentor.load('D:/coding/Python2.7/ltp_data_v3.4.0/cws.model')
    model = gensim.models.Word2Vec.load('../Sentence/model_qin')
else:
    segmentor.load('/Users/liuhui/Desktop/实验室/LTP/ltp_data_v3.4.0/cws.model')
    model = gensim.models.Word2Vec.load('../Sentence/model')
vec_size = 100

stoplist = {}
f = open('../stopword.txt', 'r')
for line in f:
    word = line.strip()
    stoplist[word] = 1
f.close()

class Sent:
    def __init__(self, _newsid, _globalid, _paraid, _localid, _sentnum, _content, _vec):
        self.newsid = _newsid        #该句所属新闻编号
        self.globalid = _globalid    #该句在该篇新闻的第几句
        self.paraid = _paraid        #该句在该篇新闻的第几段
        self.localid = _localid      #该句在所属段的第几句
        self.sentnum = _sentnum       #该句所在段有多少句
        self.content = _content
        self.vec = _vec

# 计算几个向量的平均向量
def mean_vec(vec_list):
    if len(vec_list) == 0:
        return [0.0 for k in range(0, vec_size)]
    result = [0.0 for k in range(0, len(vec_list[0]))]
    for vec in vec_list:
        for k in range(0, len(result)):
            result[k] += vec[k]
    for k in range(0, len(result)):
        result[k] /= len(vec_list)
    return result

# 计算两个向量的余弦相似度
def cos_similarity(vec1, vec2):
    result = 0.0
    vec1_size = 0.0
    vec2_size = 0.0
    for k in range(0, len(vec1)):
        result += vec1[k] * vec2[k]
        vec1_size += vec1[k] * vec1[k]
        vec2_size += vec2[k] * vec2[k]
    if vec1_size < 1e-10 or vec2_size < 1e-10:
        return 0.0
    result /= sqrt(vec1_size * vec2_size)
    return result

'''
#根据块的前后关系behind得到整体的排序
#首先根据blocks[0]，将其余的blocks划分到它的两侧，对两侧递归处理
#排序结果置于li中
def recursort(behind, li, i, index, offset):
    if len(index) == 0:
        return
    if len(index) == 1:
        li[i] = offset
        return
    r = [] #在i右边的
    l = [] #在i左边的
    for k in index:
        if k == i:
            continue
        if behind[i][k] == 1:
            l.append(k)
        elif behind[i][k] == 0:
            r.append(k)
    li[i] = offset + len(l) #i放在第len(l)的位置
    if len(r) > 0:
        recursort(behind, li, r[0], r, li[i]+1)
    if len(l) > 0:
        recursort(behind, li, l[0], l, offset)
'''

news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

outDir = 'summary/'
for news in news_name:
    print news
    path = outDir+news
    if not os.path.exists(unicode(path, 'utf8')):
        os.mkdir(unicode(path, 'utf8'))

    '''
    #读取所有的新闻
    new = []   #记录所有新闻对应的句子
    for i in range(0, 100):
        #默认最多100篇新闻
        t = []
        new.append(t)
    f = open(unicode('../Sentence/sentence/'+news+'/sentence.txt','utf8'), 'r')
    while True:
        nums = f.readline()
        if len(nums) == 0:
            break
        content = f.readline().strip()
        nums = nums.strip().split()
        nums = [int(num) for num in nums]
        words = segmentor.segment(content)
        word_vec_list = []
        for word in words:
            if word not in stoplist and word in model:
                word_vec_list.append(model[word])
        sent = Sent(nums[0],nums[1],nums[2],nums[3],nums[4],content,mean_vec(word_vec_list))
        new[nums[0]-1].append(sent)
    f.close()

    #统计有多少篇新闻
    newscnt = 0
    for i in range(0, 100):
        if len(new[99-i]) != 0:
            newscnt = 100-i
            break
    '''

    #读入所有的标题,计算其向量置于title中
    title = []
    f = open(unicode('../Sentence/sentence/'+news+'/title.txt','utf8'), 'r')
    for line in f:
        words = segmentor.segment(line.strip())
        word_vec_list = []
        for word in words:
            if word not in stoplist and word in model:
                word_vec_list.append(model[word])
        title.append(mean_vec(word_vec_list))
    f.close()

    print '标题数：', len(title)

    #读入所有标签
    f = open(unicode('../Sentence/label/'+news+'/label.txt', 'utf8'), 'r')
    labels = [line.strip().replace('+', '') for line in f]
    f.close()

    for label in labels:
        print label
        #读取排序后的块
        blocks = [] #记录该标签对应的块
        f = open(unicode('blockscore/'+news+'/'+label+'.txt', 'utf8'), 'r')
        while True:
            n = f.readline() #第一行记录了下面几个句子是一个块
            if len(n) == 0:
                break
            block = []
            n = int(n.strip())
            for i in range(0, n):
                nums = f.readline()
                nums = nums.strip().split()
                nums = [int(num) for num in nums]
                content = f.readline().strip()
                words = segmentor.segment(content)
                word_vec_list = []
                for word in words:
                    if word not in stoplist and word in model:
                        word_vec_list.append(model[word])
                sent = Sent(nums[0],nums[1],nums[2],nums[3],nums[4],content,mean_vec(word_vec_list))
                block.append(sent)
            blocks.append(block)
        f.close()
        blockcnt = len(blocks)

        #选择blocks中的若干块，使得其总句子数在大于10的情况下尽可能小
        tolsent, endblock = 0, 0
        while tolsent < 10 and endblock < blockcnt:
            tolsent += len(blocks[endblock])
            endblock += 1
        assert endblock != 0
        #按照标题的相似度将第0~endblock-1块分为几类
        cluster = []
        use = [0 for i in range(0, endblock)]
        for i in range(0, endblock):
            if use[i] == 1:
                continue
            newid_i = blocks[i][0].newsid - 1
            tcluster = [blocks[i]]
            use[i] = 1
            for j in range(i+1, endblock):
                newid_j = blocks[j][0].newsid - 1
                if use[j] == 0 and cos_similarity(title[newid_i], title[newid_j]) > 0.6:
                    tcluster.append(blocks[j])
                    use[j] = 1
            cluster.append(tcluster)
        f = open(unicode(outDir+news+'/'+label+'.txt', 'utf8'), 'w')
        #每个类进行排序
        for tcluster in cluster:
            l = len(tcluster)
            sort = [i for i in range(0, l)]
            #块在全文越靠前的位置，在段越靠前的位置，越要排到前头
            #若位置因素影响不大，则考虑时间因素，新闻标号越小，发生的时间越晚，越往后排
            for i in range(0, l):
                for j in range(i+1, l):
                    senti, sentj = tcluster[sort[i]][0], tcluster[sort[j]][0]
                    if senti.globalid > sentj.globalid or \
                       (senti.globalid == sentj.globalid and senti.localid > sentj.localid) or \
                       (senti.globalid == sentj.globalid and senti.localid == sentj.localid and senti.newsid < sentj.newsid):
                        sort[i], sort[j] = sort[j], sort[i]
            for i in range(0, l):
                for sent in tcluster[sort[i]]:
                    f.write(sent.content)
                f.write('\n')
        f.close()


        '''
        cadisent = []
        #选取blocks中的前10句子作为候选
        tolsent, endblock = 0, 0
        while tolsent != 10 and endblock < blockcnt:
            curblock = blocks[endblock]
            if tolsent + len(curblock) >= 10:
                left = 10 - tolsent
                for i in range(0, left):
                    cadisent.append(curblock[i])
                    tolsent += 1
            else:
                for sent in curblock:
                    cadisent.append(sent)
                    tolsent += 1
            endblock += 1

        #计算候选句子两两间的前后关系
        #对每个句子，计算其他的句子是放在它的前头还是后头
        #behind[i][j] = 1（或behind[j][i] = 0）(i!=j)，则说明i应放在j之后
        behind = []
        for i in range(0, tolsent):
            tmp = ['#' for i in range(0, tolsent)]
            behind.append(tmp)
        for i in range(0, tolsent):
            for j in range(i+1, tolsent):
                print i, j
                senti, sentj = cadisent[i], cadisent[j]
                if senti.newsid == sentj.newsid:
                    #二者在同一篇新闻内，则按照其原顺序排序
                    if senti.globalid < sentj.globalid:
                        behind[i][j], behind[j][i] = 0, 1
                    else:
                        behind[i][j], behind[j][i] = 1, 0
                else:
                    #在senti的新闻内，sentj与senti前面和后面的最大相似度
                    senti_front, senti_behind = 0.0, 0.0
                    nidi, sidi = senti.newsid, senti.globalid
                    for sent in new[nidi]:
                        if sent.globalid < sidi:
                            senti_front = max(senti_front, cos_similarity(sent.vec, sentj.vec))
                        elif sent.globalid > sidi:
                            senti_behind = max(senti_behind, cos_similarity(sent.vec, sentj.vec))

                    #在sentj的新闻内，senti与sentj前面和后面的最大相似度
                    sentj_front, sentj_behind = 0.0, 0.0
                    nidj, sidj = sentj.newsid, sentj.globalid
                    for sent in new[nidj]:
                        if sent.globalid < sidj:
                            sentj_front = max(sentj_front, cos_similarity(sent.vec, senti.vec))
                        elif sent.globalid > sidj:
                            sentj_behind = max(sentj_behind, cos_similarity(sent.vec, senti.vec))

                    #在除了senti和sentj的新闻k内，找到与senti和sentj的最大相似度的句子
                    behindij = -1
                    max_simi = 0.0
                    for nid in range(0, newscnt):
                        if nid == nidi or nid == nidj:
                            continue
                        simi_i, simi_j = 0.0, 0.0
                        sent_i, sent_j = None, None
                        for sent in new[nid]:
                            tmp_simii = cos_similarity(sent.vec, senti.vec)
                            tmp_simij = cos_similarity(sent.vec, sentj.vec)
                            if tmp_simii > simi_i:
                                simi_i = tmp_simii
                                sent_i = sent
                            if tmp_simij > simi_j:
                                simi_j = tmp_simij
                                sent_j = sent
                        if simi_i+simi_j > max_simi:
                            max_simi = simi_i+simi_j
                            if sent_i.globalid > sent_j.globalid:
                                behindij = 1
                            elif sent_i.globalid < sent_j.globalid:
                                behindij = 0

                    tmplist = [senti_front, senti_behind, sentj_front, sentj_behind, max_simi/2.0]

                    #基数排序，看哪个相似度最大
                    idx = [ki for ki in range(0, 5)]
                    for ki in range(0, 5):
                        for kj in range(ki+1, 5):
                            if tmplist[idx[ki]] < tmplist[idx[kj]]:
                                idx[ki], idx[kj] = idx[kj], idx[ki]

                    if behindij == -1 and idx[0] != 4:
                        if idx[0] == 0 or idx[0] == 3:
                            behind[i][j], behind[j][i] = 1, 0
                        if idx[0] == 1 or idx[0] == 2:
                            behind[i][j], behind[j][i] = 0, 1
                    elif behindij == -1 and idx[0] == 4:
                        if idx[1] == 0 or idx[1] == 3:
                            behind[i][j], behind[j][i] = 1, 0
                        if idx[1] == 1 or idx[1] == 2:
                            behind[i][j], behind[j][i] = 0, 1
                    elif behindij != -1:
                        if idx[0] == 0 or idx[0] == 3 or (idx[0] == 4 and behindij == 1):
                            behind[i][j], behind[j][i] = 1, 0
                        if idx[0] == 1 or idx[0] == 2 or (idx[0] == 4 and behindij == 0):
                            behind[i][j], behind[j][i] = 0, 1

                    print tmplist, behindij, behind[i][j]

        sort_index = [-1 for i in range(0, tolsent)]
        index = [i for i in range(0, tolsent)]
        recursort(behind, sort_index, 0, index, 0)

        f = open(unicode(outDir+news+'/'+label+'.txt', 'utf8'), 'w')
        for sent in cadisent:
            f.write(sent.content+'\n')
        for i in range(0, tolsent):
            for j in range(0, tolsent):
                f.write(str(behind[i][j])+'\t')
            f.write('\n')
        f.write('-----------------------------------------------\n')
        for i in range(0, tolsent):
            f.write(str(sort_index[i])+' ')
        f.write('\n')

        for i in range(0, tolsent):
            for j in range(0, tolsent):
                if sort_index[j] == i:
                    f.write(cadisent[j].content+'\n')
                    break
        f.close()
        '''

        """
        #选择blocks中的若干块，使得其总句子数在大于10的情况下尽可能小
        tolsent, endblock = 0, 0
        while tolsent < 10 and endblock < blockcnt:
            tolsent += len(blocks[endblock])
            endblock += 1
        assert endblock != 0

        #对0~endblock-1的块进行排序
        #对每个块，计算其他的块是放在它的前头还是后头
        #behind[i][j] = 1（或behind[j][i] = 0）(i!=j)，则说明i应放在j之后
        behind = []
        for i in range(0, endblock):
            tmp = [-1 for i in range(0, endblock)]
            behind.append(tmp)
        for i in range(0, endblock):
            for j in range(i+1, endblock):
                newi = blocks[i][0].newsid-1 #块i所在的新闻编号
                newj = blocks[j][0].newsid-1 #块j所在的新闻编号

                # 计算块j与块i在新闻newi中前半部分和后半部分的相似度，若与前半部分较为相似，则j放i前头，反之，放后头
                newi_front, newi_behind = [], []
                blocki_start = blocks[i][0].globalid
                blocki_end = blocks[i][len(blocks[i])-1].globalid
                for sent in new[newi]:
                    if sent.globalid < blocki_start:
                        newi_front.append(sent)
                    elif sent.globalid > blocki_end:
                        newi_behind.append(sent)
                simi_front, simi_behind = 0.0, 0.0
                for sent in newi_front:
                    for sentj in blocks[j]:
                        simi_front = max(simi_front, cos_similarity(sent.vec, sentj.vec))
                for sent in newi_behind:
                    for sentj in blocks[j]:
                        simi_behind = max(simi_behind, cos_similarity(sent.vec, sentj.vec))
                if simi_behind > simi_front:
                    behind[i][j], behind[j][i] = 0, 1
                else:
                    behind[i][j], behind[j][i] = 1, 0

        sort_index = [-1 for i in range(0, endblock)]
        index = [i for i in range(0, endblock)]
        recursort(behind, sort_index, 0, index, 0)

        f = open(unicode(outDir+news+'/'+label+'.txt', 'utf8'), 'w')
        for sinx in sort_index:
            for sent in blocks[sinx]:
                f.write(sent.content+'\n')
            f.write('\n')
        f.close()
        """


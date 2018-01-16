#coding:utf-8
import os
from pyltp import Segmentor, Postagger, NamedEntityRecognizer, Parser

LTP_DATA_DIR = 'D:/coding/Python2.7/ltp_data_v3.4.0'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，模型名称为`pos.model`
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`

print '载入分词模型...'
segmentor = Segmentor()  # 初始化实例
segmentor.load(cws_model_path)  # 加载模型
postagger = Postagger()
postagger.load(pos_model_path)
recognizer = NamedEntityRecognizer() # 初始化实例
recognizer.load(ner_model_path)  # 加载模型
parser = Parser() # 初始化实例
parser.load(par_model_path)  # 加载模型

r2l = ['SBV', 'FOB', 'ATT', 'ADV', 'LAD']
l2r = ['VOB', 'IOB', 'DBL', 'CMP', 'COO', 'POB', 'RAD']
def anl(q, segmentor, postagger, recognizer, parser):
    # words = segmentor.segment(q)
    words = q.split()
    #如果有书名号、引号的话，那么就不应该被分开
    #这些个符号舍弃，但是要找到一个方法标识出来，因为他们很重要
    wordl = len(words)
    twords = []
    i = 0
    baol = {'《':0}
    baor = ['》']
    while i < wordl:
        tmp = ""
        if words[i] in baol:
            tmp = '#' #标记出这个分词是引用的
            which = baol[words[i]]
            i += 1
            while i < wordl:
                if words[i] != baor[which]:
                    tmp += words[i]+'+'
                    i += 1
                else:
                    break
        else:
            tmp = words[i]
        i += 1
        twords.append(tmp)
    words = twords
    # print '#done'

    postags = postagger.postag(words)
    #将被引号标注的词性标位i（习语）
    postagsl = len(postags)
    for i in range(0, postagsl):
        if words[i][0] == '#':
            postags[i] = 'i'
    #去掉头和尾的标点
    dotl, dotr = 0, len(words)-1
    while dotl < postagsl and postags[dotl] == 'wp':
        dotl +=1
    while dotr >= 0 and  postags[dotr] == 'wp':
        dotr -= 1
    # print 'cutdone'
    if dotl >= dotr:
        s1, s2,s3,s4 = [],[],[],[]
        return s1, s2, s3, s4

    howmuch = 0 #统计有多少个句子
    sents,tags = [],[]
    i = dotl
    sent,tag = [],[]
    while i <= dotr:
        if words[i] == ',' or words[i]== '，':
            sents.append(sent)
            tags.append(tag)
            howmuch += 1
            sent,tag = [],[]
        else:
            sent.append(words[i])
            tag.append(postags[i])
        i += 1
    if len(sent) != 0:
        sents.append(sent)
        tags.append(tag)
        howmuch += 1
    # print 'sentdone'
    # print 'howmuch = ', howmuch

    netags, fas = [], []
    for i in range(0, howmuch):
        #一次大bug的发现，当sent为空时，调用哈工大的包会导致程序停止
        sent, tag = sents[i], tags[i]
        if len(sent) != 0:
            netag = recognizer.recognize(sent, tag)
            arc = parser.parse(sent, tag)

            # narc = [a.head-1 for a in arc]
            narc = [-1 for a in arc]
            cur = 0
            for a in arc:
                if a.relation in l2r:
                    narc[a.head-1] = cur
                else:
                    narc[cur] = a.head-1
                cur += 1
            netags.append(netag)
            fas.append(narc)
        else:
            netag, narc = [], []
            netags.append(netag)
            fas.append(narc)
    return sents, tags, netags, fas

# 对于句法数组fa，第i个词，它有若干子树
# 返回最深的子树的层数
def geth(size, fa, i):
    h = 0
    for j in range(0, size):
        if fa[j] == i:
            h = max(h, geth(size, fa, j)+1)
    return h

def getkw(sents, tags, netags, fas):
    #这几个用于记录关键词组、对应的词性、以及位于q的第几个子句
    #关键词组中的词用+相连，对应的词性也是
    kws, kwtags, kwids = [], [], []
    howmuch = len(sents)  #q中有多少个句子
    for sid in range(0, howmuch):
        sent, tag, nettag, fa = sents[sid], tags[sid], netags[sid], fas[sid]
        size = len(fa)
        hmax = 0
        #获得每个结点的最深子树层数
        h = [0 for i in range(0, size)]
        for i in range(0, size):
            h[i] = geth(size, fa, i)
            hmax = max(hmax, h[i])
        use = [0 for i in range(0, size)]  #均初始化为未使用
        #这些书名号内的词首先标记为使用（一般不把它与其他词构成关键词组）
        for i in range(0, size):
            if sent[i][0] == '#' :
                use[i] = 1
                kws.append(sent[i])
                kwtags.append(tag[i])
                kwids.append(sid)
        #代词、助词、介词、标点符号、连词、感叹词、拟声词不需要
        notwant1 = ['r', 'u', 'p', 'wp','c','e','o']
        badword = ['是', '请问']
        for i in range(0, size):
            if tag[i] in notwant1 or sent[i] in badword:
                use[i] = 1
            #哪后面的量词（q）不是关键词
            if i > 0 and tag[i] == 'q' and tag[i-1] == 'r':
                use[i] = 1

        #首先对于子树只有一层的未使用结点，将它与子树合并
        #并标记为使用；之后，原来子树有两层的结点变成了子树
        #还有一层的节点了
        for curh in range(1, hmax+1):
            for i in range(0, size):
                if h[i] == curh and use[i] == 0:
                    kw, kwtag = '', ''
                    for j in range(0, size):
                        if fa[j] == i and use[j] == 0:
                            kw += sent[j] + '+'
                            kwtag += tag[j] + '+'
                            use[j] = 1
                    kw += sent[i]
                    kwtag += tag[i]
                    use[i] = 1
                    kws.append(kw)
                    kwtags.append(kwtag)
                    kwids.append(sid)

        #最后一遍扫描，把未使用的作为关键词组
        for i in range(0, size):
            if use[i] == 0:
                use[i] = 1
                kws.append(sent[i])
                kwtags.append(tag[i])
                kwids.append(sid)

    return kws, kwtags, kwids

news = ['hpv疫苗','iPhone X', '乌镇互联网大会','九寨沟7.0级地震','俄罗斯世界杯',\
'双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',\
'王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',\
'萨德系统 中韩', '雄安新区', '榆林产妇坠楼']
# news = ['乌镇互联网大会']
sourceDir = '../Ngrams/Processed/'
outDir = 'continuity/'
senpuc = ['。', '?', '；','：', '！', ',', '.', '!', '?', ';', ':']
for newsName in news:
    print newsName
    f = open(unicode(sourceDir+newsName+'/words.txt', 'utf8'), 'r')
    fw = open(unicode(outDir+newsName+'.txt', 'utf8'), 'w')
    dic = {}
    tag = {}
    for line in f:
        line = line.strip()
        for puc in senpuc:
            line = line.replace('puc', '，')
        line = line.split('，')
        for sent in line:
            if len(sent) > 3:
                sents, tags, netags, fas = anl(sent, segmentor, postagger, recognizer, parser)
                kws, kwtags, kwids = getkw(sents, tags, netags, fas)
                l = len(kws)
                for i in range(0, l):
                    kw, kwtag = kws[i], kwtags[i]
                    kw = kw.replace('++', '+').replace('', '')
                    if kw not in dic:
                        if len(kw.split('+')) <= 3:
                            if kw[0] == '#':
                                kw = kw[1:len(kw)-1] #因为最后面多了个+号
                            dic[kw] = 1
                            tag[kw] = kwtag
                    else:
                        if len(kw.split('+')) <= 3:
                            if kw[0] == '#':
                                kw = kw[1:len(kw)-1]
                            dic[kw] += 1
    f.close()
    for kw in dic:
        if len(kw) != 3:#忽略一个字的
            if len(kw.split('+')) == 1 and dic[kw] >= 10:
                fw.write(''.join(kw.split('+'))+' '+tag[kw]+'\n')
            if len(kw.split('+')) > 1 and dic[kw] >= 1:
                fw.write(''.join(kw.split('+'))+' '+tag[kw]+'\n')
    fw.close()

    alltag = {}
    for kw in dic:
        if kw == '':
            continue
        t = tag[kw]
        if t != 'i':
            tkw = kw.split('+')
        else:
            tkw = [kw]

        t = t.split('+')
        l = min(len(tkw), len(t))

        try:
            for i in range(0, l):
                w, _t = tkw[i], t[i]
                if w not in alltag:
                    alltag[w] = _t
        except:
            print kw
            print ' '.join(tkw), len(tkw)
            print ' '.join(t), len(t)
            exit()
    f = open(unicode('tag/'+newsName+'.txt', 'utf8'), 'w')
    for w in alltag:
        f.write(w+' '+alltag[w]+'\n')
    f.close()







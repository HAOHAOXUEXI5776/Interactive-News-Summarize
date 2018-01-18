# coding:utf-8

# 测试ltp的依存句法分析功能，希望能够解决代词指代的问题

import os
from pyltp import Segmentor, Postagger, Parser

LTP_DATA_DIR = '/Users/liuhui/Desktop/实验室/LTP/ltp_data_v3.4.0'

# 加载分词模型，词性标注模型，依存句法分析模型
segmentor = Segmentor()
segmentor.load(os.path.join(LTP_DATA_DIR, 'cws.model'))
postagger = Postagger()
postagger.load(os.path.join(LTP_DATA_DIR, 'pos.model'))
parser = Parser()
parser.load(os.path.join(LTP_DATA_DIR, 'parser.model'))

sentence = '小明上学路上摔倒了，所以他迟到了'
words = segmentor.segment(sentence)
postags = postagger.postag(words)
arcs = parser.parse(words, postags)
for i in range(0, len(words)):
    print i+1, '\t', words[i], '\t', postags[i], '\t', '%d:%s' % (arcs[i].head, arcs[i].relation)

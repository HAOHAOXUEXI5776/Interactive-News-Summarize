#coding:utf-8
import gensim
from pyltp import Segmentor

blockDir = '../Sentence/assign/contain/'
news = 'hpv疫苗'
label = '世界卫生组织'

# 加载分词模型
segmentor = Segmentor()
segmentor.load('D:/coding/Python2.7/ltp_data_v3.4.0/cws.model')

model = gensim.models.Word2Vec.load('../Sentence/model')

s = '基建'
s1 = '马丁'
s2 = '说'

f = open(unicode(blockDir+news+'/'+label+'.txt','utf8'), 'r')
f.readline()
content = f.readline()
words = segmentor.segment(content)

for word in words:
    print word, type(word), word in model

print type(s)
print model[s1]


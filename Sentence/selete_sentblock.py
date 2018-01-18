# coding:utf-8
import os

# 根据一个标签，找到包含它的句子，如果该句子所在的段包含的句子数不多于3，则该段作为一个块，
# 如果段包含3以上的句子，则将该句子的上下两句合共3句作为一个块。
# 如果两个块有重合，比如块S1-S2-S3和块S3-S4-S5，其中S2和S3包含标签，则合并成一个块S1-S2-S3-S4-S5

labelDir = './label/'
sentDir = './sentence/'
outDir = './assign/contain/'

class Sent:
    def __init__(self, _newsid, _globalid, _paraid, _localid, _sentnum, _content):
        self.newsid = _newsid        #该句所属新闻编号
        self.globalid = _globalid    #该句在该篇新闻的第几句
        self.paraid = _paraid        #该句在该篇新闻的第几段
        self.localid = _localid      #该句在所属段的第几句
        self.sentnum = _sentnum       #该句所在段有多少句
        self.content = _content
    def haslabel(self, ngram):
        return ngram in self.content

class SentHome:
    def __init__(self):
        self.allsent = []
        self.sentnum = 0
    def set(self, sentF):
        f = open(sentF, 'r')
        while True:
            nums = f.readline()
            if len(nums) == 0:
                break
            nums = nums.strip().split()
            nums = [int(num) for num in nums]
            content = f.readline().strip()
            sent = Sent(nums[0],nums[1],nums[2],nums[3],nums[4],content)
            self.allsent.append(sent)
            self.sentnum += 1
        f.close()

def sentblock(label, sentHome):
    #返回标签label的块
    #返回的是句子编号
    blocks = []
    for i in range(0, sentHome.sentnum):
        cursent = sentHome.allsent[i]
        if cursent.haslabel(label):
            block = []
            curparaid = cursent.paraid
            curnewsid = cursent.newsid
            if cursent.sentnum <= 3:
                #当前段少于3句
                for j in range(-2, 3):
                    if i+j >= 0 and i+j < sentHome.sentnum:
                        if sentHome.allsent[i+j].paraid == curparaid \
                            and sentHome.allsent[i+j].newsid == curnewsid:
                            block.append(i+j)
            else:
                if i == sentHome.sentnum - 1 or sentHome.allsent[i+1].paraid != curparaid or sentHome.allsent[i+1].newsid != curnewsid:
                    #该句是本段的末句
                    block = [i-1, i]
                elif i == 0 or sentHome.allsent[i-1].paraid != curparaid or sentHome.allsent[i-1].newsid != curnewsid:
                    #该句是本段的首句
                    block = [i, i+1]
                else:
                    block = [i-1, i, i+1]
            blocks.append(block)
    return blocks


news_name = ['hpv疫苗', 'iPhone X', '乌镇互联网大会', '九寨沟7.0级地震', '俄罗斯世界杯',
             '双十一购物节', '德国大选', '功守道', '战狼2', '权力的游戏', '李晨求婚范冰冰', '江歌刘鑫',
             '王宝强马蓉离婚案', '百度无人驾驶汽车', '红黄蓝幼儿园', '绝地求生 吃鸡', '英国脱欧',
             '萨德系统 中韩', '雄安新区', '榆林产妇坠楼']

# news_name = ['德国大选']

def main():
    for news in news_name:
        #得到标签
        labels = []
        f = open(unicode(labelDir+news+'/label.txt', 'utf8'), 'r')
        for line in f:
            labels.append(line.strip().replace('+', ''))
        f.close()

        #得到所有句子
        sentHome = SentHome()
        sentHome.set(unicode(sentDir+news+'/sentence.txt','utf8'))

        print news, '总句子数=', sentHome.sentnum

        cur_path = unicode(outDir+news, 'utf8')
        if not os.path.exists(cur_path):
            os.mkdir(cur_path)

        for label in labels:
            blocks = sentblock(label, sentHome)
            f = open(unicode(outDir+news+'/'+label+'.txt', 'utf8'), 'w')
            for block in blocks:
                f.write(str(len(block))+'\n')
                for i in block:
                    c = sentHome.allsent[i]
                    f.write(str(c.newsid)+' '+str(c.globalid)+' '+str(c.paraid)+' '+str(c.localid)+' '+str(c.sentnum)+'\n')
                    f.write(c.content+'\n')
            f.close()


if __name__ == '__main__':
    main()

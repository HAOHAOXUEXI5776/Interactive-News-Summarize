#coding:utf-8

import wx
import codecs
import copy
import gensim
from pyltp import Segmentor
import post_process

qin = 0  # 改成0是刘辉的路径，否则是秦文涛的路径
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

class MyDragCheckBox(wx.CheckBox):
    '''垂直方向可以拖动的若干CheckBox'''
    def __init__(self, parent, label):
        super(MyDragCheckBox, self).__init__(parent, label = label)
        self.w = self.GetSize()[0]
        self.h = self.GetSize()[1]
        self.idx = 0  #该框是从上往下的第几个
        self.i = 0    #索引
        self.n = 0      #为当前事件对应的主题数
        self.flag = 0   #该框是否在被拖动
        self.limit = [0, 0, 0, 0] #拖动范围（相对于整块屏幕）
        self.l0, self.l1 = 0, 0   #本窗口中拖动的上界和下界
        self.clickbegin = (0, 0)  #刚点击该窗口时，记录偏移位置（相对于整块屏幕）
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

    def Set(self, idx, n, check, allidx, wordspin, win):
        self.i = idx
        self.idx = idx
        self.n = n
        self.check = check
        self.allidx = allidx
        self.wordspin = wordspin
        self.win = win  #用于刷新界面

    def OnLeftDown(self, e):
        self.flag = 1 #仅在此处被标为1
        cnt = 0
        for i in range(0, self.n):
            if self.check[i].flag == 1:
                cnt += 1
        assert cnt == 1

        x, y = self.ClientToScreen(e.GetPosition())
        self.ox, self.oy = self.GetPosition()
        self.px, self.py = self.wordspin[self.i].GetPosition()
        sx, sy = self.GetScreenPosition()
        self.clickbegin = x, y
        self.up = self.oy - self.idx*self.h
        #如此计算limit要求这n个框得紧挨着，相邻两个之间不能有其他的空间
        self.limit[0] = sx
        self.limit[1] = sx + self.w
        self.limit[2] = sy - self.idx*self.h
        self.limit[3] = self.limit[2] + self.n*self.h

        # e.Skip()

        # #debug
        # print 'idx:', self.idx, 'n:', self.n
        # print 'xy:', x, y, 'oxy', self.ox, self.oy, 'sxy', sx, sy
        # print 'limit:', self.limit
        # print 'wh:', self.w, self.h
        # print 'up:', self.up

    def OnMotion(self, e):
        if self.flag == 1 and e.Dragging() and e.LeftIsDown():
            mouse = wx.GetMousePosition()
            if mouse.x < self.limit[0]:
                mouse.x = self.limit[0]
            elif mouse.x > self.limit[1]:
                mouse.x = self.limit[1]
            if mouse.y < self.limit[2]:
                mouse.y  = self.limit[2]
            elif mouse.y > self.limit[3]:
                mouse.y = self.limit[3]
            dx, dy = mouse.x-self.clickbegin[0], mouse.y-self.clickbegin[1]
            self.Move((dx+self.ox, dy+self.oy))
            self.wordspin[self.i].Move((dx+self.px, dy+self.py))

    def OnLeftUp(self, e):
        if self.flag == 0:
            return
        mouse = wx.GetMousePosition()
        if mouse.y < self.limit[2]:
            mouse.y = self.limit[2]
        if mouse.y >= self.limit[3]:
            mouse.y = self.limit[3]
        nidx = (mouse.y-self.limit[2])/self.h #该框将要处在的序号
        if nidx >= self.n:
            nidx = self.n-1
        if nidx > self.idx:
            for i in range(self.idx+1, nidx+1):
                truei = self.allidx[i]
                self.check[truei].idx -= 1
        elif nidx < self.idx:
            for i in range(nidx, self.idx):
                truei = self.allidx[i]
                self.check[truei].idx += 1
        self.idx = nidx

        #更新allidx与位置
        for i in range(0, self.n):
            self.allidx[self.check[i].idx] = i
            self.check[i].SetPosition((self.ox, self.check[i].idx*self.h+self.up))
            self.wordspin[i].SetPosition((self.px, self.check[i].idx*self.h+self.up))

        self.win.Refresh()
        self.flag = 0 #仅在此处销毁flag

        e.Skip()

    def OnLeaveWindow(self, e):
        if self.flag == 1:
            self.OnLeftUp(e)





class MyWin(wx.Frame):
    def __init__(self, parent, title):
        super(MyWin, self).__init__(parent, title = title, size = (1100, 700),
            style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.newsname = ''
        self.n = 0  #事件下的主题的个数
        self.maxtopic = 20 #超过20个标签不显示
        self.maxnewsnum = 100 #规定最多显示100篇新闻
        self.history = [u'英国脱欧', u'hpv疫苗', u'功守道'] #搜索的新闻历史
        self.blank = '很长的不可见时的标题'
        self.prefd = wx.FontData()
        #颜色用于标签-综述的关系
        self.color = ['#FF0000', '#02B232', '#0000FF', '#008000', '#FF00FF',
                      '#208080', '#400000', '#800000', '#000040', '#000080',
                      '#400040', '#800080', '#408000', '#804000', '#00FFFF',
                      '#24ADA3', '#AC0987', '#745BAD', '#87813A', '#134599']
        self.panel = wx.Panel(self)
        self.SetTopBar()
        self.SetTopicBox()
        self.SetWorkstation()
        self.SetStatus()
        self.SetLocation()
        self.Go()

    def SetTopBar(self):
        # self.CreateStatusBar()  #底部状态栏
        self.box1 = wx.BoxSizer(wx.HORIZONTAL)

        txt = wx.StaticText(self.panel, -1, 'Enter a event\'s name:')
        self.box1.Add(txt, 0, wx.CENTER|wx.ALL, 2)

        self.input = wx.ComboBox(self.panel, -1, "", \
            style = wx.CB_DROPDOWN|wx.TE_PROCESS_ENTER)
        self.input.AppendItems(self.history)
        self.Bind(wx.EVT_COMBOBOX, self.OnEventSelect, self.input)
        self.input.Bind(wx.EVT_TEXT_ENTER, self.OnEventEnter)
        self.box1.Add(self.input, 1, wx.EXPAND|wx.ALL, 2)

        #quick键是为了让程序在不需要用户交互的情况下，完成所有的综述工作
        self.quick = wx.Button(self.panel, -1, '&Quick', style = wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.OnQuick, self.quick)
        self.save = wx.Button(self.panel, wx.ID_SAVE, '&Save', style = wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.save)
        self.refresh = wx.Button(self.panel, -1, '&Clear', style = wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.OnRefresh, self.refresh)
        self.about = wx.Button(self.panel, wx.ID_ABOUT, '&About', style = wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.OnAbout, self.about)
        self.exit = wx.Button(self.panel, wx.ID_EXIT, 'E&xit', style = wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.OnExit, self.exit)


        self.box1.Add(self.quick, 0, wx.EXPAND|wx.ALL, 2)
        self.box1.Add(self.save, 0, wx.EXPAND|wx.ALL, 2)
        self.box1.Add(self.refresh, 0, wx.EXPAND|wx.ALL, 2)
        self.box1.Add(self.about, 0, wx.EXPAND|wx.ALL, 2)
        self.box1.Add(self.exit, 0, wx.EXPAND|wx.ALL, 2)


    def SetTopicBox(self):

        topicbox = wx.StaticBox(self.panel, -1, 'Labels of Topics')
        self.box2 = wx.StaticBoxSizer(topicbox, wx.VERTICAL)

        self.box20 = wx.BoxSizer(wx.HORIZONTAL)
        self.seleteall = wx.CheckBox(self.panel, label = 'Not/ALL') #全选
        self.seleteall.Bind(wx.EVT_CHECKBOX, self.OnSelectall)
        self.seleteinv = wx.Button(self.panel, label = 'Inverse', size = (60, 20)) #反选
        self.seleteinv.Bind(wx.EVT_BUTTON, self.OnSelectinv)
        self.box20.Add(self.seleteall)
        self.box20.Add(self.seleteinv)


        self.box21 = wx.BoxSizer(wx.HORIZONTAL)

        self.box211 = wx.BoxSizer(wx.VERTICAL)

        self.topicList = self.maxtopic*[self.blank] #标签列表
        self.topiccheck = []
        self.allidx = []
        text1 = wx.StaticText(self.panel, label = 'Topics')
        self.box211.Add(text1)
        for i, topic in enumerate(self.topicList):
            # tmp = wx.CheckBox(self.panel, label = topic)
            tmp = MyDragCheckBox(self.panel, label = topic)
            tmp.SetForegroundColour(self.color[i])
            tmp.Hide() #初始时需要隐藏起来
            self.topiccheck.append(tmp)
            self.box211.Add(tmp, 0, wx.RESERVE_SPACE_EVEN_IF_HIDDEN)

        self.box212 = wx.BoxSizer(wx.VERTICAL)
        self.topicWord = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #每个标签生成多少字的综述， 默认250
        self.wordspin = []
        text2 = wx.StaticText(self.panel, label = '#Word')
        self.box212.Add(text2)
        for i, num in enumerate(self.topicWord):
            tmp = wx.SpinCtrl(self.panel, value = '0', size = (60,17), min = 50, max = 800)
            tmp.SetForegroundColour(self.color[i])
            tmp.Hide() #初始时需要隐藏起来
            self.wordspin.append(tmp)
            self.box212.Add(tmp, 0, wx.RESERVE_SPACE_EVEN_IF_HIDDEN)

        self.box21.Add(self.box211)
        self.box21.Add(self.box212)

        self.sumbtn = wx.Button(self.panel, label = 'Synthesize', style = wx.BU_EXACTFIT)
        self.sumbtn.Bind(wx.EVT_BUTTON, self.OnSummary)

        self.box2.Add(self.box20, 0, border = 2)
        self.box2.Add(self.box21, 0, border = 2)
        self.box2.Add(self.sumbtn, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, border = 2)

    def SetWorkstation(self):

        workbox = wx.StaticBox(self.panel, -1, 'Workstation')
        self.box3 = wx.StaticBoxSizer(workbox, wx.HORIZONTAL)

        #notebook里有自动生成的综述框（solidsum）、新闻框、网页框。。。
        self.noteb1 = wx.Notebook(self.panel, -1, style = wx.NB_TOP)

        #自动生成的综述框
        #Windows下需将style设为wx.TE_RICH，才能使的同个框内有不同字体/颜色的字
        self.solidsum = wx.TextCtrl(self.noteb1, style = wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH)
        self.solidsum.SetBackgroundColour((240, 240, 240, 255)) #设置颜色为传统的灰色，直观上给人只读的感受


        #新闻框
        self.newspanel = wx.Panel(self.noteb1, -1)
        self.newsbox = wx.BoxSizer(wx.VERTICAL)
        self.newstree = wx.TreeCtrl(self.newspanel, -1, size = (-1, 300))
        self.root1 = self.newstree.AddRoot('News file')
        self.newstreeid = []
        for i in range(0, self.maxnewsnum):
            curid = self.newstree.InsertItem(self.root1, i, text = '')
            self.newstreeid.append(curid)
        self.newstree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSeeNews) #点击到某个新闻的名字时，在newscontent显示其内容
        self.newscontent = wx.TextCtrl(self.newspanel, -1, style = wx.TE_MULTILINE|wx.TE_READONLY)
        self.newsbox.Add(self.newstree, 0, wx.ALL|wx.EXPAND)
        self.newsbox.Add(self.newscontent, 1, wx.ALL|wx.EXPAND)
        self.newspanel.SetSizer(self.newsbox)

        self.noteb1.InsertPage(0, self.solidsum, text = 'Auto generated synthesis')
        self.noteb1.InsertPage(0, self.newspanel, text = 'News')

        #editbox里面是编辑框，编辑在这里面工作
        self.editbox = wx.BoxSizer(wx.VERTICAL)
        self.editbox0 = wx.BoxSizer(wx.HORIZONTAL)
        self.fontbtn = wx.Button(self.panel, label = 'Font', size = (-1, 25), style = wx.BU_EXACTFIT)
        self.fontbtn.Bind(wx.EVT_BUTTON, self.OnFontbtn)
        self.editbox0.Add(self.fontbtn, 0, wx.EXPAND|wx.ALL, 2)
        self.editsum = wx.TextCtrl(self.panel, size = (-1, -1), style = wx.TE_MULTILINE)
        self.editbox.Add(self.editbox0, 0, wx.EXPAND|wx.ALL,0)
        self.editbox.Add(self.editsum, 1,  wx.EXPAND|wx.ALL,0)

        self.box3.Add(self.noteb1, 1, wx.ALL|wx.EXPAND, 1)
        self.box3.Add(self.editbox, 1, wx.ALL|wx.EXPAND, 1)

    def SetStatus(self):
        #设置一个文本框，动态地报告当前的操作
        statbox = wx.StaticBox(self.panel, -1, 'Status')
        self.box4 = wx.StaticBoxSizer(statbox, wx.VERTICAL)
        self.statinfo = wx.TextCtrl(self.panel, size = (-1, 200), style = wx.TE_MULTILINE|wx.TE_READONLY)
        self.box4.Add(self.statinfo, 0, wx.ALL|wx.EXPAND, 2)

    def SetLocation(self):
        self.boxv = wx.BoxSizer(wx.VERTICAL)

        self.boxv1 = wx.BoxSizer(wx.VERTICAL)
        self.boxv1.Add(self.box2, 0, wx.EXPAND)
        self.boxv1.Add(self.box4, 0, wx.EXPAND|wx.ALL)

        self.boxh = wx.BoxSizer(wx.HORIZONTAL)
        self.boxh.Add(self.boxv1, 0, wx.EXPAND)
        self.boxh.Add(self.box3, 1, wx.EXPAND)

        self.boxv.Add(self.box1,0, wx.EXPAND)
        self.boxv.Add(self.boxh, 0, wx.EXPAND)

    def Go(self):
        self.panel.SetSizer(self.boxv)
        self.panel.SetAutoLayout(True)
        self.boxv.Fit(self.panel)
        self.Centre()
        self.Show(True)

    def OnEventEnter(self, e):
        self.newsname = self.input.GetValue()
        self.search()

    def OnEventSelect(self, e):
        # self.newsname = self.input.GetStringSelection()
        self.newsname = self.input.GetValue()
        self.search()

    def OnSummary(self, e):
        self.summary()
        # e.Skip()

    def OnSelectall(self, e):
        if self.seleteall.GetValue() == True:
            #全选
            for i in range(0, self.maxtopic):
                self.topiccheck[i].SetValue(True)
        else:
            #全不选
            for i in range(0, self.maxtopic):
                self.topiccheck[i].SetValue(False)

    def OnSelectinv(self, e):
        for i in range(0, self.maxtopic):
            curvalue = self.topiccheck[i].GetValue()
            self.topiccheck[i].SetValue(1-curvalue)

    def OnFontbtn(self, e):
        #设置编辑框的字体
        fontdig = wx.FontDialog(self.panel, self.prefd)
        if fontdig.ShowModal() == wx.ID_OK:
            curfd = fontdig.GetFontData()
            nxtfont = curfd.GetChosenFont()
            self.editsum.SetFont(nxtfont)
            nxtcolor = curfd.GetColour()
            self.editsum.SetForegroundColour(nxtcolor)
            #下次选择字体的时候，初始的字体就是上次的字体了
            #不能直接self.prefd = fontdig.GetFontData(),具体什么原因不清楚
            self.prefd.SetInitialFont(nxtfont)
            self.prefd.SetColour(nxtcolor)
        fontdig.Destroy()
        e.Skip()

    def OnSeeNews(self, e):
        for i in range(0, self.maxnewsnum):
            if self.newstree.IsSelected(self.newstreeid[i]):
                if self.newsname != '':
                    f = open('../News/'+self.newsname+'/'+str(i+1)+'.txt')
                    self.newscontent.SetValue(f.read())
                    f.close()
                    break


    def search(self):
        if self.newsname == '':
            return
        self.MyRefresh()
        #类似于记录历史记录
        if self.newsname not in self.history:
            self.history.append(self.newsname)
            self.input.AppendItems(self.newsname)

        self.statinfo.AppendText(('Current event: %s is being searched...\n')%(self.newsname))

        #在新闻框内显示所有的新闻标题
        try:
            f = open('../News/'+self.newsname+'/MetaInfo.txt', 'r')
        except:
            wx.MessageBox("文件不存在", 'message', wx.OK|wx.ICON_INFORMATION)
            return
        newsname = []
        while True:
            line = f.readline()
            if len(line) == 0:
                break
            if line[0:2] == 'id':
                newsname.append(f.readline().strip())
                time = f.readline()
                f.readline()
        f.close()
        newcnt = len(newsname)
        if newcnt >= self.maxnewsnum:
            for i in range(0, self.maxnewsnum):
                self.newstree.SetItemText(self.newstreeid[i], newsname[i])
            self.statinfo.AppendText(('%d news crawled.\n')%(self.maxnewsnum))
        else:
            for i in range(0, newcnt):
                self.newstree.SetItemText(self.newstreeid[i], newsname[i])
            for i in range(newcnt, self.maxnewsnum):
                self.newstree.SetItemText(self.newstreeid[i], '')
            self.statinfo.AppendText(('%d news crawled.\n')%(newcnt))

        #获取主题
        labelpath = '../Sentence/label/'
        labelpath += self.newsname+'/label.txt'
        f = open(labelpath, 'r')

        #初始化为空，得到新的标签
        self.topicList = []
        self.topicWord = []
        for line in f:
            self.topicList.append(line.strip().replace('+', ''))
            self.topicWord.append(250)
        f.close()

        #新的多选框和数字调控按钮
        standlen = len(self.blank)
        for i, topic in enumerate(self.topicList):
            if i < self.maxtopic:
                curcheck, curspin = self.topiccheck[i], self.wordspin[i]
                curlen = len(topic)
                if curlen > standlen:
                    topic = topic[0:standlen]
                else:
                    topic = topic + (standlen-curlen)*' '
                curcheck.SetLabel(topic);curspin.SetValue(250)
                curcheck.Show();curspin.Show()

        #为了能拖动多选框要做的初始化工作
        self.n = min(len(self.topicList), self.maxtopic)
        self.allidx = [i for i in range(0, self.n)]
        for i in range(0, self.n):
            self.topiccheck[i].Set(i, self.n, self.topiccheck, self.allidx, self.wordspin, self)

        self.statinfo.AppendText(('%d topics totally.\n')%(len(self.topicList)))
        self.boxv.Layout()

    def summary(self):
        #把每个标签对应的综述，经过后处理，输出
        if self.newsname == '':
            return

        #得到所选的标签
        selectTopic = []
        selectColor = []
        for i in range(0, self.n):
            truei = self.allidx[i]  #生成总数的顺序是从上往下数的
            if self.topiccheck[truei].IsChecked():
                curlabel = self.topiccheck[truei].GetLabel()
                curlabel = curlabel.strip() #去掉末尾的空格
                selectTopic.append(curlabel)
                self.statinfo.AppendText(curlabel+'Choosed\n')
                selectColor.append(self.color[truei])

        selecnt = len(selectTopic)
        if selecnt == 0:
            self.statinfo.AppendText('No topic in selected.\n')
            return
        elif selecnt == 1:
            self.statinfo.AppendText('1 topic is selected.\n')
        else:
            self.statinfo.AppendText(('%d topics are selected.\n')%(selecnt))

        self.statinfo.AppendText('Processing...\n')

        #根据所选的标签，以及它们对应的块，经post_process.py，得到综述
        post_process.getSum(self.newsname, selectTopic, model, stoplist, segmentor)

        #输出到Auto generated summary框中
        f = open('uisum/'+self.newsname+'.txt', 'r')
        tmpsummary = f.read()
        f.close()

        self.editsum.SetValue(tmpsummary)

        #在solidsum中，标签使用对应的色彩
        self.solidsum.SetValue('')
        tmpsummary = tmpsummary.split('\n')
        i, j = 0, 0
        tmptmp = ''
        # print tmpsummary
        while i < selecnt:
            if tmpsummary[j] == '':
                if tmptmp != '':
                    self.solidsum.SetDefaultStyle(wx.TextAttr(selectColor[i]))
                    self.solidsum.AppendText(tmptmp+'\n')
                    tmptmp = ''
                    i += 1
            else:
                tmptmp += tmpsummary[j]+'\n'
            j += 1

        self.statinfo.AppendText('Synthesis done.\n')


    def MyRefresh(self):
        self.editsum.SetValue('')
        self.solidsum.SetValue('')
        self.newscontent.SetValue('')
        #将所有多选框和数字调控按钮设置为不可见，并将值初始化
        for i in range(0, self.maxtopic):
            self.topiccheck[i].Hide();self.wordspin[i].Hide()
            self.topiccheck[i].SetLabel(self.blank)
            self.topiccheck[i].SetValue(False)
            self.wordspin[i].SetValue(250)
        for i in range(0, self.maxnewsnum):
            self.newstree.SetItemText(self.newstreeid[i], '')
        self.statinfo.AppendText('Refresh done.\n')

    def OnQuick(self, e):
        self.newsname = self.input.GetValue()
        self.search()
        #选择前5个标签生成综述
        for i in range(0, 5):
            self.topiccheck[i].SetValue(True)
        self.summary()

    def OnSave(self, e):
        dlg = wx.FileDialog(self, style = wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            f = codecs.open(dlg.GetPath(), 'w', 'utf8')
            f.write(self.editsum.GetValue())
            f.close()
        dlg.Destroy()

    def OnRefresh(self, e):
        self.MyRefresh()


    def OnAbout(self, e):
        helps = 'Given a event name, this app will crawl a set of news about it. '
        helps += 'Then it will find several topics from them. You can choose some topics, '
        helps += 'and this app will generate a summary about these topics.'
        wx.MessageBox(helps, 'Guide', wx.OK|wx.ICON_INFORMATION)

    def OnExit(self, e):
        self.Close(True)


app = wx.App()
MyWin(None, 'A Interactive News Synthesis System')
app.MainLoop()

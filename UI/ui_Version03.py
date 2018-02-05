#coding:utf-8

import wx
import wx.aui
import codecs
import copy
import gensim
from pyltp import Segmentor
import post_process
import sort
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

qin = 1  # 改成0是刘辉的路径，否则是秦文涛的路径
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
        self.k = 0      #为当先显示了块的标签拥有（已显示）的块数
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

class Topic():
    '''记录与标签有关的信息'''
    def __init__(self):
        self.label = ''
        self.checked = 0
        self.blocks = [] #记录标签对应的块
        self.blocknums = [] #该块的位置信息
        self.blockchecks = [] #记录块是否被选择
        self.blockcnt = 0 #块的数目
        self.newsidx = []  #该块对应的新闻


class MyWin(wx.Frame):
    def __init__(self, parent, title):
        super(MyWin, self).__init__(parent, title = title, size = (1100, 700),
            style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.newsname = ''
        self.n = 0  #事件下的主题的个数
        self.maxtopic = 20 #超过20个标签不显示
        self.maxnewsnum = 100 #规定最多显示100篇新闻
        self.maxblockcnt = 20 #规定每个标签至多对应20个块(可以是100个块，但有点慢)
        #（这些个人为规定的“最多”是为了编程方便以及性能）
        self.lasttopic = -1 #为topic的块进行修改后，跳转到下一个topic时要保存
                            #对上一个topic的修改
        self.history = [u'英国脱欧', u'hpv疫苗', u'功守道'] #搜索的新闻历史
        self.blank = '很长的不可见时的标题'

        self.prefd = wx.FontData()#记录上一次选择的字体
        #颜色用于标签-综述的关系
        self.color = ['#FF0000', '#02B232', '#0000FF', '#008000', '#FF00FF',
                      '#208080', '#400000', '#800000', '#000040', '#000080',
                      '#400040', '#800080', '#408000', '#804000', '#00FFFF',
                      '#24ADA3', '#AC0987', '#745BAD', '#87813A', '#134599']
        self.panel = wx.Panel(self)
        self.SetTopBar()
        self.notebook = wx.Notebook(self.panel, -1, style = wx.NB_TOP)
        self.NewsTag()
        self.TopicTag()
        self.notebook.InsertPage(0, self.topicpanel, text = 'Subtopics and Text Blocks')
        self.notebook.InsertPage(0, self.newspanel, text = 'News File')
        self.notebook.SetSelection(0) #跳到News页
        self.WorkStation()
        self.SetLocation()
        self.Go()

    def SetTopBar(self):
        self.k = 0      #不知道为何，在init中已经声明了，但在一开始又说
                        #没声明，故在此又声明一次
        # self.CreateStatusBar()  #底部状态栏
        self.box1 = wx.BoxSizer(wx.HORIZONTAL)

        txt = wx.StaticText(self.panel, -1, 'Enter an topic:')
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

    def NewsTag(self):
        self.newspanel = wx.Panel(self.notebook, -1)

        text1 = wx.StaticBox(self.newspanel, label = 'News Titles')
        self.box211 = wx.StaticBoxSizer(text1, wx.VERTICAL)
        self.newstree = wx.TreeCtrl(self.newspanel, -1, size = (204, -1))
        self.newsroot = self.newstree.AddRoot('News Titles')
        self.newsid = []
        for i in range(0, self.maxnewsnum):
            curid = self.newstree.InsertItem(self.newsroot, i, text = '')
            self.newsid.append(curid)
        self.newstree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSeeNews)
        self.box211.Add(self.newstree, 1, wx.ALL|wx.EXPAND)

        statbox = wx.StaticBox(self.newspanel, -1, 'Status')
        self.box212 = wx.StaticBoxSizer(statbox, wx.VERTICAL)
        self.statinfo_copy = wx.TextCtrl(self.newspanel, size = (-1, 142), style = wx.TE_MULTILINE|wx.TE_READONLY)
        self.box212.Add(self.statinfo_copy, 1, wx.ALL|wx.EXPAND)

        self.box21 = wx.BoxSizer(wx.VERTICAL)
        self.box21.Add(self.box211, 1, wx.ALL|wx.EXPAND)
        self.box21.Add(self.box212, 0, wx.ALL|wx.EXPAND)

        text2 = wx.StaticBox(self.newspanel, label = 'News Content')
        self.box22 = wx.StaticBoxSizer(text2, wx.VERTICAL)
        self.newscontent = wx.TextCtrl(self.newspanel, -1, style = wx.TE_MULTILINE)
        self.box22.Add(self.newscontent, 1, wx.ALL|wx.EXPAND)

        self.box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.box2.Add(self.box21, 0, wx.ALL|wx.EXPAND)
        self.box2.Add(self.box22, 1, wx.ALL|wx.EXPAND)

        self.newspanel.SetSizer(self.box2)

    def TopicTag(self):
        #分三个部分
        #1.左侧标签栏
        #2.右侧选择句子栏
        # f = open('TreeCtrl.txt', 'w')
        # f.write('\n'.join(dir(wx.TreeCtrl)))
        # f.close()

        self.topicpanel = wx.Panel(self.notebook, -1)

        #1.标签栏
        #全选，反选框
        self.seleteall = wx.CheckBox(self.topicpanel, label = 'Not/All')
        self.seleteinv = wx.Button(self.topicpanel, label = 'Inverse', size = (60,23))
        self.Bind(wx.EVT_CHECKBOX, self.OnSelectall, self.seleteall)
        self.Bind(wx.EVT_BUTTON, self.OnSelectinv, self.seleteinv)
        self.box311 = wx.BoxSizer(wx.HORIZONTAL)
        self.box311.Add(self.seleteall)
        self.box311.Add(self.seleteinv)
        #标签列表
        self.topicList = self.maxtopic*[self.blank]
        self.topiccheck = []
        self.allidx = []
        text1 = wx.StaticText(self.topicpanel, label = 'Subtopics')
        for i, topic in enumerate(self.topicList):
            tmp = MyDragCheckBox(self.topicpanel, label = topic)
            tmp.SetForegroundColour(self.color[i])
            tmp.Hide()
            self.topiccheck.append(tmp)
        self.box3121 = wx.BoxSizer(wx.VERTICAL)
        self.box3121.Add(text1, 0, wx.ALL)
        for i in range(0, self.maxtopic):
            self.box3121.Add(self.topiccheck[i], 0, wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        #数字列表
        self.topicword = self.maxtopic*[0]
        self.wordspin = []
        text2 = wx.StaticText(self.topicpanel,label = '# of word')
        for i, num in enumerate(self.topicword):
            tmp = wx.SpinCtrl(self.topicpanel, value = '0', size = (60, 17), min = 50, max = 800)
            tmp.SetForegroundColour(self.color[i])
            tmp.Hide()
            self.wordspin.append(tmp)
        self.box3122 = wx.BoxSizer(wx.VERTICAL)
        self.box3122.Add(text2, 0, wx.EXPAND|wx.ALL)
        for i in range(0, self.maxtopic):
            self.box3122.Add(self.wordspin[i], 0, wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        #将标签和数字放入一个Box内
        self.box312 = wx.BoxSizer(wx.HORIZONTAL)
        self.box312.Add(self.box3121)
        self.box312.Add(self.box3122)
        #点击blobtn按钮，会在选择块栏显示相应的按钮和块
        self.blobtn = wx.Button(self.topicpanel, label = 'Text Blocks', style = wx.BU_EXACTFIT)
        self.blobtn.Bind(wx.EVT_BUTTON, self.OnBlobtn)
        #综述按钮
        self.sumbtn = wx.Button(self.topicpanel, label = 'Synthesize', style = wx.BU_EXACTFIT)
        self.sumbtn.Bind(wx.EVT_BUTTON, self.OnSummary)
        #将按钮合并在一个框内
        self.box313 = wx.BoxSizer(wx.HORIZONTAL)
        self.box313.Add(self.blobtn, 0, wx.EXPAND|wx.ALL)
        self.box313.Add(self.sumbtn, 0, wx.EXPAND|wx.ALL)

        statbox = wx.StaticBox(self.topicpanel, -1, 'Status')
        self.boxstat = wx.StaticBoxSizer(statbox, wx.VERTICAL)
        self.statinfo = wx.TextCtrl(self.topicpanel, size = (-1, 150), style = wx.TE_MULTILINE|wx.TE_READONLY)
        self.boxstat.Add(self.statinfo, 1, wx.ALL|wx.EXPAND)

        #将上述部件放入一个Box内
        staticbox1 = wx.StaticBox(self.topicpanel, -1, 'Set Subtopics')
        self.box31u = wx.StaticBoxSizer(staticbox1, wx.VERTICAL)
        self.box31u.Add(self.box311, 0, wx.ALL|wx.EXPAND)
        self.box31u.Add(self.box312, 0, wx.ALL|wx.EXPAND)
        self.box31u.Add(self.box313, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, border = 2)

        self.box31 = wx.BoxSizer(wx.VERTICAL)
        self.box31.Add(self.box31u, 0, wx.ALL|wx.EXPAND)
        self.box31.Add(self.boxstat, 0, wx.ALL|wx.EXPAND)

        #2.右侧选择句子栏
        #上方带颜色的按钮
        self.bbtnpanel = wx.Panel(self.topicpanel, -1)
        self.bbtnpanel.SetBackgroundColour((240, 240, 240, 255))
        self.blockbtn = []
        for i in range(0, self.maxtopic):
            tmp = wx.Button(self.bbtnpanel, id = 100+i, size=(20,20)) #id号用于得到事件处理
            tmp.SetBackgroundColour(self.color[i])
            tmp.Bind(wx.EVT_BUTTON, self.ShowBlock)
            self.blockbtn.append(tmp)
            tmp.Hide()
        #将上方按钮放置在GridSizer内
        # self.box321 = wx.GridSizer(cols = 20)
        self.box321 = wx.BoxSizer(wx.HORIZONTAL)
        for i in range(0, self.maxtopic):
            self.box321.Add(self.blockbtn[i], 0, wx.ALL|wx.EXPAND)
        self.bbtnpanel.SetSizer(self.box321)

        #中间添加全选、反选按钮
        self.btnpanel = wx.Panel(self.topicpanel, -1)
        self.btnpanel.SetBackgroundColour((240, 240, 240, 255))
        self.btnbox = wx.BoxSizer(wx.HORIZONTAL)
        self.bsall = wx.CheckBox(self.btnpanel, -1, 'Not/All')
        self.bsinv = wx.Button(self.btnpanel, -1, 'Inverse', size = (60, 23), style = wx.BU_EXACTFIT)
        self.bsall.Bind(wx.EVT_CHECKBOX, self.OnBsall)
        self.bsinv.Bind(wx.EVT_BUTTON, self.OnBsinv)
        # self.graybtn = wx.Button(self.btnpanel, -1, size=(15,15), style=wx.BU_EXACTFIT)
        # self.jumptext = wx.StaticText(self.btnpanel, -1, ' :Jump to news')
        self.btnbox.Add(self.bsall)
        self.btnbox.Add(self.bsinv)
        # self.btnbox.Add((10,-1))
        # self.btnbox.Add(self.graybtn)
        # self.btnbox.Add(self.jumptext)
        self.bsall.Hide(); self.bsinv.Hide()
        # self.graybtn.Hide(); self.jumptext.Hide()
        self.btnpanel.SetSizer(self.btnbox)

        #下方供选择句子
        self.blockpanel = wx.ScrolledWindow(self.topicpanel, -1)
        self.blockpanel.SetBackgroundColour((240, 240, 240, 255))
        self.blockpanel.SetScrollbars(1,1,100,100)
        self.blocktext = []
        self.blockcheck = []
        self.blocknewsbtn = [] #联系块到新闻的按钮
        tmpbox = wx.FlexGridSizer(cols = 2, vgap = 10, hgap = 40)
        tmpbox.AddGrowableCol(0, 1)
        tmpbox.AddGrowableCol(1, 8)
        for i in range(0, self.maxblockcnt):
            tmpcheck = wx.CheckBox(self.blockpanel, -1)
            tmpbtn = wx.Button(self.blockpanel, 200+i, label = 'Original news', style = wx.BU_EXACTFIT)
            tmpbtn.Bind(wx.EVT_BUTTON, self.Jump2News)
            ttbox = wx.BoxSizer(wx.VERTICAL)
            ttbox.Add(tmpcheck, 0, wx.ALIGN_LEFT)
            ttbox.Add((-1, 10))
            ttbox.Add(tmpbtn, 0, wx.ALIGN_LEFT)
            tmptext = wx.TextCtrl(self.blockpanel, -1, size = (-1, 150), style = wx.TE_MULTILINE)
            tmpbox.Add(ttbox, 0, wx.ALIGN_LEFT)
            tmpbox.Add(tmptext, 1, wx.EXPAND|wx.ALL)
            tmptext.Hide()
            tmpcheck.Hide()
            tmpbtn.Hide()
            self.blocktext.append(tmptext)
            self.blockcheck.append(tmpcheck)
            self.blocknewsbtn.append(tmpbtn)
        self.blockpanel.SetSizer(tmpbox)

        #将按钮和CheckListCtrl放入一个垂直的box内
        staticbox2 = wx.StaticBox(self.topicpanel, -1, 'Set text blocks')
        self.box32 = wx.StaticBoxSizer(staticbox2, wx.VERTICAL)
        self.box32.Add(self.bbtnpanel, 0, wx.ALL|wx.EXPAND, border = 1)
        self.box32.Add(self.btnpanel, 0, wx.ALL|wx.EXPAND, border = 1)
        self.box32.Add(self.blockpanel, 1, wx.ALL|wx.EXPAND, border = 1)

        #将上述的box31、box32组合到一个box内
        self.box3 = wx.BoxSizer(wx.HORIZONTAL)
        self.box3.Add(self.box31, 0)
        self.box3.Add(self.box32, 1, wx.EXPAND|wx.ALL)

        self.topicpanel.SetSizer(self.box3)

    def WorkStation(self):
        #最右侧的综述栏
        #上面的自动生成的、不可编辑的综述
        text1 = wx.StaticBox(self.panel, -1, 'Work On Synthesis')
        self.box41 = wx.StaticBoxSizer(text1, wx.VERTICAL)
        self.solidsum = wx.TextCtrl(self.panel, style = wx.TE_MULTILINE|wx.TE_RICH)
        # self.solidsum.SetBackgroundColour((240, 240, 240, 255)) #设置颜色为传统的灰色，直观上给人只读的感受
        self.box41.Add(self.solidsum, 1, wx.ALL|wx.EXPAND)

        self.box4 = wx.BoxSizer(wx.VERTICAL)
        self.box4.Add(self.box41, 1, wx.EXPAND|wx.ALL)


    def SetLocation(self):
        self.boxson = wx.BoxSizer(wx.HORIZONTAL)
        self.boxson.Add(self.notebook, 7, wx.EXPAND|wx.ALL)
        self.boxson.Add(self.box4, 5, wx.EXPAND|wx.ALL)
        self.boxbig = wx.BoxSizer(wx.VERTICAL)
        self.boxbig.Add(self.box1, 0, wx.EXPAND|wx.ALL)
        self.boxbig.Add(self.boxson, 1, wx.EXPAND|wx.ALL)

    def Go(self):
        self.panel.SetSizer(self.boxbig)
        self.panel.SetAutoLayout(True)
        self.boxbig.Fit(self.panel)
        self.Centre()
        self.Show()

    def OnBsall(self, e):
        if self.bsall.IsChecked():
            for i in range(0, self.k):
                self.blockcheck[i].SetValue(True)
        else:
            for i in range(0, self.k):
                self.blockcheck[i].SetValue(False)

    def OnBsinv(self, e):
        for i in range(0, self.k):
            curvalue = self.blockcheck[i].GetValue()
            self.blockcheck[i].SetValue(1-curvalue)

    def OnBlobtn(self, e):
        showi, minidx = -1, self.maxtopic+10

        for i in range(0, self.n):
            if self.topiccheck[i].IsChecked():
                self.blockbtn[i].ShowWithEffect(wx.SHOW_EFFECT_SLIDE_TO_LEFT) #带感的展示
                if self.allidx[i] < minidx:
                    minidx = self.allidx[i]
                    showi = i
            else:
                self.blockbtn[i].Hide()

        if self.lasttopic == -1 or self.topiccheck[self.lasttopic].GetValue() == False:
            #没有选中哪一个颜色按钮或者当前的块对应的标签被撤销选中了
            #就隐藏全部的
            self.bsall.Hide(); self.bsinv.Hide()
            # self.graybtn.Hide();self.jumptext.Hide()
            for i in range(0, self.maxblockcnt):
                self.blockcheck[i].Hide()
                self.blocktext[i].Hide()
                self.blocknewsbtn[i].Hide()
        if showi == -1:
            #没有标签被选中
            self.box32.Layout()
            return
        if self.lasttopic != -1 and self.topiccheck[self.lasttopic].GetValue() == True:
            self.box32.Layout()
            return
        #现在的场景：有颜色按钮，需要填充“选择块”区域，使用第showi的标签对应的块
        self.bsall.Show(); self.bsinv.Show()
        # self.graybtn.Show(); self.jumptext.Show()
        curtopic = self.topics[showi]
        self.k = min(curtopic.blockcnt, self.maxblockcnt)
        for i in range(0, self.k):
            self.blocktext[i].SetValue(curtopic.blocks[i])
            self.blocktext[i].SetForegroundColour(self.color[showi])
            self.blockcheck[i].SetValue(curtopic.blockchecks[i])
        for i in range(0, self.k):
            # self.blocktext[i].ShowWithEffect(wx.SHOW_EFFECT_SLIDE_TO_LEFT)
            # self.blocknewsbtn[i].ShowWithEffect(wx.SHOW_EFFECT_SLIDE_TO_LEFT)
            # self.blockcheck[i].ShowWithEffect(wx.SHOW_EFFECT_SLIDE_TO_LEFT)
            self.blocktext[i].Show()
            self.blocknewsbtn[i].Show()
            self.blockcheck[i].Show()
        self.box32.Layout()

        self.lasttopic = showi
        self.AddStat(('label %s has %d blocks totally.')%(self.topics[showi].label, self.k))



    def ShowBlock(self, e):
        if self.lasttopic != -1:
            #保存对它所做的修改，包括选了哪些块，对块的修改
            self.UpdateBlock(self.lasttopic)
            b = min(self.topics[self.lasttopic].blockcnt, self.maxblockcnt)
            for i in range(0, b):
                self.blocktext[i].Hide()
                self.blockcheck[i].Hide()
                self.blocknewsbtn[i].Hide()

        curid = e.GetId()
        curid -= 100
        curtopic = self.topics[curid]
        self.k = min(curtopic.blockcnt, self.maxblockcnt)
        for i in range(0, self.k):
            self.blocktext[i].SetValue(curtopic.blocks[i])
            self.blocktext[i].SetForegroundColour(self.color[curid])
            self.blockcheck[i].SetValue(curtopic.blockchecks[i])
        for i in range(0, self.k):
            self.blocktext[i].Show()
            self.blocknewsbtn[i].Show()
            self.blockcheck[i].Show()

        self.lasttopic = curid
        self.box32.Layout()

        self.AddStat(('label %s has %d blocks totally.')%(self.topics[curid].label, self.k))

    def Jump2News(self, e):
        blockidx = e.GetId()-200
        topicidx = self.lasttopic  #没想到当初设置的这个变量是这么的有用
                                   #以至于其实过其名了
        newsidx = self.topics[topicidx].newsidx[blockidx] - 1
        #跳到News的标签页，选中对应的新闻标题，并显示其内容
        self.notebook.SetSelection(0) #跳到News页
        self.newstree.SelectItem(self.newsid[newsidx])

        self.AddStat(('block %d of label:%s jumping to news %d')%(blockidx, self.topics[topicidx].label, newsidx))



    def search(self):
        if self.newsname == '':
            return
        self.MyRefresh()
        #类似于记录历史记录
        if self.newsname not in self.history:
            self.history.append(self.newsname)
            self.input.AppendItems(self.newsname)

        self.AddStat(('Current event: %s is being searched...')%(self.newsname))

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
                self.newstree.SetItemText(self.newsid[i], newsname[i])
            self.AddStat(('%d news crawled.')%(self.maxnewsnum))
        else:
            for i in range(0, newcnt):
                self.newstree.SetItemText(self.newsid[i], newsname[i])
            for i in range(newcnt, self.maxnewsnum):
                self.newstree.SetItemText(self.newsid[i], '')
            self.AddStat(('%d news crawled.')%(newcnt))
        #展开新闻树
        self.newstree.Expand(self.newsroot)


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
                    topic = topic + (standlen-curlen)/2*' '
                curcheck.SetLabel(topic);curspin.SetValue(250)
                curcheck.Show();curspin.Show()
        #为了能拖动多选框要做的初始化工作
        self.n = min(len(self.topicList), self.maxtopic)
        self.allidx = [i for i in range(0, self.n)]
        for i in range(0, self.n):
            self.topiccheck[i].Set(i, self.n, self.topiccheck, self.allidx, self.wordspin, self)
        self.AddStat(('%d topics totally.')%(len(self.topicList)))

        #得到每个标签的块
        self.topics = []
        for i in range(0, self.n):
            tmp = Topic()
            tmp.label = self.topiccheck[i].GetLabel().strip()
            tmp.checked = False
            #打开blockscore里的文件，得到该标签对应的块
            f = open('blockscore/'+self.newsname+'/'+tmp.label+'.txt', 'r')
            while True:
                num = f.readline()
                if len(num) == 0:
                    f.close()
                    break
                num = int(num)
                tmpblock = ''
                nums = '' #取原始块中第一个句子的5个数字（位置信息）
                          #作为被修改后的块的位置信息
                for j in range(0, num):
                    if j == 0:
                        nums = f.readline().strip()
                    else:
                        f.readline()
                    tmpblock += f.readline().strip()
                tmp.blocks.append(tmpblock)
                tmp.blockchecks.append(True)
                tmp.blocknums.append(nums)
                tmpnidx = int(nums.split()[0])
                tmp.newsidx.append(tmpnidx)
            tmp.blockcnt = len(tmp.blocks)
            self.topics.append(tmp)

        self.boxbig.Layout()

    def summary(self):
        #把每个标签对应的综述，经过后处理，输出
        if self.newsname == '':
            return

        #得到所选的标签
        selectTopic = []
        selectTopicid = []
        selectColor = []
        for i in range(0, self.n):
            truei = self.allidx[i]  #生成总数的顺序是从上往下数的
            if self.topiccheck[truei].IsChecked():
                curlabel = self.topiccheck[truei].GetLabel()
                curlabel = curlabel.strip() #去掉末尾的空格
                selectTopic.append(curlabel)
                selectTopicid.append(truei)
                self.AddStat(curlabel+'Chosen')
                selectColor.append(self.color[truei])

        selecnt = len(selectTopic)
        if selecnt == 0:
            self.AddStat('No topic in selected.')
            return
        elif selecnt == 1:
            self.AddStat('1 topic is selected.')
        else:
            self.AddStat(('%d topics are selected.')%(selecnt))

        self.AddStat('Processing...')

        #对选择的标签，将其被选择的块写入blockscoretmp文件，然后经过
        #sort.py的getTopicSum，得到该标签的（交互式）综述，放入topic_sumtmp
        #中，然后再经过getSum生成总的综述
        #0.在做下面的之前，先把修改过的更新到Topic结构中
        if self.lasttopic != -1:
            self.UpdateBlock(self.lasttopic)
        notuse = [0 for tid in selectTopicid] #记录是否对该标签生成综述
        #1.写入blockscoretmp文件
        for i, tid in enumerate(selectTopicid):
            curtopic = self.topics[tid]
            wordcnt = 0
            f = open('blockscoretmp/'+self.newsname+'/'+curtopic.label+'.txt', 'w')
            f.write('')
            for j, block in enumerate(curtopic.blocks):
                if j >= self.k:
                    break
                if curtopic.blockchecks[j] == True:
                    #将它输入到f里
                    f.write('1\n')
                    f.write(curtopic.blocknums[j]+'\n')
                    f.write(block.replace('\n','')+'\n') #这儿确实需要去掉'\n'，因为要满足blockscore文件的格式
                                                     #才能被sort.py中处理
                    wordcnt += len(block)/3
            f.close()

            #2.运行sort.py中的getTopicSum，得到每个标签的综述
            std = self.wordspin[tid].GetValue()
            if wordcnt < std - 40:
                #字数不够啊，报错
                self.AddStat(('Error in generating synthesis of %s:# of word is too big or the chosen block is too little')%(curtopic.label))
                notuse[i] = 1
                continue
            sort.getTopicSum(self.newsname, curtopic.label, std, model, stoplist, segmentor)

        tmpselectTopic, tmpselectColor = [], []
        for i, top in enumerate(selectTopic):
            if notuse[i] == 0:
                tmpselectTopic.append(top)
                tmpselectColor.append(selectColor[i])

        #3.根据所选的标签，以及它们对应的块，经post_process.py，得到综述
        post_process.getSum(self.newsname, tmpselectTopic, model, stoplist, segmentor)
        #输出到Auto generated summary框中
        f = open('sumtmp/'+self.newsname+'.txt', 'r')
        tmpsummary = f.read()
        f.close()

        self.solidsum.SetValue('')
        #在solidsum中，标签使用对应的色彩
        if tmpsummary == '':
            self.AddStat('Nothing to synthesize')
            return

        tmpsummary = tmpsummary.split('\n')
        i, j = 0, 0
        tmptmp = ''
        # print tmpsummary
        while i < len(tmpselectTopic):
            if tmpsummary[j] == '':
                if tmptmp != '':
                    self.solidsum.SetDefaultStyle(wx.TextAttr(tmpselectColor[i]))
                    self.solidsum.AppendText(tmptmp+'\n')
                    tmptmp = ''
                    i += 1
            else:
                tmptmp += tmpsummary[j]+'\n'
            j += 1

        self.AddStat('Synthesis done.')

    def OnEventEnter(self, e):
        self.newsname = self.input.GetValue()
        self.search()

    def OnEventSelect(self, e):
        # self.newsname = self.input.GetStringSelection()
        self.newsname = self.input.GetValue()
        self.search()

    def OnSummary(self, e):
        self.summary()

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
            if self.newstree.IsSelected(self.newsid[i]):
                if self.newsname != '':
                    f = open('../News/'+self.newsname+'/'+str(i+1)+'.txt')
                    self.newscontent.SetValue(f.read())
                    f.close()
                    self.AddStat('One news is selected.')
                    break


    def MyRefresh(self):
        self.solidsum.SetValue('')
        self.newscontent.SetValue('')
        #将所有多选框和数字调控按钮设置为不可见，并将值初始化
        for i in range(0, self.maxtopic):
            self.topiccheck[i].Hide();self.wordspin[i].Hide()
            self.topiccheck[i].SetLabel(self.blank)
            self.topiccheck[i].SetValue(False)
            self.wordspin[i].SetValue(250)
            self.blockbtn[i].Hide()
        for i in range(0, self.maxnewsnum):
            self.newstree.SetItemText(self.newsid[i], '')
        self.lasttopic = -1
        self.bsall.Hide(); self.bsinv.Hide()
        # self.graybtn.Hide(); self.jumptext.Hide()
        for i in range(0, self.maxblockcnt):
            self.blockcheck[i].SetValue(True)
            self.blocktext[i].SetValue('')
            self.blockcheck[i].Hide()
            self.blocktext[i].Hide()
            self.blocknewsbtn[i].Hide()
        self.boxbig.Layout()
        self.newstree.Collapse(self.newsroot) #折叠新闻树，有始有终
        self.AddStat('Clear done.')

    def OnQuick(self, e):
        self.newsname = self.input.GetValue()
        #如果画面中有内容，因为快捷模式会清空
        #所以要询问是否要继续快捷模式
        if self.newsname == '':
            helpok = False
            for i in range(0, self.maxtopic):
                if self.topiccheck[i].IsShown():
                    helpok = True
                    break
            if helpok:
                helps = 'The input box is empty and there exist contents! Are you sure continuing? '
                dlg = wx.MessageDialog(self.panel, helps, 'Warning', wx.OK|wx.CANCEL)
                if dlg.ShowModal() != wx.ID_OK:
                    return
            self.MyRefresh()
            return
        self.search()
        #选择前5个标签生成综述
        for i in range(0, 5):
            self.topiccheck[i].SetValue(True)
        self.OnBlobtn(e)
        self.summary()

    def OnSave(self, e):
        dlg = wx.FileDialog(self, defaultFile = self.newsname+'_synthesi.txt',
         style = wx.FD_SAVE, name = 'Save this synthesis')
        if dlg.ShowModal() == wx.ID_OK:
            f = codecs.open(dlg.GetPath(), 'w', 'utf8')
            f.write(self.solidsum.GetValue())
            f.close()
            self.AddStat(('The synthesis of %s is saved.')%(self.newsname))
        dlg.Destroy()

    def OnRefresh(self, e):
        self.MyRefresh()


    def OnAbout(self, e):
        helps = 'Given an event name, this app will crawl a set of news about it. '
        helps += 'Then it will find several topics from them. You can choose some topics, '
        helps += 'and this app will generate a summary about these topics.'
        wx.MessageBox(helps, 'Guide', wx.OK|wx.ICON_INFORMATION)

    def OnExit(self, e):
        self.Close(True)

    def AddStat(self, s):
        self.statinfo.AppendText(s+'\n')
        self.statinfo_copy.AppendText(s+'\n')

    def UpdateBlock(self, lasttopic):
        #把修改过的块更新到Topic结构中
        curtopic = self.topics[lasttopic]
        b = min(curtopic.blockcnt, self.maxblockcnt)
        for i in range(0, b):
            curtopic.blockchecks[i] = self.blockcheck[i].GetValue()
            curtopic.blocks[i] = self.blocktext[i].GetValue()


app = wx.App()
frame = MyWin(None, 'A Interactive News Synthesis System')
auim = wx.aui.AuiManager()
auim.AddPane(frame)
app.MainLoop()

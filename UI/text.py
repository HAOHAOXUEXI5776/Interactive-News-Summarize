import wx
class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=(400,300))
        self.scroll = wx.ScrolledWindow(self, -1)
        self.scroll.SetScrollbars(1,1,600,400)
        img1 = wx.Image('1.jpg', wx.BITMAP_TYPE_ANY)
        self.sb1 = wx.StaticBitmap(self.scroll,2,wx.Bitmap(img1), pos=(40,100))
        self.button = wx.Button(self.scroll, -1, "Scroll Me", pos=(50, 20))
        self.Bind(wx.EVT_BUTTON,  self.OnClickTop, self.button)
        self.button2 = wx.Button(self.scroll, -1, "Scroll Back", pos=(500, 350))
        self.Bind(wx.EVT_BUTTON, self.OnClickBottom, self.button2)

    def OnClickTop(self, event):
        self.scroll.Scroll(600, 400)
    def OnClickBottom(self, event):
        self.scroll.Scroll(1, 1)

app = wx.App()
fr = MyFrame()
fr.Show()
app.MainLoop()

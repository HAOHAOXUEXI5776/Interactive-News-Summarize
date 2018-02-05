import wx
class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=(400,300))
        pnl = wx.Panel(self, -1)
        # self.scroll = wx.ScrolledWindow(self, -1)
        # self.scroll.SetScrollbars(1,1,600,400)
        img1 = wx.Image('News_image.jpg', wx.BITMAP_TYPE_ANY)
        img1.Rescale(100,80)
        sb1 = img1.ConvertToBitmap()
        img_pic1 = wx.BitmapButton(pnl, -1, sb1)


app = wx.App()
fr = MyFrame()
fr.Show()
app.MainLoop()

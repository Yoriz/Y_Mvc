'''
Created on 28 Mar 2013

@author: Dave Wilson
'''

import wx
import ymvc


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)
        self.view = ymvc.View(self)

        panel = wx.Panel(self)
        self.labelAttr1 = wx.StaticText(panel)
        self.textAttr1 = wx.TextCtrl(panel)
        self.labelAttr2 = wx.StaticText(panel)
        self.textAttr2 = wx.TextCtrl(panel)
        self.btnOpen = wx.Button(panel, wx.ID_OPEN)

        fGridSizer = wx.FlexGridSizer(cols=2, vgap=7, hgap=4)
        fGridSizer.Add(self.textAttr1, flag=wx.ALIGN_CENTER_VERTICAL)
        fGridSizer.Add(self.labelAttr1, flag=wx.ALIGN_CENTER_VERTICAL)
        fGridSizer.Add(self.textAttr2, flag=wx.ALIGN_CENTER_VERTICAL)
        fGridSizer.Add(self.labelAttr2, flag=wx.ALIGN_CENTER_VERTICAL)

        pSizer = wx.BoxSizer(wx.VERTICAL)
        pSizer.Add(fGridSizer, 0, wx.ALIGN_CENTER | wx.ALL, 7)
        pSizer.Add(self.btnOpen, 0, wx.ALIGN_CENTER | wx.ALL, 7)

        fSizer = wx.BoxSizer(wx.VERTICAL)
        fSizer.Add(panel, 1, wx.EXPAND)

        panel.SetSizer(pSizer)
        self.SetSizer(fSizer)
        self.Layout()

        self.textAttr1.Bind(wx.EVT_TEXT,
            lambda event: self.view.notify_kw(attr1=event.String))

        self.textAttr2.Bind(wx.EVT_TEXT,
            lambda event: self.view.notify_kw(attr2=event.String))

        self.btnOpen.Bind(wx.EVT_BUTTON, lambda _: self.view.notify_msg('Open'))

    def setAttr1(self, attr1):
        self.labelAttr1.SetLabel(attr1)
        self.SetTitle(attr1)
        insertionPoint = self.textAttr1.GetInsertionPoint()
        self.textAttr1.ChangeValue(attr1)
        self.textAttr1.SetInsertionPoint(insertionPoint)

    def setAttr2(self, attr2):
        self.labelAttr2.SetLabel(attr2)
        insertionPoint = self.textAttr2.GetInsertionPoint()
        self.textAttr2.ChangeValue(attr2)
        self.textAttr2.SetInsertionPoint(insertionPoint)

    def createFrame(self):
        frame = MainFrame(None)
        frame.Show()
        return frame


class MainFrameMediator(ymvc.Mediator):
    def __init__(self):
        super(MainFrameMediator, self).__init__('MainFrame')

    def on_create_binds(self):
        self.attrModel = self.proxy_store['attrModel']
        self.view.bind(self.onViewAttr1)
        self.view.bind(self.onViewAttr2)
        self.view.bind(self.onOpen)
        self.attrModel.bind(self.onAttrModelAttr1)
        self.attrModel.bind(self.onAttrModelAttr2)

    @ymvc.on_kw_signal
    def onViewAttr1(self, attr1):
        self.attrModel.attr1 = attr1

    @ymvc.on_kw_signal
    def onViewAttr2(self, attr2):
        self.attrModel.attr2 = attr2

    @ymvc.on_msg_signal('Open')
    def onOpen(self):
        frame = self.gui.createFrame()
        frame.view.set_mediator(MainFrameMediator())

    @ymvc.wx_callafter
    @ymvc.on_attr_signal
    def onAttrModelAttr1(self, attr1):
        self.gui.setAttr1(attr1)

    @ymvc.wx_callafter
    @ymvc.on_attr_signal
    def onAttrModelAttr2(self, attr2):
        self.gui.setAttr2(attr2)

    def on_view_destroyed(self):
        print 'ViewDestroyed'


class AttrModel(ymvc.Proxy):

    def __init__(self, attr1='', attr2=''):
        super(AttrModel, self).__init__()
        self.add_obs_attrs('attr1', 'attr2')
        self.attr1 = attr1
        self.attr2 = attr2


if __name__ == '__main__':

    ymvc.proxy_store['attrModel'] = AttrModel('Attr1', 'Attr2')
    wxapp = wx.App(False)
    mainFrame = MainFrame(None)
    mainFrame.view.set_mediator(MainFrameMediator())
    mainFrame.Show()
    wxapp.MainLoop()

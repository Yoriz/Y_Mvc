'''
Created on 8 Apr 2013

@author: Dave Wilson
'''


import wx
from wxAnyThread import anythread
import ymvc

MAIN_FRAME = 'MainFrame'
CHILD_FRAME1 = 'ChildFrame1'
CHILD_FRAME2 = 'ChildFrame2'
CHILD_FRAME3 = 'ChildFrame2'


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)
        self.view = ymvc.View(self)

        panel = wx.Panel(self)
        self.txtCtrl = wx.TextCtrl(panel, size=(200, -1))
        self.btn = wx.Button(panel, label='Signal ChildFrames')
        self.btn1 = wx.Button(panel, label='Open ChildFrame1')
        self.btn2 = wx.Button(panel, label='Open ChildFrame2')
        self.btn3 = wx.Button(panel, label='Open ChildFrame3')

        fgSizer = wx.FlexGridSizer(cols=2, vgap=7, hgap=4)
        self.createControls(panel, fgSizer, 1)
        self.createControls(panel, fgSizer, 2)
        self.createControls(panel, fgSizer, 3)
        fgSizer.Add(self.txtCtrl, flag=wx.ALIGN_CENTER)
        fgSizer.Add(self.btn, flag=wx.ALIGN_CENTER)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(self.btn1)
        btnSizer.Add(self.btn2)
        btnSizer.Add(self.btn3)

        vSizer = wx.BoxSizer(wx.VERTICAL)
        vSizer.AddSpacer((0, 7))
        vSizer.Add(fgSizer, 0, wx.ALIGN_CENTER | wx.ALL, 7)
        vSizer.AddSpacer((0, 7))
        vSizer.Add(btnSizer, 0, wx.ALIGN_CENTER)
        panel.SetSizer(vSizer)

        fSizer = wx.BoxSizer(wx.VERTICAL)
        fSizer.Add(panel, 1, wx.EXPAND)

        self.SetSizer(fSizer)
        self.Layout()

        self.btn.Bind(wx.EVT_BUTTON, self.onBtn)
        self.btn1.Bind(wx.EVT_BUTTON, self.onBtn)
        self.btn2.Bind(wx.EVT_BUTTON, self.onBtn)
        self.btn3.Bind(wx.EVT_BUTTON, self.onBtn)

    def createControls(self, parent, sizer, number):
        stcTxtA = wx.StaticText(parent,
                            label='Signal From ChildFrame{}'.format(number))
        stcTxtB = wx.StaticText(parent, label='Nothing yet')
        sizer.Add(stcTxtA, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER)
        sizer.Add(stcTxtB, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER)
        setattr(self, 'stcTxtA{}'.format(number), stcTxtA)
        setattr(self, 'stcTxtB{}'.format(number), stcTxtB)

    def onBtn(self, event):
        if event.EventObject == self.btn:
            value = self.txtCtrl.GetValue()
            self.view.notifyKw(txtCtrl=value)
        elif event.EventObject == self.btn1:
            self.view.notifyMsg('Button1')
        elif event.EventObject == self.btn2:
            self.view.notifyMsg('Button2')
        elif event.EventObject == self.btn3:
            self.view.notifyMsg('Button3')

    @anythread
    def setStcTxtB(self, number, value):
        getattr(self, 'stcTxtB{}'.format(number)).SetLabel(value)
        self.Layout()

    @anythread
    def btnEnable(self, number, enable=True):
        getattr(self, 'btn{}'.format(number)).Enable(enable)

    def createChildFrame(self, no1, no2, no3):
        frame = BaseChildFrame(self)
        frame.setUpNames(no1, no2, no3)
        frame.Show()
        return frame


class MainFrameMediator(ymvc.Mediator):
    def __init__(self):
        super(MainFrameMediator, self).__init__(MAIN_FRAME)

    def onCreateBinds(self):
        self.view.bind(self.onTxtCtrl)
        self.view.bind(self.onBtn1)
        self.view.bind(self.onBtn2)
        self.view.bind(self.onBtn3)
        self.bind(self.onTxt1)
        self.bind(self.onTxt2)
        self.bind(self.onTxt2)

    @ymvc.onKwSignal
    def onTxtCtrl(self, txtCtrl):
        self.notifyMsgKw(MAIN_FRAME, value=txtCtrl)

    @ymvc.onMsgSignal('Button1')
    def onBtn1(self):
        frame = self.gui.createChildFrame(1, 2, 3)
        self.gui.btnEnable(1, False)
        frame.view.setMediator(ChildFrameMediator(CHILD_FRAME1))

    @ymvc.onMsgSignal('Button2')
    def onBtn2(self):
        frame = self.gui.createChildFrame(2, 3, 1)
        self.gui.btnEnable(2, False)
        frame.view.setMediator(ChildFrameMediator(CHILD_FRAME2))

    @ymvc.onMsgSignal('Button3')
    def onBtn3(self):
        frame = self.gui.createChildFrame(3, 1, 2)
        self.gui.btnEnable(3, False)
        frame.view.setMediator(ChildFrameMediator(CHILD_FRAME3))

    @ymvc.onMsgKwSignal(CHILD_FRAME1)
    def onTxt1(self, value):
        self.gui.setStcTxtB(1, value)

    @ymvc.onMsgKwSignal(CHILD_FRAME2)
    def onTxt2(self, value):
        self.gui.setStcTxtB(2, value)

    @ymvc.onMsgKwSignal(CHILD_FRAME3)
    def onTxt3(self, value):
        self.gui.setStcTxtB(3, value)


class BaseChildFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(BaseChildFrame, self).__init__(*args, **kwargs)
        self.view = ymvc.View(self)

        panel = wx.Panel(self)
        fgSizer = wx.FlexGridSizer(cols=2, vgap=7, hgap=4)
        self.createControls(panel, fgSizer, 1)
        self.createControls(panel, fgSizer, 2)
        self.createControls(panel, fgSizer, 3)

        vSizer = wx.BoxSizer(wx.VERTICAL)
        vSizer.AddSpacer((0, 7))
        vSizer.Add(fgSizer, 0, wx.ALIGN_CENTER | wx.ALL, 7)
        vSizer.AddSpacer((0, 7))
        panel.SetSizer(vSizer)

        fSizer = wx.BoxSizer(wx.VERTICAL)
        fSizer.Add(panel, 1, wx.EXPAND)

        self.SetSizer(fSizer)

        self.stcTxtA1.SetLabel('Signal From MainFrame')
        self.btn1.SetLabel('Signal MainFrame')

        self.Layout()

    def createControls(self, parent, sizer, number):
        stcTxtA = wx.StaticText(parent)
        stcTxtB = wx.StaticText(parent, label='Nothing yet')
        txtCtrl = wx.TextCtrl(parent, size=(200, -1))
        btn = wx.Button(parent)
        btn.Bind(wx.EVT_BUTTON, self.onBtn)
        sizer.Add(stcTxtA, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER)
        sizer.Add(stcTxtB, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER)
        sizer.Add(txtCtrl, flag=wx.ALIGN_CENTER)
        sizer.Add(btn, flag=wx.ALIGN_CENTER)
        setattr(self, 'stcTxtA{}'.format(number), stcTxtA)
        setattr(self, 'stcTxtB{}'.format(number), stcTxtB)
        setattr(self, 'txtCtrl{}'.format(number), txtCtrl)
        setattr(self, 'btn{}'.format(number), btn)
        self.view.notifyMsg('btn{}'.format(number))

    def setUpNames(self, no1, no2, no3):
        self.SetTitle('ChildFrame{}'.format(no1))
        self.stcTxtA2.SetLabel('Signal From ChildFrame{}'.format(no2))
        self.btn2.SetLabel('Signal ChildFrame{}'.format(no2))
        self.stcTxtA3.SetLabel('Signal From ChildFrame{}'.format(no3))
        self.btn3.SetLabel('Signal ChildFrame{}'.format(no3))
        self.Layout()

    def onBtn(self, event):
        if event.EventObject == self.btn1:
            self.view.notifyKw(txtCtrl1=event.String)
        elif event.EventObject == self.btn2:
            self.view.notifyKw(txtCtrl2=event.String)
        elif event.EventObject == self.btn3:
            self.view.notifyKw(txtCtrl3=event.String)

    @anythread
    def setStcTxtB(self, number, value):
        getattr(self, 'stcTxtB{}'.format(number)).SetLabel(value)
        self.Layout()


class ChildFrameMediator(ymvc.Mediator):
    def __init__(self, uniqueName):
        super(ChildFrameMediator, self).__init__(uniqueName)

    def onCreateBinds(self):
#         self.view.bind(self.onBtn1)
#         self.view.bind(self.onBtn2)
#         self.view.bind(self.onBtn3)
        self.bind(self.onMainFrameTxt)
#         self.bind(self.onTxt2)
#         self.bind(self.onTxt2)

    @ymvc.onMsgSignal('Button1')
    def onBtn1(self):
        frame = self.gui.createChildFrame(1, 2, 3)
        self.gui.btnEnable(1, False)

    @ymvc.onMsgSignal('Button2')
    def onBtn2(self):
        frame = self.gui.createChildFrame(2, 3, 1)
        self.gui.btnEnable(2, False)

    @ymvc.onMsgSignal('Button3')
    def onBtn3(self):
        frame = self.gui.createChildFrame(3, 1, 2)
        self.gui.btnEnable(3, False)

    @ymvc.onMsgKwSignal(MAIN_FRAME)
    def onMainFrameTxt(self, value):
        self.gui.setStcTxtB(1, value)

    @ymvc.onMsgKwSignal('CHILD_FRAME2')
    def onTxt2(self, value):
        self.gui.setStcTxtB(2, value)

    @ymvc.onMsgKwSignal('CHILD_FRAME3')
    def onTxt3(self, value):
        self.gui.setStcTxtB(3, value)


if __name__ == '__main__':

    wxapp = wx.App(False)
    mainFrame = MainFrame(None, title='MainFrame')
    mainFrame.view.setMediator(MainFrameMediator())
    mainFrame.Show()
    wxapp.MainLoop()

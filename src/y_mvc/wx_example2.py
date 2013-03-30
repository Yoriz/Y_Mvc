'''
Created on 29 Mar 2013

@author: Dave Wilson
'''

import wx
from wxAnyThread import anythread
import time
import ymvc


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)
        self.view = ymvc.View(self)

        panel = wx.Panel(self)
        self.label1 = wx.StaticText(panel, label='0')
        self.btn = wx.Button(panel, label='start')

        pSizer = wx.BoxSizer(wx.VERTICAL)
        pSizer.Add(self.label1, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        pSizer.Add(self.btn, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 5)
        pSizer.AddSpacer((0, 5))

        fSizer = wx.BoxSizer(wx.VERTICAL)
        fSizer.Add(panel, 1, wx.EXPAND)

        panel.SetSizer(pSizer)
        self.SetSizer(fSizer)
        self.Fit()
        self.Layout()

        self.btn.Bind(wx.EVT_BUTTON, lambda x: self.view.notify('Start'))

    @anythread
    def setLabel(self, value):
        self.label1.SetLabel(str(value))

    @anythread
    def setButtonState(self, enabled=True):
        self.btn.Enable(enabled)


class MainFrameController(ymvc.Controller):

    def __init__(self, gui, delayedModel):
        super(MainFrameController, self).__init__(gui)
        self.delayedModel = delayedModel

        self.gui.view.bind(self.onViewStart)
        self.delayedModel.bind(self.onDelayedModelBusy)
        self.delayedModel.bind(self.onDelayedModelValue)

    @ymvc.onNotify('Start')
    def onViewStart(self):
        self.delayedModel.notify('StartCount')

    @ymvc.onNotifyKw('busy')
    def onDelayedModelBusy(self, busy):
        self.gui.setButtonState(not busy)

    @ymvc.onAttr('value')
    def onDelayedModelValue(self, value):
        self.gui.setLabel(value)


class DelayedModel(ymvc.Model):
    def __init__(self):
        super(DelayedModel, self).__init__('value')
        self.bind(self.startCount)
        self.value = 0

    @ymvc.onNotify('StartCount')
    def startCount(self):
        self.notifyKw(busy=True)
        for number in xrange(1, 11):
            time.sleep(1)
            self.value = number
        self.value = 0
        self.notifyKw(busy=False)


if __name__ == '__main__':
    delayedModel = DelayedModel()
    wxapp = wx.App(False)
    mainFrame = MainFrame(None)
    mainFrame.view.setController(MainFrameController, delayedModel)
    mainFrame.Show()
    wxapp.MainLoop()

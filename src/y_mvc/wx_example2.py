'''
Created on 29 Mar 2013

@author: Dave Wilson
'''

import wx
from wx_lib.wxdecorator import wxCallafter
from util.decorator import runAsync
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

        self.btn.Bind(wx.EVT_BUTTON, lambda x: self.view.notify_msg('Start'))

    def setLabel(self, value):
        self.label1.SetLabel(str(value))

    def setButtonState(self, enabled=True):
        self.btn.Enable(enabled)


class MainFrameMediator(ymvc.Mediator):

    def __init__(self, unique_name):
        super(MainFrameMediator, self).__init__(unique_name)

    def on_create_binds(self):

        self.delayedModel = self.model_store['delayedModel']

        self.view.bind(self.onViewStart)
        self.delayedModel.bind(self.onDelayedModelBusy)
        self.delayedModel.bind(self.onDelayedModelValue)

    @ymvc.on_msg_signal('Start')
    def onViewStart(self):
        self.delayedModel.notify_msg('StartCount')

    @wxCallafter
    @ymvc.on_kw_signal
    def onDelayedModelBusy(self, busy):
        self.gui.setButtonState(not busy)

    @wxCallafter
    @ymvc.on_attr_signal
    def onDelayedModelValue(self, value):
        self.gui.setLabel(value)


class DelayedModel(ymvc.Model):
    def __init__(self):
        super(DelayedModel, self).__init__()
        self.add_obs_attrs('value')
        self.bind(self.startCount)
        self.value = 0

    @runAsync
    @ymvc.on_msg_signal('StartCount')
    def startCount(self):
        self.notify_kw(busy=True)
        for number in xrange(1, 11):
            time.sleep(1)
            self.value = number
            print self.value
        self.value = 0
        self.notify_kw(busy=False)


if __name__ == '__main__':
    ymvc.model_store['delayedModel'] = DelayedModel()
    wxapp = wx.App(False)
    mainFrame = MainFrame(None)
    mainFrame.view.set_mediator(MainFrameMediator('MainFrameMediator'))
    mainFrame.Show()
    wxapp.MainLoop()

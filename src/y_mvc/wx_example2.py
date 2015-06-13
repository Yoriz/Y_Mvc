'''
Created on 29 Mar 2013

@author: Dave Wilson
'''

import time

from wx import gizmos
import wx
from wx.lib import sized_controls, intctrl

import ymvc2 as ymvc


class MainFrame(sized_controls.SizedFrame):

    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)

        pane = self.GetContentsPane()
        self.label1 = wx.StaticText(pane, label='0')
        self.label1.SetSizerProps(halign='center')
        self.ctrl_increment = intctrl.IntCtrl(pane, size=(50, -1))
        self.ctrl_increment.SetValue(1)
        self.ctrl_increment.SetToolTipString('Change the increment value')
        self.ctrl_increment.SetSizerProps(halign='center')
        self.btn_start = wx.Button(pane, label='Start')
        self.btn_start.SetSizerProps(halign='center')
        self.btn_stop = wx.Button(pane, label='Stop')
        self.btn_stop.Disable()
        self.btn_stop.SetSizerProps(halign='center')
        self.btn_led = wx.Button(pane, label='Create LED')
        self.btn_led.SetSizerProps(halign='center')
        pane.Sizer.AddSpacer(7, 7)
        self.SetInitialSize((200, -1))
        self.Fit()

    def set_label(self, value):
        self.label1.SetLabel(str(value))

    def set_button_state(self, enabled=True):
        self.btn_start.Enable(enabled)
        self.btn_stop.Enable(not enabled)


class LedFrame(sized_controls.SizedFrame):

    def __init__(self, *args, **kwargs):
        super(LedFrame, self).__init__(*args, **kwargs)
        pane = self.GetContentsPane()

        self.ctrl_led = gizmos.LEDNumberCtrl(pane)
        self.ctrl_led.SetSizerProps(align='center')
        self.ctrl_led.SetValue('0')
        self.ctrl_led.SetAlignment(gizmos.LED_ALIGN_CENTER)
        self.SetInitialSize((200, -1))
        self.Fit()

    def set_value(self, value):
        self.ctrl_led.SetValue(str(value))


class MainFrameMediator(ymvc.Mediator):

    def __init__(self):
        super(MainFrameMediator, self).__init__()

    def on_create_binds(self):

        self.busy_counter = self.proxy_store['busy_counter']

        self.gui.ctrl_increment.Bind(intctrl.EVT_INT, self.on_gui_ctrl_incr)
        self.gui.btn_start.Bind(wx.EVT_BUTTON, self.on_gui_btn_start)
        self.gui.btn_stop.Bind(wx.EVT_BUTTON, self.on_gui_btn_stop)
        self.gui.btn_led.Bind(wx.EVT_BUTTON, self.on_gui_btn_led)
        self.gui.Bind(wx.EVT_CLOSE, self.on_gui_closed)

        self.busy_counter.bind(self.on_busy_counter_busy)
        self.busy_counter.bind(self.on_busy_counter_value)

    def on_gui_ctrl_incr(self, event):
        print 'value changed'
        self.busy_counter.increment = event.GetValue()

    def on_gui_btn_start(self, event):
        self.busy_counter.start_count()

    def on_gui_btn_stop(self, event):
        self.busy_counter.stop_count()

    def on_gui_btn_led(self, event):
        frame = LedFrame(None)
        mediator = LedFrameMediator()
        mediator.attach_to_gui(frame)
        frame.Show()

    def on_gui_closed(self, event):
        self.busy_counter.stop_count()
        event.Skip()

    @ymvc.wx_callafter
    @ymvc.on_kw_signal
    def on_busy_counter_busy(self, busy):
        self.gui.set_button_state(not busy)

    @ymvc.wx_callafter
    @ymvc.on_attr_signal
    def on_busy_counter_value(self, value):
        self.gui.set_label(value)


class LedFrameMediator(ymvc.Mediator):

    def __init__(self):
        super(LedFrameMediator, self).__init__()

    def on_create_binds(self):

        self.busy_counter = self.proxy_store['busy_counter']
        self.busy_counter.bind(self.on_busy_counter_value)

    @ymvc.wx_callafter
    @ymvc.on_attr_signal
    def on_busy_counter_value(self, value):
        self.gui.set_value(value)


class BusyCounterProxy(ymvc.Proxy):

    def __init__(self):
        super(BusyCounterProxy, self).__init__()
        self.add_obs_attrs('value')
        self.value = 0
        self.increment = 1
        self._stop_counter = False

#     @ymvc.proxy_method
    @ymvc.run_async
    def start_count(self):
        self.notify_kw(busy=True)
        while not self._stop_counter:
            self.value = self.value + self.increment
            self.wait_in_queue()
            print self.value
            time.sleep(1)
            if self._stop_counter:
                break
        self._stop_counter = False
        self.value = 0
        self.notify_kw(busy=False)

#     @ymvc.proxy_method
    def stop_count(self):
        self._stop_counter = True


if __name__ == '__main__':
    ymvc.proxy_store['busy_counter'] = BusyCounterProxy()
    wxapp = wx.App(False)
    frame = MainFrame(None)
    mediator = MainFrameMediator()
    mediator.attach_to_gui(frame)
    frame.Show()
    wxapp.MainLoop()

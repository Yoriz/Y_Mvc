'''
Created on 28 Mar 2013

@author: Dave Wilson
'''

import wx
from wx.lib import sized_controls

import ymvc


class MainFrame(sized_controls.SizedFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pane = self.GetContentsPane()
        pane_form = sized_controls.SizedPanel(pane)
        pane_form.SetSizerType('form')
        label = wx.StaticText(pane_form, label='Attribute 1')
        label.SetSizerProps(halign='right', valign='center')
        self.text_attr1 = wx.TextCtrl(pane_form)
        label = wx.StaticText(pane_form, label='Attribute 2')
        label.SetSizerProps(halign='right', valign='center')
        self.text_attr2 = wx.TextCtrl(pane_form)
        pane_btns = sized_controls.SizedPanel(pane)
        pane_btns.SetSizerType('horizontal')
        pane_btns.SetSizerProps(
            border=(('right',), 7), halign='center')
        self.btn_open = wx.Button(pane_btns, wx.ID_OPEN)
        self.Fit()

    def set_attr1(self, attr1):
        insertionPoint = self.text_attr1.GetInsertionPoint()
        self.text_attr1.ChangeValue(attr1)
        self.text_attr1.SetInsertionPoint(insertionPoint)

    def set_attr2(self, attr2):
        insertionPoint = self.text_attr2.GetInsertionPoint()
        self.text_attr2.ChangeValue(attr2)
        self.text_attr2.SetInsertionPoint(insertionPoint)

    def create_frame(self):
        frame = MainFrame(None)
        frame.Show()
        return frame


class MainFrameMediator(ymvc.Mediator):

    def __init__(self):
        super().__init__('MainFrame')

    def on_create_binds(self):
        self.attr_proxy = ymvc.proxy_store['AttrProxy']
        self.gui.text_attr1.Bind(wx.EVT_TEXT, self.on_gui_attr1)
        self.gui.text_attr2.Bind(wx.EVT_TEXT, self.on_gui_attr2)
        self.gui.btn_open.Bind(wx.EVT_BUTTON, self.on_gui_open)
        self.attr_proxy.bind(self.on_attr_model_attr1)
        self.attr_proxy.bind(self.on_attr_model_attr2)

    def on_gui_attr1(self, event):
        self.attr_proxy.attr1 = event.String

    def on_gui_attr2(self, event):
        self.attr_proxy.attr2 = event.String

    def on_gui_open(self, event):
        frame = self.gui.create_frame()
        mediator = MainFrameMediator()
        mediator.attach_to_gui(frame)

    @ymvc.on_attr_signal
    def on_attr_model_attr1(self, attr1):
        self.gui.set_attr1(attr1)

    @ymvc.on_attr_signal
    def on_attr_model_attr2(self, attr2):
        self.gui.set_attr2(attr2)

    def on_view_destroyed(self):
        print('ViewDestroyed')

    def called_by(self, who):
        print('MainFrameMediator called by:', who)


class AttrProxy(ymvc.Proxy):

    def __init__(self, attr1='', attr2=''):
        super().__init__()
        self.add_obs_attrs('attr1', 'attr2')
        self.attr1 = attr1
        self.attr2 = attr2


if __name__ == '__main__':

    ymvc.proxy_store['AttrProxy'] = AttrProxy('Attr1', 'Attr2')
    wxapp = wx.App(False)
    frame = MainFrame(None)
    mediator = MainFrameMediator()
    ymvc.weak_mediator_store['MainFrameMediator'] = mediator
    mediator.attach_to_gui(frame)
    frame.Show()
    del frame
    wxapp.MainLoop()

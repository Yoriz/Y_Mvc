'''
Created on 5 Apr 2013

@author: Dave Wilson
'''

import wx
from wxAnyThread import anythread
from wx_lib.frames import GaugeFrame, FRAME_DIALOG_STYLE3
from y_mvc import ymvc
from olv_ctrl import OlvOwnSortHasIdColumn, OlvOwnSortHasIdColumnController
from page_selector_ctrl import PageSelectorCtrl, PageSelectorController


class PagedOlv(GaugeFrame):
    def __init__(self, *args, **kwargs):
        if not kwargs.get('sytle'):
            kwargs['style'] = FRAME_DIALOG_STYLE3
        super(PagedOlv, self).__init__(*args, **kwargs)
        self.view = ymvc.View(self)

        #------------------------------------------------------------- Controls
        panel = wx.Panel(self, style=wx.TAB_TRAVERSAL)
        self.ctrlOlv = OlvOwnSortHasIdColumn(panel)
        self.ctrlPage = PageSelectorCtrl(panel)
        self.btnNew = wx.Button(panel, wx.ID_NEW)
        self.btnEdit = wx.Button(panel, wx.ID_EDIT)
        self.btnSelectNone = wx.Button(panel, label='Select None')

        #--------------------------------------------------------------- Sizers
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        hSizer.Add(self.ctrlPage, 1)
        hSizer.AddSpacer((4, 0))
        hSizer.Add(self.btnNew)
        hSizer.Add(self.btnEdit, 0, wx.LEFT, 4)
        hSizer.Add(self.btnSelectNone, 0, wx.LEFT, 4)

        vSizer = wx.BoxSizer(wx.VERTICAL)
        vSizer.Add(self.ctrlOlv, 1, wx.EXPAND | wx.ALL, 7)
        vSizer.Add(hSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 7)
        vSizer.AddSpacer((0, 7))
        panel.SetSizer(vSizer)

        self.setPanel(panel)

        #------------------------------------------------------------- Settings
        self.SetInitialSize((800, 600))
        self.CenterOnParent()
        self.GetParent().Disable()

        #---------------------------------------------------------------- Binds
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.btnNew.Bind(wx.EVT_BUTTON, self.onBtnNew)
        self.btnEdit.Bind(wx.EVT_BUTTON, self.onBtnEdit)
        self.btnEdit.Bind(wx.EVT_UPDATE_UI, self.onBtnEditUpdate)
        self.btnSelectNone.Bind(wx.EVT_BUTTON, self.onBtnSelectNone)

    #------------------------------------------------------------------- Events
    def onClose(self, event):
        self.Close()

    def onBtnNew(self, event):
        self.view.notify('New')

    def onBtnEdit(self, event):
        self.view.notify('Edit')

    def onBtnEditUpdate(self, event):
        event.Enable(bool(self.ctrlOlv.selectedId))

    def onBtnSelectNone(self, event):
        self.ctrlOlv.DeselectAll()
        event.Skip()

    #------------------------------------------------------------------ Actions
    @anythread
    def Close(self):
        self.GetParent().Enable()
        self.Destroy()

    #------------------------------------------------------------------ Methods


class PagedOlvController(ymvc.Controller):
    def __init__(self, gui, itemsModel, pageSelectorModel):
        super(PagedOlvController, self).__init__(gui)
        self.gui.ctrlOlv.view.setController(OlvOwnSortHasIdColumnController,
                                       itemsModel)
        self.gui.ctrlPage.view.setController(PageSelectorController,
                                        pageSelectorModel)


if __name__ == '__main__':
    wxapp = wx.App(False)

    parentFrame = wx.Frame(None)
    parentFrame.Show()

    frame = PagedOlv(parentFrame)
#     accessModel = AccessModel()
#     frame.view.setController(MainAppController, accessModel)
    frame.Show()
    wxapp.MainLoop()
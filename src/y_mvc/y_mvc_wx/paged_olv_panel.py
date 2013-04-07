'''
Created on 5 Apr 2013

@author: Dave Wilson
'''

import wx
from y_mvc import ymvc
from olv_ctrl import OlvCtrl, OlvCtrlController
from page_selector_ctrl import PageSelectorCtrl, PageSelectorController


class PagedOlvPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(PagedOlvPanel, self).__init__(*args, **kwargs)
        self.view = ymvc.View(self)

        #------------------------------------------------------------- Controls
        self.ctrlOlv = OlvCtrl(self)
        self.ctrlPage = PageSelectorCtrl(self)
        self.btnNew = wx.Button(self, wx.ID_NEW)
        self.btnEdit = wx.Button(self, wx.ID_EDIT)
        self.btnSelectNone = wx.Button(self, label='Select None')

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
        self.SetSizer(vSizer)

        #------------------------------------------------------------- Settings
        #---------------------------------------------------------------- Binds
        self.btnNew.Bind(wx.EVT_BUTTON, self.onBtnNew)
        self.btnEdit.Bind(wx.EVT_BUTTON, self.onBtnEdit)
        self.btnEdit.Bind(wx.EVT_UPDATE_UI, self.onBtnEditUpdate)
        self.btnSelectNone.Bind(wx.EVT_BUTTON, self.onBtnSelectNone)

    #------------------------------------------------------------------- Events
    def onBtnNew(self, event):
        self.view.notifyMsg('New')

    def onBtnEdit(self, event):
        self.view.notifyMsg('Edit')

    def onBtnEditUpdate(self, event):
        event.Enable(bool(self.ctrlOlv.selectedId))

    def onBtnSelectNone(self, event):
        self.ctrlOlv.DeselectAll()
        event.Skip()

    #------------------------------------------------------------------ Actions
    #------------------------------------------------------------------ Methods


class PagedOlvPanelController(ymvc.Controller):
    def __init__(self, gui, ItemsModel, pageModel):
        super(PagedOlvPanelController, self).__init__(gui)
        self.gui.ctrlOlv.view.setController(OlvCtrlController,
                                       ItemsModel)
        self.gui.ctrlPage.view.setController(PageSelectorController,
                                        pageModel)
        self.ItemsModel = ItemsModel
        self.pageModel = pageModel


if __name__ == '__main__':
    from y_mvc.models.data_model import ItemsModel
    from y_mvc.models.page_model import PageModel

    itemsModel = ItemsModel()
    pageModel = PageModel()

    wxapp = wx.App(False)
    frame = wx.Frame(None)
    pagedOlvCtrl = PagedOlvPanel(frame)
    pagedOlvCtrl.view.setController(PagedOlvPanelController, itemsModel,
                                    pageModel)
    frame.Show()
    wxapp.MainLoop()

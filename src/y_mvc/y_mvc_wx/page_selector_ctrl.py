'''
Created on 31 Mar 2013

@author: Dave Wilson
'''

import wx
from wx_lib.wxdecorator import wxCallafter
from wx.lib.intctrl import IntCtrl
from y_mvc import ymvc

REQUEST_PAGE_NO = 'RequestPageNo'


def createBtn(parent, pSizer, label, tipText, handler, updateHandler=None):
    font = wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Webdings')
    ctrl = wx.Button(parent, label=label, size=(23, 23))
    ctrl.SetFont(font)
    ctrl.SetToolTipString(tipText)
    pSizer.Add(ctrl, 0, flag=wx.ALIGN_CENTER)
    ctrl.Bind(wx.EVT_BUTTON, handler)
    if updateHandler:
        ctrl.Bind(wx.EVT_UPDATE_UI, updateHandler)
    return ctrl


def createCtrlPageNo(parent, pSizer, handler):
    ctrl = IntCtrl(parent, value=1, size=(70, -1), min=1, max=1, limited=True,
                   allow_none=True,
                    style=wx.TE_CENTER | wx.TE_PROCESS_ENTER | wx.BORDER_THEME)
    ctrl.SetToolTipString("Enter page number")
    pSizer.Add(ctrl, 0, border=1, flag=wx.ALL | wx.ALIGN_CENTER)
    ctrl.Bind(wx.EVT_TEXT_ENTER, handler)
    return ctrl


class PageSelectorCtrl(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(PageSelectorCtrl, self).__init__(*args, **kwargs)
        self.view = ymvc.View(self)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        createBtn(self, sizer, "9", "Show first page", self.onBtnFirst)
        createBtn(self, sizer, "7", "Show previous page", self.onBtnPrevious,
                                                    self.onBtnPreviousUpdate)
        self.ctrlPageNo = createCtrlPageNo(self, sizer, self.onPageNo)
        createBtn(self, sizer, "8", "Show next page", self.onBtnNext,
                                                        self.onBtnNextUpdate)
        createBtn(self, sizer, ":", "Show last page", self.onBtnLast)

        self.ctrlDetails = wx.StaticText(self, label="Page")

        sizer.Add(self.ctrlDetails, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 4)
        self.SetSizer(sizer)
        self.Fit()

    def onBtnFirst(self, event):
        self.setPageNo(1)
        self.notifyPageNo()
        event.Skip()

    def onBtnPrevious(self, event):
        if self.getPageNo() > 1:
            self.setPageNo(self.getPageNo() - 1)
            self.notifyPageNo()
        event.Skip()

    def onBtnPreviousUpdate(self, event):
        if not self.IsEnabled():
            event.Skip()
        event.Enable(False if self.getPageNo() == 1 else True)

    def onPageNo(self, event):
        self.setPageNo(int(event.String))
        self.notifyPageNo()
#        event.Skip()

    def onBtnNext(self, event):
        if self.getPageNo() < self.getlastPageNo():
            self.setPageNo(self.getPageNo() + 1)
            self.view.notifyKw(pageNo=self.getPageNo())
        event.Skip()

    def onBtnNextUpdate(self, event):
        if not self.IsEnabled():
            event.Skip()
        condition = self.getPageNo() == self.getlastPageNo()
        event.Enable(False if condition else True)

    def onBtnLast(self, event):
        self.setPageNo(self.getlastPageNo())
        self.notifyPageNo()
        event.Skip()

    def notifyPageNo(self):
        self.view.notifyKw(pageNo=self.getPageNo())

    def getPageNo(self):
        return self.ctrlPageNo.GetValue() or 1

    def getlastPageNo(self):
        return self.ctrlPageNo.GetMax()

    def setPageNo(self, value):
        self.ctrlPageNo.ChangeValue(value)

    def setLastPageNo(self, value):
        self.ctrlPageNo.SetMax(value)

    def setPageDetails(self, pageDetails):
        self.ctrlDetails.SetLabel(pageDetails)
        self.GetParent().Layout()


class PageSelectorMediator(ymvc.Mediator):
    def __init__(self, uniqueName):
        super(PageSelectorMediator, self).__init__(uniqueName)

    def onCreateBinds(self):
        self.pageModel = self.modelStore[self.uniqueName + 'pageModel']

        self.view.bind(self.onViewPageNo)

        self.pageModel.bind(self.onpageModelLastPageNo)
        self.pageModel.bind(self.onpageModelPageNo)
        self.pageModel.bind(self.onpageModelPageDetails)

    @ymvc.onKwSignal
    def onViewPageNo(self, pageNo):
        self.notifyMsgKw(self.uniqueName + REQUEST_PAGE_NO, pageNo=pageNo)
        self.pageModel.notifyKw(requestPageNo=pageNo)

    @wxCallafter
    @ymvc.onAttrSignal
    def onpageModelPageNo(self, pageNo):
        self.gui.setPageNo(pageNo)

    @wxCallafter
    @ymvc.onAttrSignal
    def onpageModelLastPageNo(self, lastPageNo):
        self.gui.setLastPageNo(lastPageNo)

    @wxCallafter
    @ymvc.onAttrSignal
    def onpageModelPageDetails(self, pageDetails):
        self.gui.setPageDetails(pageDetails)


class RecordsTestModel(ymvc.Model):
    def __init__(self, uniqueName):
        super(RecordsTestModel, self).__init__()
        self.uniqueName = uniqueName
        self.pageModel = self.modelStore[uniqueName + 'pageModel']
        self.numRecords = 2500
        self.onPageSelectorModelRequestPageNo(1)

        self.pageModel.bind(self.onPageSelectorModelRequestPageNo)
        self.pageModel.bind(self.onPageModelLimitOffset)

    @ymvc.onKwSignal
    def onPageSelectorModelRequestPageNo(self, requestPageNo):
        self.pageModel.numRecords = self.numRecords
        self.pageModel.pageNo = requestPageNo

    @ymvc.onKwSignal
    def onPageModelLimitOffset(self, limit, offset):
        print 'Requested database records limit: {}, offset: {}'.format(limit,
                                                                        offset)


class TestAppMediator(ymvc.Mediator):
    def __init__(self, uniqueName):
        super(TestAppMediator, self).__init__(uniqueName)
        self.pageModel = PageModel()
        self.modelStore[uniqueName + 'pageModel'] = self.pageModel
        self.modelStore['recordsTestModel'] = RecordsTestModel(self.uniqueName)

        self.bind(self.onRequestPageNo)

    @ymvc.onMsgKwSignal('TestingPageSelector' + REQUEST_PAGE_NO)
    def onRequestPageNo(self, pageNo):
        self.pageModel.numRecords = 2500
        self.pageModel.pageNo = pageNo


if __name__ == '__main__':
    from y_mvc.models.page_model import PageModel
    uniqueName = 'TestingPageSelector'
    testAppMediator = TestAppMediator(uniqueName)
    wxapp = wx.App(None)
    frame = wx.Frame(None, title="Testing PageDetails Panel")
    pageSelectorCtrl = PageSelectorCtrl(frame)
    mediator = PageSelectorMediator(uniqueName)
    pageSelectorCtrl.view.setMediator(mediator)
    fSizer = wx.BoxSizer(wx.VERTICAL)
    fSizer.Add(pageSelectorCtrl)
    frame.SetSizer(fSizer)
    frame.Layout()
    frame.Show()
    wxapp.MainLoop()

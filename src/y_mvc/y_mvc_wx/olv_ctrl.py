'''
Created on 1 Apr 2013

@author: Dave Wilson
'''


import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from ObjectListView import ObjectListView, ColumnDefn
from wxAnyThread import anythread
from y_mvc import ymvc
from y_mvc.models import data_model
from y_mvc.models.data_model import ItemsModel
from collections import namedtuple

DOUBLE_CLICKED = 'DoubleClicked'
SORT_CHANGED = 'SortChanged'


class OlvCtrl(ObjectListView, ListCtrlAutoWidthMixin):
    '''An ObjectListView that request you sort you own data.
    and has methods for an id column'''

    def __init__(self, *args, **kwargs):
        self.controller = None
        kwargs['sortable'] = False
        if not kwargs.get('sytle'):
            kwargs['style'] = (wx.LC_REPORT | wx.LC_SINGLE_SEL |
                               wx.LC_HRULES | wx.LC_VRULES)
        super(OlvCtrl, self).__init__(*args, **kwargs)
        ListCtrlAutoWidthMixin.__init__(self)
        self.selectedId = None
        self.previousSortIndex = -1
        self.sortAscending = True
        self._setInitState()
        self._createBinds()
        self.view = ymvc.View(self)

    def _setInitState(self):
        self._setupEmptyListMsg()
        self._setupImageList()
        self.useAlternateBackColors = False

    def _setupEmptyListMsg(self):
        self.stEmptyListMsg.SetForegroundColour(wx.LIGHT_GREY)
        colour = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNFACE)
        self.stEmptyListMsg.SetBackgroundColour(colour)
        self.SetEmptyListMsg("No Data")

    def _setupImageList(self):
        if not self.smallImageList:
            self.SetImageLists()
        hasName = self.smallImageList.HasName(
                            super(OlvCtrl, self).NAME_DOWN_IMAGE)
        sizeCondition = self.smallImageList.GetSize(0) == (16, 16)
        if not hasName and sizeCondition:
            self.RegisterSortIndicators()

    def _HandleSize(self, evt):
        """
        The ListView is being resized
        """
        self._PossibleFinishCellEdit()
        self._ResizeSpaceFillingColumns()
        size = self.GetClientSize()
        dimensions = (0, 21, size.GetWidth(), size.GetHeight())
        self.stEmptyListMsg.SetDimensions(*dimensions)
        evt.Skip()

    def _getColumnIndex(self, columnName):
        columns = [column.valueGetter for column in self.columns]

        try:
            return columns.index(columnName)
        except ValueError:
            return -1

    def _getColumnName(self, columnIndex):
        return self.columns[columnIndex].valueGetter

    def _createBinds(self):
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListItemSelection)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListItemDeselection)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.onListColClick)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onListItemActivated)

    def onListItemSelection(self, event):
        selected_item = self.GetSelectedObject()
        self.selectedId = selected_item.id
        self.view.notifyKw(selectedId=self.selectedId)
        event.Skip()

    def onListItemDeselection(self, event):
        wx.CallAfter(self.recheck_list_item_deselection)
        event.Skip()

    def recheck_list_item_deselection(self):
        if not self.GetSelectedObject():
            self.view.notifyKw(selectedId=None)
            self.selectedId = None

    def onListColClick(self, event):
        columnName = self._getColumnName(event.GetColumn())
        if columnName:
            ascending = not self.sortAscending
            if self._getColumnIndex(columnName) != self.previousSortIndex:
                ascending = True
            self.setSortIndicator(columnName, ascending)
            self.view.notifyKw(sortColumnName=columnName,
                               sortAscending=ascending)

        event.Skip()

    def onListItemActivated(self, event):
        selected_item = self.GetSelectedObject()
        self.selectedId = selected_item.id
        self.view.notifyKw(doubleClickedId=self.selectedId)
        event.Skip()

    def SetColumns(self, column_defns, repopulate=True):
        super(OlvCtrl, self).SetColumns(column_defns, repopulate)
        self.AutoSizeColumns()

    def getSelectedObjectId(self):
        selected_object = self.GetSelectedObject()
        return None if not selected_object else selected_object.id

    def getObjectById(self, obj_id):
        obj = [obj for obj in self.modelObjects if obj.id == obj_id]
        return None if not obj else obj[0]

    def getObjectIndex(self, obj):
        return self._MapModelIndexToListIndex(self.GetIndexOf(obj))

    def setPreviousSortIndicator(self):
        index = self.previousSortIndex
        if index < 0:
            return
        headerImage = self.columns[index].headerImage
        if isinstance(headerImage, basestring):
            headerImage = self.smallImageList.GetImageIndex(headerImage)
        self.SetColumnImage(index, headerImage)

    @anythread
    def SetObjects(self, modelObjects, preserveSelection=False):
        parent = self.GetParent()
        parent.Freeze()
        super(OlvCtrl, self).SetObjects(modelObjects,
                                                      preserveSelection)
        self.SetEmptyListMsg("No Data")
        wx.CallAfter(self.AutoSizeColumns)
        wx.CallAfter(self.SendSizeEvent)
        wx.CallAfter(parent.Thaw)

    @anythread
    def setSortIndicator(self, columnName, ascending):
        index = self._getColumnIndex(columnName)
        if index < 0:
            return
        parent = self.GetParent()
        parent.Freeze()
        self.setPreviousSortIndicator()

        imageName = self.NAME_UP_IMAGE if ascending else self.NAME_DOWN_IMAGE
        imageIndex = self.smallImageList.GetImageIndex(imageName)

        if imageIndex != -1:
            self.SetColumnImage(index, imageIndex)

        self.previousSortIndex = index
        self.sortAscending = ascending
        parent.Thaw()

    @anythread
    def selectId(self, selectId, ensureVisible=True):
        parent = self.GetParent()
        parent.Freeze()
        self.Unbind(wx.EVT_LIST_ITEM_SELECTED)
        self.Unbind(wx.EVT_LIST_ITEM_DESELECTED)
        if not selectId:
            self.DeselectAll()
        else:
            model_object = self.getObjectById(selectId)
            if model_object:
                realIndex = self.getObjectIndex(model_object)
                self.Select(realIndex)
                if ensureVisible:
                    self.EnsureVisible(realIndex)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListItemSelection)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListItemDeselection)
        parent.Thaw()

    @anythread
    def SetEmptyListMsg(self, msg):
        super(OlvCtrl, self).SetEmptyListMsg(msg)

    @anythread
    def modeAccessingData(self):
        parent = self.GetParent()
        parent.Freeze()
        self.DeleteAllItems()
        self.SetEmptyListMsg("Accessing Data")
        parent.Thaw()
#        self.Enable(False)

#    @anythread
#    def modeDataRecieved(self):
#        self.SetEmptyListMsg("No Data")
#        if self.GetParent().IsEnabled():
#            self.Enable(True)
#
#    @anythread
#    def modeDataError(self, errorText):
#        self.DeleteAllItems()
#        self.SetEmptyListMsg(errorText)
#        self.Enable(False)


class OlvCtrlMediator(ymvc.Mediator):
    def __init__(self, uniqueName):
        super(OlvCtrlMediator, self).__init__(uniqueName)

    def onCreateBinds(self):
        self.itemsModel = self.modelStore[self.uniqueName + 'itemsModel']

        self.view.bind(self.onViewKwSelectedId)
        self.view.bind(self.onViewKwDoubleClickId)
        self.view.bind(self.onViewKwSortColumnAscending)

        self.itemsModel.bind(self.onItemsModelItems)
        self.itemsModel.bind(self.onItemsModelSelectedId)
        self.itemsModel.bind(self.onItemsModelSortDetails)
        self.itemsModel.bind(self.onStatusModelError)
        self.itemsModel.bind(self.onStatusModelStatus)

    @ymvc.onKwSignal
    def onViewKwSelectedId(self, selectedId):
        self.itemsModel.selectedId = selectedId

    @ymvc.onKwSignal
    def onViewKwDoubleClickId(self, doubleClickedId):
        self.notifyMsgKw(self.uniqueName + DOUBLE_CLICKED,
                         selectedId=doubleClickedId)

    @ymvc.onKwSignal
    def onViewKwSortColumnAscending(self, sortColumnName, sortAscending):
        SortDetails = ((sortColumnName, sortAscending),)
        self.notifyMsgKw(self.uniqueName + SORT_CHANGED,
                         SortDetails=SortDetails)

    @ymvc.onAttrSignal
    def onItemsModelItems(self, items):
        if self.gui:
            self.gui.SetObjects(items)

    @ymvc.onAttrSignal
    def onItemsModelSelectedId(self, selectedId):
        if self.gui:
            self.gui.selectId(selectedId)

    @ymvc.onAttrSignal
    def onItemsModelSortDetails(self, sortDetails):
        if self.gui:
            sortName, ascending = sortDetails[0]
            self.gui.setSortIndicator(sortName, ascending)

    @ymvc.onAttrSignal
    def onStatusModelError(self, error):
        if self.gui:
            if error:
                self.gui.SetEmptyListMsg(error)

    @ymvc.onAttrSignal
    def onStatusModelStatus(self, status):
        if self.gui:
            if status == data_model.STATUS_ACCESSING_DATA:
                self.gui.modeAccessingData()


class TestAppMediator(ymvc.Mediator):
    def __init__(self, uniqueName):
        super(TestAppMediator, self).__init__(uniqueName)

        DataItem = namedtuple('DataItem', 'id customerName partNumber')
        items = [DataItem(index, 'name{}'.format(index),
                          'part{}'.format(index)) for index in xrange(1, 1000)]

        self.itemsModel = ItemsModel(items=items)
        self.modelStore[self.uniqueName + 'itemsModel'] = self.itemsModel


class TestFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(TestFrame, self).__init__(*args, **kwargs)
        self.olvCtrl = OlvCtrl(self)

        columns = [ColumnDefn(title="",
                      valueGetter="", maximumWidth=0),
               ColumnDefn(title="Customer name",
                              valueGetter="customerName", minimumWidth=150),
               ColumnDefn(title="Part Number", valueGetter="partNumber",
                              minimumWidth=150)]
        self.olvCtrl.SetColumns(columns)
        self.Show()


if __name__ == '__main__':
    app = wx.App(False)
    testFrame = TestFrame(None)
    uniqueName = 'TestOlv'
    testAppMediator = TestAppMediator(uniqueName)
    mediator = OlvCtrlMediator(uniqueName)
    testFrame.olvCtrl.view.setMediator(mediator)
    app.MainLoop()

'''
Created on 28 Mar 2013

@author: Dave Wilson
'''

import wx
from wxAnyThread import anythread
import ymvc


class TextCtrl(wx.TextCtrl):

    def __init__(self, *args, **kwargs):
        super(TextCtrl, self).__init__(*args, **kwargs)
        self._isValid = False

    def ChangeValue(self, value):
        '''Change the value in the text entry field. Does not generate a
        text change event.'''
        insertionPoint = self.GetInsertionPoint()
        isEmpty = self.IsEmpty()
        super(TextCtrl, self).ChangeValue(value)

        if self.FindFocus() == self:
            if isEmpty:
                self.SetInsertionPointEnd()
            else:
                self.SetInsertionPoint(insertionPoint)

    @property
    def isValid(self):
        return self._isValid

    @isValid.setter
    def isValid(self, isValid=False):
        self._isValid = isValid
        if isValid:
            self.SetBackgroundColour((144, 238, 144))
        else:
            self.SetBackgroundColour(wx.NullColour)
        self.GetParent().Refresh()


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)
        self.view = ymvc.View(self)

        panel = wx.Panel(self)
        self.label1 = wx.StaticText(panel)
        self.text1 = TextCtrl(panel)
        self.text1.Bind(wx.EVT_TEXT,
                        lambda event: self.view.notifyKw(title=event.String))

        pSizer = wx.BoxSizer(wx.VERTICAL)
        pSizer.Add(self.label1, 0, wx.ALL, 5)
        pSizer.Add(self.text1, 0, wx.ALL, 5)

        fSizer = wx.BoxSizer(wx.VERTICAL)
        fSizer.Add(panel, 1, wx.EXPAND)

        panel.SetSizer(pSizer)
        self.SetSizer(fSizer)
        self.Layout()

    @anythread
    def setTitle(self, title):
        self.label1.SetLabel(title)
        self.SetTitle(title)
        self.text1.ChangeValue(title)

    @anythread
    def setTitleIsValid(self, titleIsValid):
        self.text1.isValid = titleIsValid


class MainFrameController(ymvc.Controller):
    def __init__(self, view, model1):
        super(MainFrameController, self).__init__(view)
        self.model1 = model1
        self.view.bind(self.onViewTitle)
        self.model1.bind(self.onModel1Title)
        self.model1.bind(self.onModel1TitleIsValid)

    @ymvc.onNotifyKw('title')
    def onViewTitle(self, title):
        self.model1.title = title

    @ymvc.onAttr('title')
    def onModel1Title(self, title):
        self.gui.setTitle(title)

    @ymvc.onAttr('titleIsValid')
    def onModel1TitleIsValid(self, titleIsValid):
        self.gui.setTitleIsValid(titleIsValid)


class Model1(ymvc.Model):
    def __init__(self, title=''):
        super(Model1, self).__init__('title', 'titleIsValid')
        self.titleIsValid = False
        self.title = title

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value.title()
        self.titleIsValid = self._title != ''

if __name__ == '__main__':

    model1 = Model1('Model1 start value')

    wxapp = wx.App(False)
    mainFrame = MainFrame(None)
    MainFrameController(mainFrame.view, model1)
    mainFrame.Show()
    wxapp.MainLoop()

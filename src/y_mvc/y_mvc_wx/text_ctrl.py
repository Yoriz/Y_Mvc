'''
Created on 31 Mar 2013

@author: Dave Wilson
'''

import wx
from wx.lib.newevent import NewCommandEvent

TextChangeEvent, EVT_TEXT_CHANGE = NewCommandEvent()


class TextChangeCtrl(wx.TextCtrl):
    '''Rather then change the text itself, it fires a EVT_TEXT_CHANGE
    Set a function to acceptChar that returns True/False
    validColour and notValidColour can be set'''

    def __init__(self, *args, **kwargs):
        super(TextChangeCtrl, self).__init__(*args, **kwargs)
        self.insertionPoint = 0
        self._isValid = False
        self.acceptChar = lambda character: True
        self.validColour = (144, 238, 144)
        self.notValidColour = wx.NullColour

        self.Bind(wx.EVT_CHAR, self.onChar)
        self.Bind(wx.EVT_TEXT_PASTE, self.onPaste)

    def onPaste(self, event):
        '''When text is pasted in, each char will be checkIsValid
        if all char are ok will send EVT_TEXT_CHANGE otherwise it will
        pop up a dialog stating invalid char pasted'''
        data = wx.TextDataObject()
        clipboard = wx.Clipboard()
        dataOk = clipboard.GetData(data)
        clipboard.Close()
        if not dataOk:
            return
        pastedText = data.GetText()
        acceptable = all(map(self.acceptChar, pastedText))
        if not acceptable:
            with wx.MessageDialog(self, 'Invalid character pasted', 'Error!',
                                  wx.ICON_ERROR | wx.OK | wx.CENTER) as dialog:
                dialog.ShowModal()
                return

        start, end = self.GetSelection()
        text = self.GetValue()
        if start != end:
            text = ''.join((text[:start], text[end:]))

        insertionPoint = end + len(pastedText)

        newText = ''.join((text[:start], pastedText, text[start:]))
        self.insertionPoint = insertionPoint
        self.postTextChangeEvent(newText, self.insertionPoint, True)

    def onChar(self, event):
        '''Sends an EVT_TEXT_CHANGE if the char passes acceptChar'''
        key = event.GetKeyCode()
        insertionPoint = self.GetInsertionPoint()
        start, end = self.GetSelection()
        text = self.GetValue()
        if 31 < key < 123:
            char = chr(key)
            if self.acceptChar(char):
                newText = ''.join((text[:start], char, text[end:]))
                self.insertionPoint = insertionPoint + 1
                self.postTextChangeEvent(newText, self.insertionPoint)

        elif key in (wx.WXK_BACK, wx.WXK_DELETE) and start != end:
            newText = ''.join((text[:start], text[end:]))
            self.insertionPoint = insertionPoint
            self.postTextChangeEvent(newText, self.insertionPoint)

        elif key == wx.WXK_BACK:
            newText = ''.join((text[:start - 1], text[start:]))
            self.insertionPoint = insertionPoint - 1
            self.postTextChangeEvent(newText, self.insertionPoint)

        elif key == wx.WXK_DELETE:
            newText = ''.join((text[:start], text[start + 1:]))
            self.insertionPoint = insertionPoint
            self.postTextChangeEvent(newText, self.insertionPoint)

        else:
            event.Skip()

    def postTextChangeEvent(self, newText, insertionPoint, pasted=False):
        evt = TextChangeEvent(self.Id, insertionPoint=insertionPoint,
                              pasted=pasted)
        evt.SetString(newText)
        wx.PostEvent(self, evt)

#     def ChangeValue(self, value):
#         '''Change the value in the text entry field. Does not generate a
#         text change event. Maintains insert point'''
# 
#         isEmpty = self.IsEmpty()
#         super(TextChangeCtrl, self).ChangeValue(value)
# 
#         if self.FindFocus() == self:
#             if isEmpty:
#                 self.SetInsertionPointEnd()
#             else:
#                 self.SetInsertionPoint(self.insertionPoint)

    @property
    def isValid(self):
        return self._isValid

    @isValid.setter
    def isValid(self, isValid=False):
        '''Colours the background depending on its validity'''
        if self._isValid == isValid:
            return
        self._isValid = isValid
        if isValid:
            colour = self.validColour
        else:
            colour = self.notValidColour

        self.SetBackgroundColour(colour)
        self.GetParent().Refresh()

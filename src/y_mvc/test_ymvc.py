'''
Created on 24 Mar 2013

@author: Dave Wilson
'''

import ymvc
import unittest


class TestBase(unittest.TestCase):

    def setUp(self):
        self.ymvcBase = ymvc.YmvcBase()
        self.notifyCalled = False
        self.attr1 = None
        self.attr2 = None
        self.attr3 = None

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    @ymvc.onKwSignal
    def onTestOnSignalKw(self, attr1):
        self.attr1 = attr1

    @ymvc.onKwSignal
    def onTestOnSignalManyKw(self, attr2, attr1, attr3):
        self.attr1 = attr1
        self.attr2 = attr2
        self.attr3 = attr3

    @ymvc.onMsgSignal('Empty')
    def onTestOnSignalNotifyMsg(self):
        self.notifyCalled = True

    @ymvc.onMsgKwSignal('CallMe')
    def onTestOnSignalNotifyMsgKw(self, attr1, attr2):
        self.attr1 = attr1
        self.attr2 = attr2
        self.attr3 = 'CallMe'

    def testNotifyKw(self):
        self.ymvcBase.bind(self.onTestOnSignalKw)
        self.ymvcBase.notifyKw(attr1='TestValue')
        self.ymvcBase.waitInQueue()
        self.assertEqual('TestValue', self.attr1)

    def testNotifyManyKw(self):
        self.ymvcBase.bind(self.onTestOnSignalManyKw)
        self.ymvcBase.notifyKw(attr1='attr1', attr2='attr2', attr3='attr3')
        self.ymvcBase.waitInQueue()
        self.assertEqual('attr1', self.attr1)
        self.assertEqual('attr2', self.attr2)
        self.assertEqual('attr3', self.attr3)

    def testNotify(self):
        self.ymvcBase.bind(self.onTestOnSignalNotifyMsg)
        self.ymvcBase.notifyMsg('Empty')
        self.ymvcBase.waitInQueue()
        self.assertEqual(True, self.notifyCalled)

    def testNotifyMsgKw(self):
        self.ymvcBase.bind(self.onTestOnSignalNotifyMsgKw)
        self.ymvcBase.notifyMsgKw('CallMe', attr1='attr1', attr2='attr2')
        self.ymvcBase.waitInQueue()
        self.assertEqual('attr1', self.attr1)
        self.assertEqual('attr2', self.attr2)
        self.assertEqual('CallMe', self.attr3)


class TestModel1(ymvc.Model):

    def __init__(self, attr1='StartValue', attr2='StartValue'):
        super(TestModel1, self).__init__()
        self.addObsAttrs('attr1', 'attr2')
        self.attr1 = attr1
        self.attr2 = attr2
        self.attr3 = 'Attr3'


class TestModel(unittest.TestCase):

    def setUp(self):
        self.model = TestModel1()
        self.attr1 = None
        self.attr2 = None

    @ymvc.onAttrSignal
    def attr1Callback(self, attr1):
        self.attr1 = attr1

    @ymvc.onAttrSignal
    def attr2Callback(self, attr2):
        self.attr2 = attr2

    def testSetAttr(self):
        self.model.attr1 = 'Testing'
        self.model.waitInQueue()
        self.assertEqual('Testing', self.model.attr1)

    def testSlotGetAttr(self):
        self.model.slotGetAttr(self.attr1Callback)
        self.model.waitInQueue()
        self.assertEqual(self.model.attr1, self.attr1)

    def testSlotAttrCallbackOnBind(self):
        self.model.bind(self.attr1Callback)
        self.model.waitInQueue()
        self.assertEqual('StartValue', self.attr1)

    def testSetAttrCallback(self):
        self.model.bind(self.attr1Callback)
        self.model.attr1 = 'Testing'
        self.model.waitInQueue()
        self.assertEqual('Testing', self.attr1)

    def testNonBindAttr(self):
        self.assertEqual('Attr3', self.model.attr3)
        self.model.attr3 = 'Altered'
        self.assertEqual('Altered', self.model.attr3)

    def testHasModelStore(self):
        self.assertIs(ymvc.modelStore, self.model.modelStore)


class TestViewAndMediator(unittest.TestCase):

    def setUp(self):
        self.viewDestroyed = False
        self.createBinds = False

        class Gui(object):
            def __init__(self):
                self.view = ymvc.View(self)

        self.gui = Gui()

    def onViewDestroyed(self):
        self.viewDestroyed = True

    def onCreateBinds(self):
        self.createBinds = True

    def testViewSetMediator(self):
        mediator = ymvc.Mediator('Mediator1')
        mediator.onViewDestroyed = self.onViewDestroyed
        mediator.onCreateBinds = self.onCreateBinds
        self.gui.view.setMediator(mediator)
        self.assertIs(self.gui, mediator.gui)
        self.assertIs(ymvc.modelStore, mediator.modelStore)
        self.assertIs(self.gui.view.__class__, mediator.view.__class__)
        del self.gui.view
        self.assertEqual(True, self.viewDestroyed)
        self.assertEqual(True, self.createBinds)


if __name__ == '__main__':
    unittest.main()

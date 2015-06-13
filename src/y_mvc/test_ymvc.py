'''
Created on 24 Mar 2013

@author: Dave Wilson
'''

import ymvc
import unittest


class TestBase(unittest.TestCase):

    def setUp(self):
        self.ymvcBase = ymvc.YmvcBase(ymvc._proxy_queued_thread_out)
        self.notifyCalled = False
        self.attr1 = None
        self.attr2 = None
        self.attr3 = None

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    @ymvc.on_kw_signal
    def onTestOnSignalKw(self, attr1):
        self.attr1 = attr1

    @ymvc.on_kw_signal
    def onTestOnSignalManyKw(self, attr2, attr1, attr3):
        self.attr1 = attr1
        self.attr2 = attr2
        self.attr3 = attr3

    @ymvc.on_msg_signal('Empty')
    def onTestOnSignalNotifyMsg(self):
        self.notifyCalled = True

    @ymvc.on_msg_kw_signal('CallMe')
    def onTestOnSignalNotifyMsgKw(self, attr1, attr2):
        self.attr1 = attr1
        self.attr2 = attr2
        self.attr3 = 'CallMe'

    def testNotifyKw(self):
        self.ymvcBase.bind(self.onTestOnSignalKw)
        self.ymvcBase.notify_kw(attr1='TestValue')
        self.ymvcBase.wait_in_queue()
        self.assertEqual('TestValue', self.attr1)

    def testNotifyManyKw(self):
        self.ymvcBase.bind(self.onTestOnSignalManyKw)
        self.ymvcBase.notify_kw(attr1='attr1', attr2='attr2', attr3='attr3')
        self.ymvcBase.wait_in_queue()
        self.assertEqual('attr1', self.attr1)
        self.assertEqual('attr2', self.attr2)
        self.assertEqual('attr3', self.attr3)

    def testNotify(self):
        self.ymvcBase.bind(self.onTestOnSignalNotifyMsg)
        self.ymvcBase.notify_msg('Empty')
        self.ymvcBase.wait_in_queue()
        self.assertEqual(True, self.notifyCalled)

    def testNotifyMsgKw(self):
        self.ymvcBase.bind(self.onTestOnSignalNotifyMsgKw)
        self.ymvcBase.notify_msg_kw('CallMe', attr1='attr1', attr2='attr2')
        self.ymvcBase.wait_in_queue()
        self.assertEqual('attr1', self.attr1)
        self.assertEqual('attr2', self.attr2)
        self.assertEqual('CallMe', self.attr3)


class TesProxy1(ymvc.Proxy):

    def __init__(self, attr1='StartValue', attr2='StartValue'):
        super(TesProxy1, self).__init__()
        self.add_obs_attrs('attr1', 'attr2')
        self.attr1 = attr1
        self.attr2 = attr2
        self.attr3 = 'Attr3'


class TestProxy(unittest.TestCase):

    def setUp(self):
        self.proxy = TesProxy1()
        self.attr1 = None
        self.attr2 = None

    @ymvc.on_attr_signal
    def attr1Callback(self, attr1):
        self.attr1 = attr1

    @ymvc.on_attr_signal
    def attr2Callback(self, attr2):
        self.attr2 = attr2

    def testSetAttr(self):
        self.proxy.attr1 = 'Testing'
        self.proxy.wait_in_queue()
        self.assertEqual('Testing', self.proxy.attr1)

    def testSlotGetAttr(self):
        self.proxy.slot_get_attr(self.attr1Callback)
        self.proxy.wait_in_queue()
        self.assertEqual(self.proxy.attr1, self.attr1)

    def testSlotAttrCallbackOnBind(self):
        self.proxy.bind(self.attr1Callback)
        self.proxy.wait_in_queue()
        self.assertEqual('StartValue', self.attr1)

    def testSetAttrCallback(self):
        self.proxy.bind(self.SetAttrCallback, False)
        self.proxy.attr1 = 'Testing'
#         self.proxy.wait_in_queue()
#         self.assertEqual('Testing', self.attr1)

    @ymvc.on_attr_signal
    def SetAttrCallback(self, attr1):
        self.assertEqual('Testing', attr1)

    def testNonBindAttr(self):
        self.assertEqual('Attr3', self.proxy.attr3)
        self.proxy.attr3 = 'Altered'
        self.assertEqual('Altered', self.proxy.attr3)

    def testHasProxyStore(self):
        self.assertIs(ymvc.proxy_store, self.proxy.proxy_store)


class TestViewAndMediator(unittest.TestCase):

    def setUp(self):
        self.viewDestroyed = False
        self.createBinds = False

        class Gui(object):
            def __init__(self):
                self.view = ymvc.View(self)

        self.gui = Gui()

    def on_view_destroyed(self):
        self.viewDestroyed = True

    def on_create_binds(self):
        self.createBinds = True

    def testViewSetMediator(self):
        mediator = ymvc.Mediator('Mediator1')
        mediator.on_view_destroyed = self.on_view_destroyed
        mediator.on_create_binds = self.on_create_binds
        self.gui.view.set_mediator(mediator)
        self.assertIs(self.gui, mediator.gui)
        self.assertIs(ymvc.proxy_store, mediator.proxy_store)
        self.assertIs(self.gui.view.__class__, mediator.view.__class__)
        del self.gui.view
        self.assertEqual(True, self.viewDestroyed)
        self.assertEqual(True, self.createBinds)


if __name__ == '__main__':
    unittest.main()

'''
Created on 24 Mar 2013

@author: Dave Wilson
'''

from y_signal.ysignal import Ysignal
from functools import wraps

_SIGNAL = 'uniqueSignalKeyName'


class SignalNotify(tuple):
    '''Creates a Notification signal'''
    def __new__(self, name):
        return tuple.__new__(self, name)


class SignalNotifyKw(tuple):
    '''Creates a Notification signal with given keywords'''
    def __new__(self, *keywords):
        if not keywords:
            raise AttributeError('At least one keyword required')
        items = list(sorted(keywords))
        items.insert(0, 'SignalNotifyKeywords')
        return tuple.__new__(self, items)


class SignalAttr(tuple):
    '''Creates a attribute signal'''
    def __new__(self, attribute):
        return tuple.__new__(self, ('SignalAttr', attribute))


def onSignal(signal):
    '''Signal handler decorator, the decorated method will only be called if
    the signal argument passed in matches the decorated signal or if no
    signal argument is passed in at all'''
    def decorator(target):
        target._ySignal = signal

        @wraps(target)
        def wrapper(self, *args, **kwargs):
            signal_call = kwargs.pop(_SIGNAL, None)
            if not signal_call or (signal_call == signal):
                return target(self, *args, **kwargs)
        return wrapper
    return decorator


def onAttr(Attribute):
    '''Decorates a slot that binds to a model attribute'''
    return onSignal(SignalAttr(Attribute))


def onNotify(message):
    '''Decorates a slot that binds to a message notification'''
    return onSignal(SignalNotify(message))


def onNotifyKw(*keywords):
    '''Decorates a slot that binds to a keywords notification'''
    return onSignal(SignalNotifyKw(*keywords))


class YmvcBase(object):
    '''YmvcBase object for signal communication in ymvc'''
    def __init__(self, useThread=True):
        '''Initialise attributes'''
        self._ySignal = Ysignal(useThread)

    def bind(self, slot):
        '''bind a slot'''
        self._ySignal.bind(slot)

    def waitInQueue(self):
        '''wait in the signal queue till current signals are done'''
        self._ySignal.waitInQueue()

    def waitTillQueueEmpty(self):
        '''Wait till the queue is empty (not reliable!)'''
        self._ySignal.waitTillQueueEmpty()

    def notify(self, message):
        '''Sends a message notification to all slots interested
        Decorate slots with onNotify(message)'''
        kwargs = {_SIGNAL: SignalNotify(message)}
        return self._ySignal.emit(**kwargs)

    def notifyKw(self, **kwargs):
        '''Sends a keywords notification to all slots interested
        Decorate slots with onNotifyKw(*keywords)'''
        kwargs[_SIGNAL] = SignalNotifyKw(*kwargs.keys())
        return self._ySignal.emit(**kwargs)


class View(YmvcBase):
    '''Communicates from your view to the controller'''
    def __init__(self, gui):
        super(View, self).__init__(False)
        self.gui = gui
        self.controller = None

    def setController(self, controller):
        '''Set the controller related to this view'''
        self.controller = controller


class Model(YmvcBase):
    '''Contains the data of your application'''

    _signaledAttr = []

    def __init__(self, *attributes):
        '''Set the attributes you want to observe changes
        Decorate slots with onAttr(attribute)'''
        super(Model, self).__init__()
        self._signaledAttr = attributes

    def bind(self, slot):
        '''binds a slot if it is an attribute slot emits its value'''
        super(Model, self).bind(slot)
        if isinstance(slot._ySignal, SignalAttr):
            self.slotGetAttr(slot)

    def __setattr__(self, name, value):
        '''Add a _setattrCall to the queue if listed in _signaledAttr'''
        if not hasattr(self, name):
            return YmvcBase.__setattr__(self, name, value)

        if name in self._signaledAttr:
            future = self._ySignal.threadPoolExe.submit(self._setattrCall,
                                                    name, value)
            future.add_done_callback(self._ySignal.slotCheck)
            return future
        else:
            return YmvcBase.__setattr__(self, name, value)

    def _setattrCall(self, name, value):
        '''Sets an attributes value and then sends a signal of its new value'''
        YmvcBase.__setattr__(self, name, value)
        kwargs = {_SIGNAL: SignalAttr(name), name: getattr(self, name)}
        self._ySignal._emitCall(**kwargs)

    def slotGetAttr(self, slot):
        '''Emit the attribute for this slot only'''
        signal, name = slot._ySignal, slot._ySignal[1]
        kwargs = {_SIGNAL: signal, name: getattr(self, name)}
        return self._ySignal.emitSlot(slot, **kwargs)


class Controller(object):
    '''Communicates between a view and models'''
    def __init__(self, view):
        '''Sets up the view/controller pairing'''
        self.view = view
        self.gui = view.gui
        view.setController(self)

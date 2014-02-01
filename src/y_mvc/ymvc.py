'''
Created on 24 Mar 2013

@author: Dave Wilson
'''

import functools
import threading
import inspect
import weakref


from y_signal import ysignal


try:
    import wx
except ImportError:
    pass


_SIGNAL = 'uniqueSignalKeyName'
_SIGNAL_ATTR = 'Attr'
_SIGNAL_MSG = 'Msg'
_SIGNAL_KW = 'Kw'
_SIGNAL_MSGKW = 'MsgKw'

_mediator_queued_thread = ysignal.QueuedThread()
_proxy_queued_thread_in = ysignal.QueuedThread()
_proxy_queued_thread_out = ysignal.QueuedThread()

_global_signal = ysignal.Ysignal(_mediator_queued_thread)
proxy_store = {}
weak_proxy_store = weakref.WeakValueDictionary()


def message_signal(message):
    '''Returns a tuple representing a message signal'''
    return (_SIGNAL_MSG, message)


def keywords_signal():
    '''Returns a tuple representing a keyword signal'''
    return (_SIGNAL_KW,)


def messsage_with_keywords_signal(message):
    '''Returns a tuple representing a message keyword signal'''
    return (_SIGNAL_MSGKW, message)


def attribute_signal():
    '''Returns a tuple representing a attribute signal'''
    return (_SIGNAL_ATTR,)


def wx_callafter(target):
    '''Decorates a mediator method to make thread safe wx method calls'''
    @functools.wraps(target)
    def wrapper(*args, **kwargs):
        if not args[0].gui:
            return
        wx.CallAfter(target, *args, **kwargs)
    return wrapper


def run_async(func):
    '''Decorates a method to run in a separate thread'''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_hl = threading.Thread(target=func, args=args, kwargs=kwargs)
        func_hl.start()
        return func_hl
    return wrapper


def on_msg_signal(message):
    '''Decorates a method to only be called if the message matches the signal
    or if not called with a signal'''
    def decorator(target):
        target._signal = message_signal(message)

        @functools.wraps(target)
        def wrapper(self, *args, **kwargs):
            signal_call = kwargs.pop(_SIGNAL, None)
            if not signal_call or signal_call == target._signal:
                return target(self, *args, **kwargs)
        return wrapper
    return decorator


def on_msg_kw_signal(message):
    '''Decorates a method to only be called if the message and keywords match
    the signal or if not called with a signal'''
    def decorator(target):
        target._signal = messsage_with_keywords_signal(message)
        target_args = inspect.getargspec(target).args
        target_args.remove('self')
        target_args = set(target_args)

        @functools.wraps(target)
        def wrapper(self, *args, **kwargs):
            signal_call = kwargs.pop(_SIGNAL, None)
            if not signal_call or (signal_call == target._signal and
                                   set(kwargs.keys()) == target_args):
                return target(self, *args, **kwargs)
        return wrapper
    return decorator


def on_kw_signal(target):
    '''Decorates a method to only be called if the keywords match
    or if not called with a signal'''
    target._signal = keywords_signal()
    target_args = inspect.getargspec(target).args
    target_args.remove('self')
    target_args = set(target_args)

    @functools.wraps(target)
    def wrapper(self, *args, **kwargs):
        signal_call = kwargs.pop(_SIGNAL, None)
        if not signal_call or (signal_call == target._signal and
                               set(kwargs.keys()) == target_args):
            return target(self, *args, **kwargs)
    return wrapper


def on_attr_signal(target):
    '''Decorates a method to only be called if the keyword matches the
    attribute of the model that changed or if not called with a signal'''
    target._signal = attribute_signal()
    target_args = inspect.getargspec(target).args
    target_args.remove('self')
    target._attributes = target_args

    @functools.wraps(target)
    def wrapper(self, *args, **kwargs):
        signal_call = kwargs.pop(_SIGNAL, None)
        if not signal_call or (signal_call == target._signal and
                               kwargs.keys() == target._attributes):
            return target(self, *args, **kwargs)
    return wrapper


class YmvcBase(object):
    '''YmvcBase object for signal communication in ymvc'''
    def __init__(self, queued_thread=None):
        '''Initialise attributes'''
        self._ysignal = ysignal.Ysignal(queued_thread)

    def bind(self, slot):
        '''bind a slot'''
        self._ysignal.bind(slot)

    def unbind(self, slot):
        '''Remove slot from the list of listeners'''
        self._ysignal.unbind(slot)

    def unbind_all(self):
        '''Remove all slots'''
        self._ysignal.unbind_all()

    def wait_in_queue(self):
        '''wait in the signal queue till current signals are done'''
        self._ysignal.wait_in_queue()

    def notify_msg(self, message):
        '''Call methods decorated with on_msg_signal with matching message'''
        kwargs = {_SIGNAL: message_signal(message)}
        return self._ysignal.emit(**kwargs)

    def notify_kw(self, **kwargs):
        '''Call methods decorated with on_kw_signal with matching keywords'''
        kwargs[_SIGNAL] = keywords_signal()
        return self._ysignal.emit(**kwargs)

    def notify_msg_kw(self, message, **kwargs):
        '''Call methods decorated with on_msg_kw_signal with matching message
        and keywords'''
        kwargs[_SIGNAL] = messsage_with_keywords_signal(message)
        return self._ysignal.emit(**kwargs)


class View(YmvcBase):
    '''Communicates from your view to a Mediator'''
    def __init__(self, gui):
        super(View, self).__init__(None)
        self.gui = gui
        self.mediator = None

    def set_mediator(self, mediator):
        '''Set the Mediator to use with this view'''
        self.mediator = mediator
        mediator.gui = self.gui
        mediator.view = weakref.proxy(self, mediator._on_view_destroyed)
        mediator.on_create_binds()


class Proxy(YmvcBase):
    '''Contains the data of your application'''

    def __init__(self):
        '''Initialise'''
        super(Proxy, self).__init__(_proxy_queued_thread_out)
        self.call = YmvcBase(_proxy_queued_thread_in)
        self._signaled_attrs = set()
        self.proxy_store = proxy_store

    def add_obs_attrs(self, *attributes):
        self._ysignal.queued_thread.submit(self.add_obs_attrs_call, attributes)

    def add_obs_attrs_call(self, attributes):
        self._signaled_attrs.update(set(attributes))

    def remove_obs_attrs(self, *attributes):
        self._ysignal.queued_thread.submit(self.remove_obs_attrs_call,
            attributes)

    def remove_obs_attrs_call(self, attributes):
        self._signaled_attrs.difference_update(set(attributes))

    def bind(self, slot, immediate_callback=True):
        '''binds a slot if it is a signaledAttr emits its value'''
        super(Proxy, self).bind(slot)
        if immediate_callback and slot._signal == attribute_signal():
            self.slot_get_attr(slot)

    def __setattr__(self, name, value):
        '''Add a _setattr_call to the queue if listed in signaledAttrs'''
        if not hasattr(self, name):
            return YmvcBase.__setattr__(self, name, value)

        if name in self._signaled_attrs:
            if self._ysignal.queued_thread:
                self._ysignal.queued_thread.submit(self._setattr_call, name,
                                                  value)

            else:
                self._setattr_call(name, value)
        else:
            return YmvcBase.__setattr__(self, name, value)

    def _setattr_call(self, name, value):
        '''Sets an attributes value and then sends a signal of its new value'''
        YmvcBase.__setattr__(self, name, value)
        self._notify_attr_call(name)

    def _notify_attr_call(self, name):
        '''Call methods decorated with on_attr_signal with matching
        attribute'''
        kwargs = {_SIGNAL: attribute_signal(), name: getattr(self, name)}
        self._ysignal._emit_call(**kwargs)

    def notify_attr(self, name):
        '''Notify of an attribute change manually'''
        self._ysignal.queued_thread.submit(self._notify_attr_call, name)

    def slot_get_attr(self, slot):
        '''Emit the attribute for this slot only'''
        name = slot._attributes[0]
        kwargs = {_SIGNAL: attribute_signal(), name: getattr(self, name)}
        return self._ysignal.emit_slot(slot, **kwargs)


class Mediator(YmvcBase):
    '''Mediates between a view and models and can send/receive signals to/from
    other mediator's'''
    def __init__(self, unique_name=''):
        '''Initialise attributes'''
        self._ysignal = _global_signal
        self.unique_name = unique_name
        self.gui = None
        self.view = None
        self.proxy_store = proxy_store

    def on_create_binds(self):
        '''Overwrite this method with required binds, will be called when set
        to a view'''

    def _on_view_destroyed(self, *args, **kwargs):
        self.on_view_destroyed()

    def on_view_destroyed(self):
        '''Overwrite if an action is required when the view is destroyed'''

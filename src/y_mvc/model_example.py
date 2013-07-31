'''
Created on 22 Jun 2013

@author: Dave Wilson
'''


import functools
import threading
import time
import ymvc


def runAsync(func):
    '''Decorates a method to run in a separate thread'''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_hl = threading.Thread(target=func, args=args, kwargs=kwargs)
        func_hl.start()
        return func_hl
    return wrapper


class Threader(ymvc.Model):
    def __init__(self):
        super(Threader, self).__init__()
        self.add_obs_attrs('value', 'counting')
        self.bind(self.start)
        self.bind(self.stop)
        self.value = 0
        self.counting = False

    @runAsync
    @ymvc.on_msg_signal('start')
    def start(self):
        self.counting = True
        self.wait_in_queue()
        while self.counting:
            print 'Counting'
            time.sleep(1)
            self.value += 1
            self.wait_in_queue()

    @runAsync
    @ymvc.on_msg_signal('stop')
    def stop(self):
        self.counting = False


class CountMediator(ymvc.Mediator):
    def __init__(self):
        super(CountMediator, self).__init__()
        self.threader = Threader()
        self.threader.bind(self.onThreaderValue)
        self.threader.bind(self.onThreaderCounting)
        self.threader.notify_msg('start')
        while True:
            print 'running main loop'
            time.sleep(1)

    @ymvc.on_attr_signal
    def onThreaderValue(self, value):
        print 'Threader count: {}'.format(value)
        if value == 5:
            self.threader.notify_msg('stop')

    @ymvc.on_attr_signal
    def onThreaderCounting(self, counting):
        if counting:
            print 'Threader started counting'
        else:
            print 'Threader not counting'

if __name__ == '__main__':
    mediator = CountMediator()

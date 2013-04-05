'''
Created on 1 Apr 2013

@author: Dave Wilson
'''

from y_mvc import ymvc


class StatusModel(ymvc.Model):
    STATUS_OK = 'Ok'
    STATUS_ACCESSING_DATA = 'Accessing Data'
    STATUS_MODIFYING_DATA = 'Modifying Data'
    STATUS_SAVING_DATA = 'Saving Data'
    STATUS_CHECKING_DATA = 'Checking Data'
    STATUS_ERROR = 'Data Error'

    def __init__(self, status='Ok', error=''):
        super(StatusModel, self).__init__('status', 'error')
        self.status = status
        self.error = error


class ItemsModel(ymvc.Model):
    '''Keyword Notifications
        'changeSortDetails' - call another model to update items based on
                              sortDetails
        'doubleClickedId' - Inform of doubleClickId action
    '''
    def __init__(self, items=None, selectedId=None, sortDetails=None):
        super(ItemsModel, self).__init__('items', 'selectedId', 'sortDetails')
        self.items = items or []
        self.selectedId = selectedId
        self.sortDetails = sortDetails or (('', True),)
        self.statusModel = StatusModel()

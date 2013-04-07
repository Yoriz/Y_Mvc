'''
Created on 1 Apr 2013

@author: Dave Wilson
'''

from y_mvc import ymvc
from page_model import PageModel

STATUS_OK = 'Ok'
STATUS_ACCESSING_DATA = 'Accessing Data'
STATUS_MODIFYING_DATA = 'Modifying Data'
STATUS_SAVING_DATA = 'Saving Data'
STATUS_CHECKING_DATA = 'Checking Data'
STATUS_ERROR = 'Data Error'


class BaseDataModel(ymvc.Model):

    def __init__(self, status=STATUS_OK, error=''):
        super(BaseDataModel, self).__init__()
        self.addObsAttrs('status', 'error')
        self.status = status
        self.error = error


class ItemsModel(BaseDataModel):
    '''Keyword Notifications
        'doubleClickedId' - Inform of doubleClickId action
    '''
    def __init__(self, items=None, selectedId=None, sortDetails=None):
        super(ItemsModel, self).__init__()
        self.addObsAttrs('items', 'selectedId', 'sortDetails')
        self.items = items or []
        self.selectedId = selectedId
        self.sortDetails = sortDetails or (('', True),)

    def requestChangeSortDetails(self, sortDetails):
        '''call another model to update items based on sortDetails'''
        self.notifyKw(changeSortDetails=sortDetails)


class PagedItemsModel(ItemsModel, PageModel):
    def __init__(self):
        ItemsModel.__init__(self)
        PageModel.__init__(self)

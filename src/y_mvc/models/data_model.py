'''
Created on 1 Apr 2013

@author: Dave Wilson
'''

from y_mvc import ymvc
from util.pagination import pagination

STATUS_OK = 'Ok'
STATUS_ACCESSING_DATA = 'Accessing Data'
STATUS_MODIFYING_DATA = 'Modifying Data'
STATUS_SAVING_DATA = 'Saving Data'
STATUS_CHECKING_DATA = 'Checking Data'
STATUS_ERROR = 'Data Error'


class BaseDataModel(ymvc.Model):

    def __init__(self, status='', error=''):
        super(BaseDataModel, self).__init__()
        self.addObsAttrs('status', 'error')
        self.status = status
        self.error = error

    def __str__(self):
        string = 'status: {}'.format(self.status)
        string += ', error: {}'.format(self.error)
        return string

    def __repr__(self):
        return '{}<({})>'.format(self.__class__.__name__, str(self))


class ItemsModel(BaseDataModel):
    def __init__(self, items=None, selectedId=None, sortDetails=None):
        super(ItemsModel, self).__init__()
        self.addObsAttrs('items', 'selectedId', 'sortDetails')
        self.items = items or []
        self.selectedId = selectedId
        self.sortDetails = sortDetails or (('', True),)

    def __str__(self):
        string = super(ItemsModel, self).__str__()
        string += ', items: {}'.format(self.items)
        string += ', selectedId: {}'.format(self.selectedId)
        string += ', sortDetails: {}'.format(self.sortDetails)
        return string


class PagedItemsModel(ItemsModel):
    def __init__(self, items=None, selectedId=None, sortDetails=None):
        super(PagedItemsModel, self).__init__(items, selectedId, sortDetails)
        self.addObsAttrs('pagination')
        self.pagination = None
        self.setPagination(1)

    def setPagination(self, pageNo, numRecords=None, perPage=1000, orphans=0):
        if not numRecords:
            numRecords = len(self.items)
        self.pagination = pagination(pageNo, numRecords, perPage, orphans)

#     def __repr__(self):
#         string = 'PagedItemsModel<('
#         string += 'items: {}'.format(self.items)
#         string += ', selectedId: {}'.format(self.selectedId)
#         string += ', sortDetails: {}'.format(self.sortDetails)
#         string += ', pagination: {}'.format(self.pagination)
#         string += ', pagination: {}'.format(self.pagination)
#         return string

if __name__ == '__main__':
    pagedItemsModel = PagedItemsModel((1, 2, 3, 4, 5))
    print pagedItemsModel

'''
Created on 31 Mar 2013

@author: Dave Wilson
'''

from y_mvc import ymvc
from util.pagination import pagination
from collections import namedtuple

PageSlice = namedtuple('PageSlice', 'bottom top')
OffsetLimit = namedtuple('OffsetLimit', 'offset limit')


class PageModel(ymvc.Model):
    '''Keyword Notifications
            'offset', 'limit' - call for database records
            'bottom', 'top' - call for slice of data
    '''
    numRecords = 0
    perPage = 1000
    orphans = 0

    def __init__(self, pageNo=1, lastPageNo=1, pageDetails='Page'):
        super(PageModel, self).__init__()
        self.pageNo = pageNo
        self.lastPageNo = lastPageNo
        self.pageDetails = pageDetails
        self.pageSlice = PageSlice(0, 0)
        self.offsetLimit = OffsetLimit(0, 0)
        self.add_obs_attrs('pageNo', 'lastPageNo', 'pageDetails', 'pageSlice',
                         'offsetLimit')

    @property
    def pageNo(self):
        return self._pageNo

    @pageNo.setter
    def pageNo(self, value):
        page = pagination(value, self.numRecords, self.perPage, self.orphans)
        self.offsetLimit = OffsetLimit(page.offset, page.limit)
        self.pageSlice = PageSlice(page.bottom, page.top)
        self.lastPageNo = page.numPages
        self._pageNo = page.pageNo
        self.pageDetails = page.details

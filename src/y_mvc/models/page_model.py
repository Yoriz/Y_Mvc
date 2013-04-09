'''
Created on 31 Mar 2013

@author: Dave Wilson
'''

from y_mvc import ymvc
from util.pagination import pagination


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
        self.addObsAttrs('pageNo', 'lastPageNo', 'pageDetails')
        self.pageNo = pageNo
        self.lastPageNo = lastPageNo
        self.pageDetails = pageDetails

    @property
    def pageNo(self):
        return self._pageNo

    @pageNo.setter
    def pageNo(self, value):
        page = pagination(value, self.numRecords, self.perPage, self.orphans)
        self.notifyKw(offset=page.offset, limit=page.limit)
        self.notifyKw(bottom=page.bottom, top=page.top)
        self.lastPageNo = page.numPages
        self._pageNo = page.pageNo
        self.pageDetails = page.details

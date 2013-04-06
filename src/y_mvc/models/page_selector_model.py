'''
Created on 31 Mar 2013

@author: Dave Wilson
'''

from y_mvc import ymvc
from util.pagination import pagination


class PageSelectorModel(ymvc.Model):
    '''Keyword Notifications
            requestPageNo - call another model to set numRecords
            'offset', 'limit' - call for database records
            'bottom', 'top' - call for slice of data
    '''
    numRecords = 0
    perPage = 1000
    orphans = 0

    def __init__(self, pageNo=1, lastPageNo=1, pageDetails='Page'):
        super(PageSelectorModel, self).__init__()
        self.addObsAttrs('pageNo', 'lastPageNo', 'pageDetails')
        self.pageNo = pageNo
        self.lastPageNo = lastPageNo
        self.pageDetails = pageDetails

        self.bind(self.onRequestPageNo)

    @property
    def pageNo(self):
        return self._pageNo

    @pageNo.setter
    def pageNo(self, value):
        page = pagination(value, self.numRecords, self.perPage, self.orphans)
        self.lastPageNo = page.numPages
        self._pageNo = page.pageNo
        self.pageDetails = page.details
        self.notifyKw(offset=page.offset, limit=page.limit)
        self.notifyKw(bottom=page.bottom, top=page.top)

    @ymvc.onKwSignal
    def onRequestPageNo(self, requestPageNo):
        print 'Requested pageNo:', requestPageNo

from views import Views
from time  import sleep
from urlparse import urlparse
import httplib2


class UpdateViews(object):
    def __init__(self, table, commited_index, base_url):
        self.views = Views(table, commited_index)
        self.url   = base_url

    def doGet(self, asset_id):
        method  = 'GET'
        body    = ''

        if asset_id is not None:
            uri = urlparse(self.url + asset_id)
            h = httplib2.Http()
            try:
                response, content = h.request(uri.geturl(), method, body)
            except socket.error as err:
                print "error"

            if response['status'] == '200':
                return content
            elif response['status'] == '404':
                return content

    def update(self, t=1):
        items = self.views.query_uncommited()
        for item in items:
            print item
            print self.doGet(item['asset_id'])
            sleep(t)


u = UpdateViews('Views', 'commited-index', 'http://backend.zolechamedia.net/v1/private/updateview/')
u.update()


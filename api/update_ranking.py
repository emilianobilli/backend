from ranking import Ranking
from time  import sleep
from urlparse import urlparse
import httplib2


class UpdateRanking(object):
    def __init__(self, table, commited_index, base_url):
        self.ranking = Ranking(table, commited_index)
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

            print response
            print content
            if response['status'] == '200':
                return content
            elif response['status'] == '404':
                return content

    def update(self, t=1):
        items = self.ranking.query_uncommited()
        for item in items:
            print item
            print self.doGet(item['asset_id'])
            sleep(t)


u = UpdateRanking('Ranking', 'commited-index', 'http://backend.zolechamedia.net/v1/private/updateranking/')
u.update()


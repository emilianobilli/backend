import httplib2
import urlparse

class Subtitle(object):
    def __init__(self, ep=None):
        self.h     = httplib2.Http() 
        self.ep    = ep

    def __get_url(self, asset_id, lang, action='check', format='vtt'):
        url = None
        if asset_id is not None and lang is not None:
            url = '%s/%s/%s/%s/%s' % (self.ep, asset_id,lang,format, action)
        return url

    def doGet(self, url):
        method = 'GET'
        uri    = urlparse.urlparse(url)
        return self.h.request(uri.geturl(), method)

    def check(self, asset_id, lang, format='vtt'):
        url = self.__get_url(asset_id, lang, 'check', format)
	print url
        if url is not None:
            ret, _x = self.doGet(url)
	    print ret
            if 'status' in ret:
                if ret['status'] == '200':
                    return True
                else:
                    return False
        return False

    def get_subtitle_url(self, asset_id, lang,format='vtt'):
        return self.__get_url(asset_id,lang, 'sub')

    def get_subtitle(self, asset_id, lang, format='vtt'):
        pass



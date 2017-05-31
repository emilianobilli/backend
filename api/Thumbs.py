
class Thumbs(object):
    def __init__(self, cdn):
        self.cdn = cdn

    def __get_url(self, asset_id,format= 'vtt'):
        url = None
        if asset_id is not None:
            url = '%s/%s/thumbs/%s.%s' % (self.cdn, asset_id,asset_id,format)
        return url

    def get_url(self, asset_id):
        return self.__get_url(asset_id)


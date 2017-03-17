
class CdnImg(object):
    def __init__(self, cdnbase, path):
        self.cdnbase = cdnbase
        self.path    = path
        self.i       = 0
        self.q       = 60

    def nxt(self):
        if len(self.cdnbase) == self.i + 1:
            self.i = 0
        else:
            self.i = self.i + 1
        return self.i

    def getUrl(self, filename, width=None):
        if width is not None:
            return '%s%s%s?w=%s' % (self.cdnbase[self.nxt()],
                                         self.path,
                                         filename, str(width) if type(width).__name__ == 'int' else width)
        else:
            return '%s%s%s' % (self.cdnbase[self.nxt()],
                               self.path,
                               filename)

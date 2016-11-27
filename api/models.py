from Collection import dynamodbCollection
from Collection import cloudsearchCollection



class objBase(object):
    def __init__(self):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError

    def query(self):
        raise NotImplementedError

    def put(self):
        raise NotImplementedError

    def post(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError



class Blocks(objBase):
    def __init__(self, config):
        self.db = dynamodbCollection(config)

    def query(self, lang=None):
        if lang is not None:
            return self.db.query(lang)



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


class smallCollection(objBase):
    def __init__(self, db_config):
        self.db = dynamodbCollection(db_config)

    def query(self, pk=None):
        if pk is not None:
            return self.db.query(pk)


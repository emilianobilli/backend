from Collection import dynamodbCollection
from Collection import cloudsearchCollection


class objBase(object):
    def __init__(self):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError

    def query(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def add(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError


class dbCollection(objBase):
    def __init__(self, db_config):
        self.db = dynamodbCollection(db_config)

    def query(self, pk=None):
        if pk is not None:
            return self.db.query(pk)


class dbseCollection(objBase):
    def __init__(self, db_config, se_config):
        self.db = dynamodbCollection(db_config)

    def get(self, pk, sk):
        if pk is not None:
            return self.db.get(pk,sk)

    def query(self, lang=None, fq=[], sort):
        pass



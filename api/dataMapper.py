'''
    Transfomacion
'''
class dataMapper(object):
    def __init__(self, schema={}):
        self.schema = schema
    '''
        This function in only valid for plain
        documents
    '''
    def Map(self, Item={}):
        ret = {}
        keys = Item.keys()
        for k in keys:
            if k in self.schema:
                if self.schema[k] == 'SS' and Item[k] ==[]:
                    continue
                ret[k] = {self.schema[k]: Item[k]}
            else:
                ''' 
                Don't map the keys that not exist in the schema 
                '''
                pass
        return ret

    def unMap(self, Item={}):
        ret = {}
        keys = Item.keys()
        for k in keys:
            if k in self.schema:
                dtk = (Item[k].keys())[0] if len(Item[k].keys()) == 1 else None
                if dtk is not None:
                    ret[k] = Item[k][dtk]
        return ret


class dataStringDict(object):
    def __init__(self, keys=[]):
        self.keys = keys

    def String(self, Item={}):
        ret = {}
        keys = Item.keys()
        for k in keys:
            if k in self.keys:
                if (type(Item[k]).__name__ == 'list' or
                    type(Item[k]).__name__ == 'str'):
                    ret[k] = Item[k]
                elif (type(Item[k]).__name__ == 'int' or 
                    type(Item[k]).__name__ == 'float' or 
                    type(Item[k]).__name__ == 'boolean'):
                    ret[k] = str(Item[k])
                elif type(Item[k]).__name__ == 'unicode':
                    ret[k] = str(Item[k].encode('utf-8'))
            else:
                ''' 
                Don't map the keys that not exist in self.keys 
                '''
        return ret


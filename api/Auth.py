from Collection import dynamodbCollection
from Collection import DynamoException
from Collection import CollectionException
import md5      # token
import time     # token
import json

class Auth(object):
    def __init__(self, config):
        self.table = dynamodbCollection(config)

    def _get_md5_hash(self, seed):
        m = md5.md5()
        s = str(time.time())
        m.update(s + seed)
        return m.hexdigest()

    def create_apikey(self, user_data):
        akey_item = {}
        str_user_data = json.dumps(user_data)
        akey_item['apikey']     = self._get_md5_hash(str_user_data)
        akey_item['enabled']    = 1
        akey_item['expiration'] = int(time.time()) + 7200
        for k in user_data.keys():
            akey_item[k] = user_data[k]
        
        self.table.add(akey_item)

        return {'apikey': akey_item['apikey'], 'expiration': akey_item['expiration']}

    def authorize(self, user_data):
        try:
            body   = self.create_apikey(user_data)
            status = 200            
        except CollectionException as e:
            status = 422
            body   = {'status': 'failure', 'message': str(e)}
        except DynamoException as e:
            status = 500
            body   = {'status': 'failure', 'message': str(e)}
        except Exception as e:
            status = 500
            body   = {'status': 'failure', 'message': str(e)}
        return {'status': status, 'body': body}

    def check_api_key(self, api_key):
        akey_item = {}
        akey_item['apikey'] = api_key

        
        try:
            ret = self.table.get(akey_item)
            if 'item' in ret:
                if ret['item'] != {}:
                    if int(ret['item']['enabled']) == 1:
                        now    = int(time.time())
                        if int(ret['item']['expiration']) > now:
                            status = 200
                            body   = ret['item']
                        else:
                            ret['item']['enabled'] = 0
                            status = 403
                            body   = {'status': 'failure', 'message': 'api-key expired'}
                            self.table.add(ret['item'])
                    else:
                        status = 403
                        body   = {'status': 'failure', 'message': 'api-key expired'}
                else:
                    status = 401
                    body   = {'status': 'failure', 'message': 'invalid api-key'}
            else:
                status = 401
                body   = {'status': 'failure', 'message': 'invalid api-key'}

        except CollectionException as e:
            status = 500
            body   = {'status': 'failure', 'message': str(e)}
        except DynamoException as e:
            status = 500
            body   = {'status': 'failure', 'message': str(e)}
        except Exception as e:
            status = 500
            body   = {'status': 'failure', 'message': str(e)}

        return {'status': status, 'body':body}


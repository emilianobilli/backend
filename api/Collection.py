from dataMapper import dataMapper
from dataMapper import dataStringDict
from csParsers  import Structured
import boto3
import socket
import json
import httplib2
import urlparse

'''
Blocks 
schema = { 'language':  'S',
           'block_id':  'S',
           'block_name: 'S',
           'channel':   'S' }
    {
        "database": {
            "table": "Blocks",
            "pk": "language",
            "sk": "block_id",
            "schema": { 
                "language":  "S",
                "block_id":  "S",
                "block_name: "S",
                "channel":   "S" 
            }
        }
    }              
'''

           
class dynamodbCollection(object):
    def __init__(self, config):
        db = config['database']
        self.table               = db['table']
        if 'pk' not in db:
            pass # Raise exception

        self.pk                  = db['pk']
        if 'sk' in db:
            self.sk              = db['sk']
        else:
            self.sk              = None

        if 'schema' not in db:
            pass # Raise exception

        self.schema              = db['schema']
        self.data_mapper         = dataMapper(self.schema)
        try:
            self.client          = boto3.client('dynamodb')
        except Exception as e:
            pass # Raise exception

    
    
    def _check_query_return(self, ret):
        doc = {}
        n   = 0
        if 'ResponseMetadata' in ret:
            if 'HTTPStatusCode' in ret['ResponseMetadata']:
                if ret['ResponseMetadata']['HTTPStatusCode'] == 200:
                    if 'Count' in ret:
                        doc['count'] = ret['Count']
                    if 'Items' in ret:
                        doc['items']  = []
                        for item in ret['Items']:
                            n = n + 1
                            doc['items'].append(self.data_mapper.unMap(item))
                    if 'Count' in ret:
                        doc['count'] = ret['Count']
                    else:
                        doc['count'] = n

        return doc

    def _check_get_return(self, ret):
        doc = {}
        if 'ResponseMetadata' in ret:
            if 'HTTPStatusCode' in ret['ResponseMetadata']:
                if ret['ResponseMetadata']['HTTPStatusCode'] == 200:
                    if 'Item' in ret:
                        doc['item'] = self.data_mapper.unMap(ret['Item'])
                    else:
                        doc['item'] = {}
        return doc



    def query(self, pkv=None):
        if pkv is None:
            pass # Raise -> Need Partition Key

        ret =  self.client.query(TableName=self.table,
                                 KeyConditionExpression='%s = :val' % (self.pk), 
                                 ExpressionAttributeValues={':val': {self.schema[self.pk]: pkv}})

        return self._check_query_return(ret)

    def get(self, pkv=None, skv=None):
        
        to_get = {}
        
        if pkv is None:
            pass # Raise -> Need Partition Key to perform a get_item()
        
        to_get[self.pk] = pkv
        
        
        if self.sk is not None:
            if skv is None:
                pass # Raise -> Need Sort Key
            else:
                to_get[self.sk] = skv

        doc = self.data_mapper.Map(to_get)

        ret = self.client.get_item(TableName=self.table, Key=doc)

        return self._check_get_return(ret)
        
    def add(self, Item ={}):


        if self.pk not in Item:
            return {'status': 'fail', 'message': 'Primary key not present in Item -> %s' % self.pk }

        if self.sk is not None:
            if self.sk not in Item:
                return {'status': 'fail', 'message': 'Sork key not present in Item -> %s' % self.sk }

        '''
        Primero convertir todos los campos a String
        '''
        dsd = dataStringDict(Item.keys()).String(Item)
        doc = self.data_mapper.Map(dsd)

        try:
            ret = self.client.put_item(TableName=self.table, Item=doc)
            if 'ResponseMetadata' in ret:
                if 'HTTPStatusCode' in ret['ResponseMetadata'] and ret['ResponseMetadata']['HTTPStatusCode'] == 200:
                    return {'status': 'success'}
                else:
                    return {'status': 'fail', 'message': str(ret)}
        except Exception, e:
            return {'status': 'fail', 'message' : str(e)}


    def delete(self, pkv=None, skv=None):
        toDel = {}

        if pkv is None:
            pass # Raise Error
        else:
            toDel[self.pk] = pkv

        if self.sk is not None:
            if skv is None:
                return {'status': 'fail', 'message': 'Sort key (%s) not in Item (%s)' % (self.sortKey, Item) }
            else:
                toDel[self.sk]  = skv

        doc = self.data_mapper.Map(toDel)

        try:
            ret = self.client.delete_item(TableName=self.table, Key=doc)
            if 'ResponseMetadata' in ret:
                if 'HTTPStatusCode' in ret['ResponseMetadata'] and ret['ResponseMetadata']['HTTPStatusCode'] == 200:
                    return {'status': 'success'}
                else:
                    return {'status': 'fail', 'message': str(ret)}
        except Exception, e:
            return {'status': 'fail', 'message' : str(e)}


db = dynamodbCollection({
        "database": {
            "table": "Blocks",
            "pk": "lang",
            "sk": "block_id",
            "schema": { 
                "lang":  "S",
                "block_id":  "S",
                "block_name": "S",
                "channel":   "S" 
            }
        }
    })

'''
    { "domain": {
        "id_field": "house_id",
        "name": "",
        "filter_query": {},
        "schema": [],
        "return_field": [],
        "parser": "",
        "useHttps": "",
        }
    }
'''


class cloudsearchCollection(object):
    def __init__(self, config, parser=Structured):
	self.client       = boto3.client('cloudsearch')

        if not 'domain' in config:
            pass # Raise

        domain = config['domain']

        if not 'name' in domain:
            pass # Raise

        if not 'useHttps' in domain:
            self.useHttps = False

        self.parser_class = parser
	self.domain_name  = domain['name']
	
	domain = self.__get_domain()

	if domain is not None:
	    if self.useHttps:
		base = 'https://'
	    else:
		base = 'http://'
	    document_ep = base + domain['DocService']['Endpoint']
	    search_ep   = base + domain['SearchService']['Endpoint']
	    self.__endpoint_init(document_ep,search_ep)
	else:
	    pass # Raise

    def __get_domain(self):
	try:
	    response = self.client.describe_domains(DomainNames=[self.domain_name])
	except:
	    pass
	if 'DomainStatusList' in response and len(response['DomainStatusList']) == 1:
	    domain = response['DomainStatusList'][0]
	    return domain
	return None

    def __endpoint_init(self, document_ep, search_ep):
	self.document_endpoint 	= document_ep
	self.search_endpoint   	= search_ep
	self.document_url      	= '2013-01-01/documents/batch'
	self.search_url		= '2013-01-01/search'
	self.document_endpoint  = self.document_endpoint + '/' if not self.document_endpoint.endswith('/') else self.document_endpoint
	self.search_endpoint	= self.search_endpoint   + '/' if not self.search_endpoint.endswith('/')   else self.search_endpoint  

    def doPost(self, body):
	method = 'POST'
	header = { 'Content-type': 'application/json' }

	uri = urlparse.urlparse(self.document_endpoint + self.document_url) 
	h = httplib2.Http()

	try:
    	    response, content = h.request(uri.geturl(), method, body, header)
	except socket.error as err:
	    return False, err

    	return response, content

    def doGet(self, qString):
	method = 'GET'

	qString = qString.replace(' ', '%20')
	qString = qString.replace('\'', '%27')

        print self.search_endpoint + self.search_url + '?' + qString
	uri = urlparse.urlparse(self.search_endpoint + self.search_url + '?' + qString)
	h = httplib2.Http()

	try:
	    response, content = h.request(uri.geturl(), method)
	except socket.error as err:
    	    return False, err

	return response, content

    def delete(self, did):
	doc = {}
	doc['id']   = did
	doc['type'] = 'delete'

	response, content = self.doPost(json.dumps([doc]))
	if response and 'status' in response:
	    if response['status'] == '200':
		return True, content
	    else:
		return False, content
    
	return False, content

    def add(self, did, fields):
	doc = {}
	doc['id']     = did
	doc['type']   = 'add'
	doc['fields'] = fields

	response, content = self.doPost(json.dumps([doc]))
	if response and 'status' in response:
	    if response['status'] == '200':
		return True, content
	    else:
		return False, content
	return False, content

    def get(self, did):
        pass


    def _check_query_return(self, ret):
        doc = {}
        doc['count'] = 0
        doc['total'] = 0
        doc['items'] = []
        response, content = ret
        
        if response:
            if 'status' in response and response['status'] == '200':
                cs_reply = json.loads(content)
                if 'hits' in cs_reply:
                    if 'found' in cs_reply['hits']:
                        doc['total'] = cs_reply['hits']['found']
                        if doc['total'] > 0:
                            hit = cs_reply['hits']['hit']
                            for d in hit:
                                doc['count'] = doc['count'] + 1
                                doc['items'].append(d['fields'])
                
        return doc


    def query(self, querylist=[], start=0, size=10, sort=None, order=None):
        p = self.parser_class()
        for q in querylist:
            if type(q).__name__ == 'dict':
                p.fq_add(q)

        p.start = start
        p.size  = size
        qString = p.make()
        ret = self.doGet(qString)

        return self._check_query_return(ret)

    def search(self):
        pass



#cs = cloudsearchCollection({ 'domain': { 'name': 'sdhotgotest'}})
#fq = [{'channel': 'Venus'}, {'category': 'anal'}]
#print cs.query(fq)
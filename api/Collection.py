from dataMapper import dataMapper
from dataMapper import dataStringDict
from csParsers  import Structured
import boto3
import socket
import json
import httplib2
import urlparse

class CollectionException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class DynamoException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class CloudSearchException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class dynamodbCollection(object):
    def __init__(self, config):
        db = config['database']

        self.table               = db['table']
        if 'pk' not in db:
            CollectionException('(__init__) Primary Key field not found in config')

        self.pk                  = db['pk']
        if 'sk' in db:
            self.sk              = db['sk']
        else:
            self.sk              = None

        if 'schema' not in db:
            CollectionException('(__init__) Schema not found in config')

        self.schema              = db['schema']
        self.data_mapper         = dataMapper(self.schema)
        try:
            self.client          = boto3.client('dynamodb')
        except Exception, e:
            DynamoException(str(e))

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

    def _check_get_return(self, ret, ppArg=None):
        doc = {}
        if 'ResponseMetadata' in ret:
            if 'HTTPStatusCode' in ret['ResponseMetadata']:
                if ret['ResponseMetadata']['HTTPStatusCode'] == 200:
                    if 'Item' in ret:
                        doc['item'] = self.data_mapper.unMap(ret['Item'])
                    else:
                        doc['item'] = {}
        return doc



    def query(self, q={}):

        if self.pk not in q:
            raise CollectionException('(Query) Primary key not found in item (%s)' % self.pk )

        try:
            ret =  self.client.query(TableName=self.table,
                                     KeyConditionExpression='%s = :val' % (self.pk), 
                                     ExpressionAttributeValues={':val': {self.schema[self.pk]: q[self.pk]}})
        except Exception, e:
            raise DynamoException(str(e))

        return self._check_query_return(ret)

    def get(self, Item={}):
        
        to_get = {}
        
        if self.pk not in Item:
            raise CollectionException('(Get) Primary key not found in item (%s)' % self.pk )

        if self.sk is not None:
            if self.sk not in Item:
                raise CollectionException('(Get) Sort key not found in item (%s)' % self.sk )
            to_get[self.sk] = Item[self.sk]

        to_get[self.pk] = Item[self.pk]

        doc = self.data_mapper.Map(to_get)

        try:
            ret = self.client.get_item(TableName=self.table, Key=doc)
        except Exception, e:
            raise DynamoException(str(e))

        return self._check_get_return(ret)


    def add(self, Item ={}):

        if self.pk not in Item:
            raise CollectionException('(Add) Primary key not found in item (%s)' % self.pk )

        if self.sk is not None:
            if self.sk not in Item:
                raise CollectionException('(Add) Sort key not found in item (%s)' % self.sk )

        '''
        Primero convertir todos los campos a String
        '''
        dsd = dataStringDict(Item.keys()).String(Item)
        doc = self.data_mapper.Map(dsd)
        try:
            ret = self.client.put_item(TableName=self.table, Item=doc)
        except Exception, e:
            raise DynamoException(str(e))
        
        if 'ResponseMetadata' in ret:
            if 'HTTPStatusCode' not in ret['ResponseMetadata'] or ret['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise DynamoException(str(ret))
        
        return Item

    def delete(self, Item={}):
        toDel = {}

        if self.pk not in Item:
            raise CollectionException('(Delete) Primary key not found in item (%s)' % self.pk )

        toDel[self.pk] = Item[self.pk]

        if self.sk is not None:
            if self.sk not in Item:
                raise CollectionException('(Delete) Sort key not found in item (%s)' % self.sk )
            toDel[self.sk] = Item[self.sk]

        doc = self.data_mapper.Map(toDel)

        try:
            ret = self.client.delete_item(TableName=self.table, Key=doc)
        except Exception, e:
            raise DynamoException(str(e))

        if 'ResponseMetadata' in ret:
            if 'HTTPStatusCode' not in ret['ResponseMetadata'] or ret['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise DynamoException(str(ret))

        return toDel

'''
    { "domain": {
        "id_field": "house_id",
        "name": "",
        "filter_query": {},
        "schema": [],
        "return_field": [],
        "useHttps": "",
        }
    }
'''


class cloudsearchCollection(object):
    def __init__(self, config, parser=Structured):

	self.client       = boto3.client('cloudsearch')

        if not 'domain' in config:
            raise CollectionException('(__init__) Domain not found in config')

        domain = config['domain']

        #
        # Se consulta la existencia de los campos 
        # mandatorios
        #

        if (not 'name'          in domain or
            not 'id_field'      in domain or
            not 'schema'        in domain or
            not 'return_fields' in domain):
            raise CollectionException('(__init__) Mandatory value not found in config')


        self.id_field           = domain['id_field']
        self.schema             = domain['schema']
        self.return_fields      = domain['return_fields']
        self.parser_class       = parser
	self.domain_name        = domain['name']

        if not 'useHttps' in domain:
            self.useHttps = False
        else:
            self.useHttps = domain['useHttps']

        self.__init_domain()

        self.h = httplib2.Http()

    def __get_domain(self):
	try:
	    response = self.client.describe_domains(DomainNames=[self.domain_name])
	except Exception, e:
	    raise CloudSearchException('(__get_domain) ' + e)
	if 'DomainStatusList' in response and len(response['DomainStatusList']) == 1:
	    domain = response['DomainStatusList'][0]
	    return domain
	return None

    
    def __init_domain(self):
        search_domain = self.__get_domain()

	if search_domain is not None:
	    if self.useHttps:
		base = 'https://'
	    else:
		base = 'http://'
	    document_ep = base + search_domain['DocService']['Endpoint']
	    search_ep   = base + search_domain['SearchService']['Endpoint']
	    self.__endpoint_init(document_ep,search_ep)
	else:
	    raise CloudSearchException('(__init_domain) Unable to found Domain')

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
#	h = httplib2.Http()
        
        print body

	try:
    	    response, content = self.h.request(uri.geturl(), method, body, header)
	except socket.error as err:
	    raise CloudSearchException('(doPost) ' + err)

    	return response, content

    def doGet(self, qString):
	method = 'GET'

	qString = qString.replace(' ', '%20')
	qString = qString.replace('\'', '%27')

#        print self.search_endpoint + self.search_url + '?' + qString
	uri = urlparse.urlparse(self.search_endpoint + self.search_url + '?' + qString)
#	h = httplib2.Http()

	try:
	    response, content = self.h.request(uri.geturl(), method)
	except socket.error as err:
    	    raise CloudSearchException('(doGet) ' + err)

	return response, content

    def _delete(self, did):
	doc = {}
	doc['id']   = did
	doc['type'] = 'delete'

	response, content = self.doPost(json.dumps([doc]))
	if response and 'status' in response:
	    if response['status'] != '200':
		raise CloudSearchException(str(content))
	else:
            raise CloudSearchException('(Delete) Unable to found return status code')

        return did

    def delete(self, Item={}):
        if self.id_field not in Item:
            raise CollectionException('(Add) Id field not found in item (%s)' % self.id_field )
        did = Item[self.id_field]
        return self._delete(did)

    def add(self, Item={}):

        if self.id_field not in Item:
            raise CollectionException('(Add) Id field not found in item (%s)' % self.id_field )

        did = Item[self.id_field]
        doc = dataStringDict(self.schema).String(Item)
        return self._add(did,doc)


    def _add(self, did, fields):
	doc = {}
	doc['id']     = did
	doc['type']   = 'add'
	doc['fields'] = fields

	response, content = self.doPost(json.dumps([doc]))
        if response and 'status' in response:
	    if response['status'] != '200':
		raise CloudSearchException(str(content))
	else:
            raise CloudSearchException('(Delete) Unable to found return status code')

	return did


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


    def query(self, querylist=[], exclude=None, start=0, size=10, sort=None):
        p = self.parser_class()
        for ql in querylist:
            p.fq_add(ql)
        p.return_fields = self.return_fields
        p.exclude = exclude
        p.start   = start
        p.size    = size
        p.sort    = sort
        qString   = p.make()

        ret = self.doGet(qString)

        return self._check_query_return(ret)

    def search(self, q=None, exclude=None, start=0, size=10):
        p = self.parser_class()
        p.q = q
        p.exclude = exclude
        p.start   = start
        p.return_fields = self.return_fields
        p.size    = size

        qString   = p.make()

        ret = self.doGet(qString)
        return self._check_query_return(ret)



#cs = cloudsearchCollection({ 'domain': { 'name': 'sdhotgotest'}})
#fq = [{'channel': 'Venus'}, {'category': 'anal'}]
#print cs.query(fq)
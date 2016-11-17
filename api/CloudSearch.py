import boto3
import socket
import json
import httplib2
import urlparse
from urllib import urlencode

class CloudSearchDomains(object):
    def __init__(self):
	self.cs_domain_interface = {}

    def addDomain(self, domainName):
	self.cs_domain_interface[domainName] = CloudSearch(domainName)

    def onDomain(self, domainName):
	return self.cs_domain_interface[domainName]

class CloudSearch(object):
    def __init__(self, domainName, useHttps=True):
	self.client     = boto3.client('cloudsearch')
	self.domainName = domainName
	
	domain = self.__get_domain()
	if domain is not None:
	    if useHttps:
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
	    response = self.client.describe_domains(DomainNames=[self.domainName])
	except:
	    pass
	if 'DomainStatusList' in response and len(response['DomainStatusList']) == 1:
	    domain = response['DomainStatusList'][0]
	    return domain
	return None

    def Processing(self):
	domain = self.__get_domain()
	if domain is not None:
	    return domain['Processing']

    def RequiresIndexDocuments(self):
	domain = self.__get_domain()
	if domain is not None:
	    return domain['RequiresIndexDocuments']


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

	uri = urlparse.urlparse(self.search_endpoint + self.search_url + '?' + qString)
	h = httplib2.Http()

	try:
	    response, content = h.request(uri.geturl(), method)
	except socket.error as err:
    	    return False, err

	return response, content

    def deleteDocument(self, did):
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

    def addDocument(self, did, fields):
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


    def searchByLiteral(self, literal=None, literal_field=None, start=None, size=None,sort=None,return_fields=None):

	if literal is None or literal_field is None:
	    return False, ''

	if type(literal).__name__ == 'list':
	    queryLiteral = " ".join(literal)
	else:
	    queryLiteral = literal

	query = 'q=%s&q.options={fields:[\'%s\']}' % (queryLiteral,literal_field)

	if start is not None:
	    if type(start).__name__ == 'str':
		if start.isdigit():
		    int_start = int(start)
		else:
		    pass # Raise Exception
	    elif type(start).__name__ == 'int':
		int_start = start
	    else:
		pass # Raise Exception
	
	    query = query + '&start=%d' % int_start

	if size is not None:
	    if type(size).__name__ == 'str':
		if size.isdigit():
		    int_size = int(size)
		else:
		    pass # Raise Exception
	    elif type(size).__name__ == 'int':
		int_size = size
	    else:
		pass # Raise Exception
	    
	    query = query + '&size=%d' % int_size
	

	if sort is not None:
	    if sort.startswith('-'):
		qsort = '%s desc' % sort[1:]
	    else:
		qsort = '%s asc' % sort
	    query = query + '&sort=%s' % qsort
        
	
	if return_fields is not None:
	    query = query + '&return=%s' % (",".join(return_fields) if type(return_fields).__name__ == 'list' else return_fields)

	response, content =  self.doGet(query)
	if response and 'status' in response:
	    if response['status'] == '200':
		return True, content
	    else:
		return False, content
	return False, content


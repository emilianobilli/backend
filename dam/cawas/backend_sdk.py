from urlparse import urlparse
import httplib2
import json
import socket


class ApiBackendException(Exception):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)


class ApiBackendServer(object):
    def __init__(self, apiurl = ''):
        self.apiurl  = apiurl

    def get(self, url):
        method = 'GET'
        body   = ''

        if url is not None:
            uri = urlparse(self.apiurl + url)
        else:
            raise ApiBackendException('get(): url cannot be None')

        http = httplib2.Http()

        try:
            response, content = http.request(uri.geturl(),  method, body)
        except socket.error as err:
            raise ApiBackendException(err)

        if response['status'] == '200':
            return content
        else:
            cont = json.loads(content)
            raise ApiBackendException(cont['message'])


    def post(self, url, apikey, body):
        method = 'POST'
        header = { 'Content-type': 'application/json', 'X-PRIVATE-APIKEY': apikey}

        http = httplib2.Http()

        if url is not None:
            uri = urlparse(self.apiurl + url)
        else:
            raise ApiBackendException('post(): url cannot be None')

        try:
            response, content = http.request(uri.geturl(), method, json.dumps(body), header)
        except socket.error as err:
            raise ApiBackendException(err)

        if response['status'] == '201':
            return content
        else:
            try:
                cont = json.loads(content)
                raise ApiBackendException(cont['message'])
            except ValueError:
                raise ApiBackendException("Deconding JSON has failed")



    def delete(self, url, apikey, body):
        method = 'POST'
        header = {'Content-type': 'application/json', 'X-PRIVATE-APIKEY': apikey}

        http = httplib2.Http()

        if url is not None:
            uri = urlparse(self.apiurl + url)
        else:
            raise ApiBackendException('delete(): url cannot be None')

        try:
            response, content = http.request(uri.geturl(), method, json.dumps(body), header)
        except socket.error as err:
            raise ApiBackendException(err)
        print response, content
        if response['status'] == '204':
            return content
        else:
            cont = json.loads(content)
            raise ApiBackendException(cont['message'])


class ApiBackendResource(object):
    def __init__(self, server, url, apikey):
        self.server = ApiBackendServer(server)
        self.url = url
        self.apikey = apikey

    def add(self, item):
        print 'backend_sdk_add' + str(item)
        return self.server.post(self.url, self.apikey, {"action":"add", "item":item})

    def update(self, item):
        return self.server.post(self.url, self.apikey, {"action":"add", "item":item})

    def delete(self, item):
        return self.server.delete(self.url, self.apikey, {"action":"del", "item":item})

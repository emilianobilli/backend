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
            raise ApiBackendException(cont['error'])


    def post(self, url, body):
        method = 'POST'
        header = { 'Content-type': 'application/json' }

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
            cont = json.loads(content)
            raise ApiBackendException(cont['error'])


    def delete(self, url, body):
        method = 'DELETE'
        header = {'Content-type': 'application/json'}

        http = httplib2.Http()

        if url is not None:
            uri = urlparse(self.apiurl + url)
        else:
            raise ApiBackendException('delete(): url cannot be None')

        try:
            response, content = http.request(uri.geturl(), method, json.dumps(body), header)
        except socket.error as err:
            raise ApiBackendException(err)

        if response['status'] == '204':
            return content
        else:
            cont = json.loads(content)
            raise ApiBackendException(cont['message'])


class ApiBackendResource(object):
    def __init__(self, server, url):
        self.server = ApiBackendServer(server)
        self.url = url

    def add(self, item):
        return self.server.post(self.url, json.dumps(item))

    def update(self, item):
        return self.server.post(self.url, json.dumps(item))

    def delete(self, item):
        return self.server.delete(self.url, json.dumps(item))

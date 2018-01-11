import os, datetime, json
from django.http import HttpResponse
from ..models import Asset
from django.shortcuts import render,redirect


class TagController(object):

    def index(self, request):
        data = {'code': 200, 'message': 'Guardado Correctamente'}
        return render(request, 'cawas/videotag/index.html', None)


    def add(self, request):


        if request.is_ajax():
            if request.method == 'POST':
                try:
                    #crear videotag
                    data = {'code': 200, 'message': 'Guardado Correctamente'}
                    return HttpResponse(json.dumps(data), None, 200)
                except Asset.DoesNotExist as e:
                    return HttpResponse("No existe Asset", None, 500)

        return render(request, 'cawas/videotag/index.html', None)



    def delete(self, request):
        data = {'code': 200, 'message': 'Guardado Correctamente'}
        return HttpResponse(json.dumps(data), None, 200)



    def findAll(self):
        data =[
                {'id': 1, 'description': 'Tag 1'},
                {'id': 2, 'description': 'Tag 2'},
               ]
        return HttpResponse(json.dumps(data), None, 200)



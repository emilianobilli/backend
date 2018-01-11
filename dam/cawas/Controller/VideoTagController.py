import os, datetime, json
from django.http import HttpResponse
from ..models import Asset
from django.shortcuts import render,redirect


class VideoTagController(object):

    def index(self, request):
        tags = Asset.objects.all()
        context ={'tags': tags}
        return render(request, 'cawas/videotag/index.html', context)


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


    def ajaxtags(self, request):
        tags = Asset.objects.all()

        if request.method == 'GET':
            tagsjson=[]

            for t in tags:
                tagsjson.append({"id":t.id,"descripcion":t.asset_id})

            print 'debug1' + str(json.dumps(tagsjson))
            return HttpResponse(json.dumps(tagsjson), None, 200)

        else:
            return HttpResponse("Metodo no permitido", None, 500)

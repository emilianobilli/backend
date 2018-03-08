from django.http import HttpResponse
from ..models import Asset
import os, datetime, json


class ContractController(object):

    def add(self,request):
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    json_data = json.loads(request.body)


                    mydata = [{'code': 200, 'message': 'Guardado Correctamente'}]
                    return HttpResponse(json.dumps(mydata), None, 200)
                except Asset.DoesNotExist as e:
                    return HttpResponse("No existe Asset", None, 500)
                except KeyError:
                    return HttpResponse("Error en decodificacion de datos", None, 500)


    def edit(self, request):
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    json_data = json.loads(request.body)

                    mydata = [{'code': 200, 'message': 'Guardado Correctamente'}]
                    return HttpResponse(json.dumps(mydata), None, 200)
                except Asset.DoesNotExist as e:
                    return HttpResponse("No existe Asset", None, 500)
                except KeyError:
                    return HttpResponse("Error en decodificacion de datos", None, 500)



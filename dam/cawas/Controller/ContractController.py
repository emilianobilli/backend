from django.http import HttpResponse
from ..models import Asset, Contract
import os, datetime, json, logging
from django.shortcuts import render,redirect


class ContractController(object):

    #Get
    def add(self,request):
        context = {}
        return render(request, 'cawas/contracts/add.html', context)

    #Get
    def edit(self,request, id):
        item = Contract.objects.get(id=id)
        context = {'item':item}
        return render(request, 'cawas/contracts/edit.html', context)


    def list(self, request):
        try:
            registros = Contract.objects.all()
            context = {'registros':registros}
            return render(request, 'cawas/contracts/list.html', context)
        except Asset.DoesNotExist as e:
            return HttpResponse("No existe Asset", None, 500)
        except KeyError:
            return HttpResponse("Error en decodificacion de datos", None, 500)


    #Post Json
    def api_add(self,request):
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    self.getDataFormAndSave(request)
                    mydata = [{'code': 200, 'message': 'Guardado Correctamente'}]
                    return HttpResponse(json.dumps(mydata), None, 200)
                except Asset.DoesNotExist as e:
                    return HttpResponse("No existe Asset", None, 500)
                except KeyError:
                    return HttpResponse("Error en decodificacion de datos", None, 500)



    #Post Json
    def api_edit(self, request):
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    self.getDataFormAndSave(request)
                    mydata = [{'code': 200, 'message': 'Guardado Correctamente'}]
                    return HttpResponse(json.dumps(mydata), None, 200)
                except Asset.DoesNotExist as e:
                    return HttpResponse("No existe Asset", None, 500)
                except KeyError:
                    return HttpResponse("Error en decodificacion de datos", None, 500)

                    # Post Json

    def api_delete(self, request):
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    self.getDataFormAndDelete(request)
                    mydata = [{'code': 200, 'message': 'Guardado Correctamente'}]
                    return HttpResponse(json.dumps(mydata), None, 200)
                except Asset.DoesNotExist as e:
                    return HttpResponse("No existe Asset", None, 500)
                except KeyError:
                    return HttpResponse("Error en decodificacion de datos", None, 500)



    def getDataFormAndSave(self,request):
        try:
            json_data    = json.loads(request.body)
            contract = Contract()
            if ('id' in json_data['contract']):
                id           = json_data['contract']['id']
                contract = Contract.objects.get(id=id)

            nombre       = json_data['contract']['nombre']
            descripcion  = json_data['contract']['descripcion']
            provider     = json_data['contract']['provider']
            fecha_inicio = datetime.datetime.strptime(json_data['contract']['fecha_inicio'], '%d-%m-%Y').strftime('%Y-%m-%d')
            fecha_fin    = datetime.datetime.strptime(json_data['contract']['fecha_fin'], '%d-%m-%Y').strftime('%Y-%m-%d')

            contract.name        = nombre
            contract.description = descripcion
            contract.start_date  = fecha_inicio
            contract.end_date    = fecha_fin
            contract.provider    = provider
            contract.save()

        except Exception as e:
            logging.exception("Error: " + e.message)


    def getDataFormAndDelete(self, request):
        try:
            json_data = json.loads(request.body)
            id = json_data['contract']['id']
            contract = Contract()
            contract = Contract.objects.get(id=id)
            contract.delete()
        except Exception as e:
            logging.exception("Error: " + e.message)
from django.http import HttpResponse
from ..models import Asset, Contract, FatherAsset
import os, datetime, json, logging
from django.shortcuts import render,redirect


class FatherAssetController(object):


    #Get
    def add(self,request):
        contracts = Contract.objects.all()
        context = {'contracts':contracts}
        return render(request, 'cawas/fatherassets/add.html', context)

    #Get
    def edit(self,request, id):
        item = FatherAsset.objects.get(id=id)
        contracts = Contract.objects.all()
        context = {'item':item, 'contracts':contracts}
        return render(request, 'cawas/fatherassets/edit.html', context)


    def list(self, request):
        try:
            contracts = Contract.objects.all()
            registros = FatherAsset.objects.all()
            context = {'registros':registros, 'contracts':contracts }
            return render(request, 'cawas/fatherassets/list.html', context)
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
            fatherasset = FatherAsset()
            if ('id' in json_data['item']):
                if json_data['item']['id'] != '':
                    id           = int(json_data['item']['id'])
                    fatherasset = FatherAsset.objects.get(id=id)

            asset_id       = json_data['item']['asset_id']
            contract       = Contract.objects.get(id=json_data['item']['contract'])
            duration       = int(json_data['item']['duration'])
            arrival_date   = datetime.datetime.strptime(json_data['item']['arrival_date'], '%d-%m-%Y').strftime('%Y-%m-%d')


            fatherasset.asset_id     = asset_id
            fatherasset.contract     = contract
            fatherasset.arrival_date = arrival_date
            fatherasset.duration     = duration
            fatherasset.save()

        except Exception as e:
            logging.exception("Error: " + e.message)


    def getDataFormAndDelete(self, request):
        try:
            json_data   = json.loads(request.body)
            id          = int(json_data['item']['id'])
            fatherasset = FatherAsset.objects.get(id=id)
            fatherasset.delete()
        except Exception as e:
            logging.exception("Error: " + e.message)
import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import PackagePrice, CableOperator, Country, PackagePrice
from django.http import HttpResponse
from django.template.defaulttags import register
from django.contrib import messages

RULES = {'H': 'HotGo Registration Page',
         'P': 'Provider Registration Page',
         'D': 'Default Page'}

class PackagePriceController(object):
    #Option


    def add(self, request):
        try:
            if request.is_ajax():
                if request.method == 'POST':
                    json_data = json.loads(request.body)
                    rr = PackagePrice()
                    if (json_data['data']['country'] is not None):
                        if (json_data['data']['country'] > 0):
                            country_id = json_data['data']['country']
                            country    = Country.objects.get(id=country_id)
                            rr.country = country

                    if (json_data['data']['price'] is not None):
                        if (json_data['data']['price'] != ''):
                            price = json_data['data']['price']
                            rr.price = price

                    if (json_data['data']['price_display'] is not None):
                        if (json_data['data']['price_display'] != ''):
                            price_display = json_data['data']['price_display']
                            rr.price_display = price_display

                    rr.save()
                    mydata = [{'code': 200, 'message': 'Guardado Correctamente'}]
                    #messages.add_message(request, messages.INFO, 'Guardado Correctamente')
                    return HttpResponse(json.dumps(mydata), None, 200)


            if request.method == 'GET':
                countries = Country.objects.all()



                context = {
                    'title': 'Package Price',
                    'countries': countries,
                    'rules':RULES
                }
                return render(request, 'cawas/packageprices/add.html', context)


        except Country.DoesNotExist as e:
            return HttpResponse("Error: No Existe Pais (" + str(e.message) + ")", None, 500)
        except Exception as e:
            return HttpResponse("Hubo un error:(" + str(e.message) + ")", None, 500)
        except KeyError:
            return HttpResponse("Error en decodificacion de datos", None, 500)



    def edit(self, request, id ):
        try:
            if request.is_ajax():
                if request.method == 'POST':
                    json_data = json.loads(request.body)

                    rr = PackagePrice.objects.get(id=json_data['data']['packageprice_id'])
                    print 'edit: ' + str(json_data)
                    if (json_data['data']['country'] is not None):
                        if (json_data['data']['country'] > 0):
                            country_id = json_data['data']['country']
                            country = Country.objects.get(id=country_id)
                            rr.country = country
                            print 'edit: ' +country_id
                    if (json_data['data']['price'] is not None):
                        if (json_data['data']['price'] != ''):
                            price = json_data['data']['price']
                            rr.price = price
                            print 'edit: ' + price
                    if (json_data['data']['price_display'] is not None):
                        if (json_data['data']['price_display'] != ''):
                            price_display = json_data['data']['price_display']
                            rr.price_display = price_display
                            print 'edit: ' + price_display
                    rr.save()
                    mydata = [{'code': 200, 'message': 'Guardado Correctamente'}]
                    #messages.add_message(request, messages.INFO, 'Guardado Correctamente')
                    return HttpResponse(json.dumps(mydata), None, 200)




            if request.method == 'GET':
                if not request.user.is_authenticated:
                    lc = LogController()
                    return redirect(lc.login_view(request))

                registro = PackagePrice.objects.get(id=id)
                countries = Country.objects.all()
                cableoperators = CableOperator.objects.all()

                context = {
                           'registro':  registro,
                           'countries': countries,
                           'rules':     RULES
                           }
                return render(request, 'cawas/packageprices/edit.html', context)

        except CableOperator.DoesNotExist as e:
            return HttpResponse("No existe Cable Operador",None, 500)
        except Country.DoesNotExist as e:
            return HttpResponse("Error: No Existe Pais (" + str(e.message) + ")", None, 500)
        except Exception as e:
            return HttpResponse("Hubo un error:(" + str(e.message) + ")", None, 500)
        except KeyError:
            return HttpResponse("Error en decodificacion de datos", None, 500)





    def index(self, request, ):
        try:
            registros = PackagePrice.objects.all()
            context = {'title': 'Listado Package Price',
                       'registros': registros,
                       'rules': RULES
                       }
            return render(request, 'cawas/packageprices/list.html', context)
        except Country.DoesNotExist as e:
            return HttpResponse("Error: No Existe Pais (" + str(e.message) + ")", None, 500)
        except Exception as e:
            return HttpResponse("Hubo un error:(" + str(e.message) + ")", None, 500)
        except KeyError:
            return HttpResponse("Error en decodificacion de datos", None, 500)




    def delete(self, request):
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    json_data = json.loads(request.body)
                    id        = json_data['id']
                    print 'Id: ' + id
                    rr = PackagePrice.objects.get(id=id)
                    rr.delete()

                    mydata = [{'code': 200, 'message': 'Guardado Correctamente'}]

                    return HttpResponse(json.dumps(mydata), None, 200)
                except PackagePrice.DoesNotExist as e:
                    mydata = [{'code': 500, 'message': 'No existe el Registro'}]
                    return HttpResponse(json.dumps(mydata), None, 500)
                except Exception as e:
                    mydata = [{'code': 500, 'message': e.message}]
                    return HttpResponse(json.dumps(mydata), None, 500)


    @register.filter
    def get_item(dictionary, key):
        return dictionary.get(key)


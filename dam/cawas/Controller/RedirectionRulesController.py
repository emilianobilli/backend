import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import RedirectionRule, CableOperator, Country
from django.http import HttpResponse
from django.template.defaulttags import register
from django.contrib import messages

RULES = {'H': 'HotGo Registration Page',
         'P': 'Provider Registration Page',
         'D': 'Default Page'}

class RedirectionRulesController(object):
    #Option
    # HotGoRegistrationPage, ProviderRegistrationPage, DefaultPage

    def add(self, request):
        try:
            if request.is_ajax():
                if request.method == 'POST':
                    json_data = json.loads(request.body)
                    print 'debug1'
                    rr = RedirectionRule()
                    if (json_data['redirectionrules']['cableoperator'] is not None):
                        if json_data['redirectionrules']['cableoperator'] != '':
                            co_id = json_data['redirectionrules']['cableoperator']
                            co = CableOperator.objects.get(id=co_id)
                            rr.cableoperator = co

                    if (json_data['redirectionrules']['country'] is not None):
                        if (json_data['redirectionrules']['country'] > 0):
                            country_id = json_data['redirectionrules']['country']
                            country = Country.objects.get(id=country_id)
                            rr.country = country

                    if (json_data['redirectionrules']['rule'] is not None):
                        if (json_data['redirectionrules']['rule'] != ''):
                            rule_id = json_data['redirectionrules']['rule']
                            rr.rule = rule_id

                    rr.save()
                    mydata = [{'code': 200, 'message': 'Guardado Correctamente'}]
                    messages.add_message(request, messages.INFO, 'Guardado Correctamente')
                    return HttpResponse(json.dumps(mydata), None, 200)


            if request.method == 'GET':
                countries = Country.objects.all()
                cableoperators = CableOperator.objects.all()


                context = {
                    'title': 'Redirection Rules',
                    'countries': countries,
                    'cableoperators':cableoperators,
                    'rules':RULES
                }
                return render(request, 'cawas/redirectionrules/add.html', context)

        except CableOperator.DoesNotExist as e:
            return HttpResponse("No existe Cable Operador",None, 500)
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

                    rr = RedirectionRule.objects.get(id=json_data['redirectionrules']['redirectionrule_id'])
                    if (json_data['redirectionrules']['cableoperator'] is not None):
                        if json_data['redirectionrules']['cableoperator'] != '':
                            co_id = json_data['redirectionrules']['cableoperator']
                            co = CableOperator.objects.get(id=co_id)
                            rr.cableoperator = co

                    if (json_data['redirectionrules']['country'] is not None):
                        if (json_data['redirectionrules']['country'] > 0):
                            country_id = json_data['redirectionrules']['country']
                            country = Country.objects.get(id=country_id)
                            rr.country = country

                    if (json_data['redirectionrules']['rule'] is not None):
                        if (json_data['redirectionrules']['rule'] != ''):
                            rule_id = json_data['redirectionrules']['rule']
                            rr.rule = rule_id

                    rr.save()
                    mydata = [{'code': 200, 'message': 'Guardado Correctamente'}]
                    messages.add_message(request, messages.INFO, 'Guardado Correctamente')
                    return HttpResponse(json.dumps(mydata), None, 200)




            if request.method == 'GET':
                if not request.user.is_authenticated:
                    lc = LogController()
                    return redirect(lc.login_view(request))

                registro = RedirectionRule.objects.get(id=id)
                countries = Country.objects.all()
                cableoperators = CableOperator.objects.all()

                context = {
                           'registro':  registro,
                           'cableoperators':cableoperators,
                           'countries': countries,
                           'rules':     RULES
                           }
                return render(request, 'cawas/redirectionrules/edit.html', context)

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
            if request.method == 'GET':
                if not request.user.is_authenticated:
                    lc = LogController()
                    return redirect(lc.login_view(request))



            registros = RedirectionRule.objects.all()
            context = {'title': 'Listado Redirection Rules',
                       'registros': registros,
                       'rules': RULES
                       }
            return render(request, 'cawas/redirectionrules/list.html', context)

        except CableOperator.DoesNotExist as e:
            return HttpResponse("No existe Cable Operador",None, 500)
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
                    id = json_data['id']
                    print 'Id: ' + id
                    rr = RedirectionRule.objects.get(id=id)
                    rr.delete()

                    mydata = [{'code': 200, 'message': 'Guardado Correctamente'}]

                    return HttpResponse(json.dumps(mydata), None, 200)
                except RedirectionRule.DoesNotExist as e:
                    mydata = [{'code': 500, 'message': 'No existe el Registro'}]
                    return HttpResponse(json.dumps(mydata), None, 500)
                except Exception as e:
                    mydata = [{'code': 500, 'message': e.message}]
                    return HttpResponse(json.dumps(mydata), None, 500)


    @register.filter
    def get_item(dictionary, key):
        return dictionary.get(key)


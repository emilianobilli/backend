import os, datetime, json
from django.core.exceptions import *
from django.shortcuts import render, redirect
from LogController import LogController
from ..backend_sdk import ApiBackendServer, ApiBackendResource, ApiBackendException
from ..Helpers.GlobalValues import *
from ..Helpers.PublishHelper import PublishHelper
from ..models import Asset, Setting,  CableOperator, Language ,PublishZone, PublishQueue,Image, Country
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger





class CableOperatorController(object):
    #Atributos
    decjson=""
    code_return=0
    message_return=''
    #0 = ok, -1= error


    #respuestas, 0 = ok, 2= login
    def add(self, request):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))
        vgrabarypublicar = '0'
        # POST - Obtener datos del formulario y guardar la metadata
        if request.method == 'POST':
            # parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson.replace('\r','\\r').replace('\n','\\n'))
            vimg = Image()
            operator = CableOperator()
            try:
                pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
                print 'deb1'
                api_key = Setting.objects.get(code='backend_api_key')
                print 'deb2'
                co_url = Setting.objects.get(code='backend_co_url')
                print 'deb3'
                base_dir = Setting.objects.get(code='dam_base_dir')
                print 'deb4'
                zones = PublishZone.objects.filter(enabled=True)
                operator.name = decjson['cableoperator']['name']
                operator.phone = decjson['cableoperator']['phone']
                operator.site = decjson['cableoperator']['site']

                operator.country = Country.objects.get(id=decjson['cableoperator']['country_id'])
                vgrabarypublicar = decjson['cableoperator']['publicar']
                operator.save()
                vimg.name = operator.cableoperator_id
                if (request.FILES.has_key('ThumbHor')):
                    if request.FILES['ThumbHor'].name != '':
                        # TRATAMIENTO DE IMAGEN Landscape
                        vimg.landscape = request.FILES['ThumbHor']
                        extension = os.path.splitext(vimg.landscape.name)[1]
                        varchivo =  pathfilesland.value + vimg.name + extension
                        vimg.landscape.name = varchivo
                        varchivo_server = base_dir.value + varchivo
                        if os.path.isfile(varchivo_server):
                            os.remove(varchivo_server)
                vimg.save()
                operator.image = vimg
                operator.save()
                #Publicar en BKD
                co_id = operator.cableoperator_id
                for z in zones:
                    print 'deb5'
                    self.publish_cableoperator(co_id, co_url, api_key, z)
                    print 'deb6'

            except Setting.DoesNotExist as e:
                request.session['list_CableOperator_message'] = "Error al Guardar CableOperator. (" + str(e.message) + ")"
                request.session['list_CableOperator_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return
            except Exception as e:
                request.session['list_CableOperator_message'] = "Error al Guardar CableOperator. (" + str(e.message) + ")"
                request.session['list_CableOperator_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return


            # Eliminar cola de publicacion para el item en estado Queued
            ph = PublishHelper()
            try:
                ph = PublishHelper()
                ph.func_publish_image(request, vimg)
            except Exception as e:
                request.session['list_CableOperator_message'] = "Error al Guardar Imagen de Cable Operador. (" + str(e.message) + ")"
                request.session['list_CableOperator_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return


            request.session['list_CableOperator_message'] = 'Guardado Correctamente'
            request.session['list_CableOperator_flag'] = FLAG_SUCCESS
            #FIN DE POST

        if request.method =='GET':
            # Cargar variables para presentar en templates
            countries = Country.objects.all()
            operators = CableOperator.objects.all().order_by('id')
            context = {'countries':countries,'operators':operators}
            return render(request, 'cawas/cableoperators/add.html', context)




    #EDICION DE GIRL
    def edit(self, request, cableoperator_id):
        #AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        #VARIABLES PARA GET - CARGA OPERADOR
        try:
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            print 'deb1'
            api_key = Setting.objects.get(code='backend_api_key')
            print 'deb2'
            co_url = Setting.objects.get(code='backend_co_url')
            print 'deb3'
            base_dir = Setting.objects.get(code='dam_base_dir')
            print 'deb4'
            zones = PublishZone.objects.filter(enabled=True)
            operator = CableOperator.objects.get(cableoperator_id=cableoperator_id)
            # carga imagenes
            i = len(operator.image.landscape.name)
            imgland = operator.image.landscape.name[5:i]
            countries = Country.objects.all()

        #Nuevo diccionario para completar lenguages y metadata
        except Setting.DoesNotExist as e:
            request.session['list_CableOperator_message'] = "Error al Guardar Categoria. (" + e.message + ")"
            request.session['list_CableOperator_flag'] = FLAG_ALERT
            self.code_return = -1
            return self.code_return
        except CableOperator.DoesNotExist as e:
            request.session['list_CableOperator_message'] = "Error al Guardar Categoria. (" + e.message + ")"
            request.session['list_CableOperator_flag'] = FLAG_ALERT
            self.code_return = -1
            return self.code_return

        if request.method == 'POST':
            # Parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson.replace('\r','\\r').replace('\n','\\n'))
            operator.name = decjson['cableoperator']['name']
            operator.phone = decjson['cableoperator']['phone']
            operator.site = decjson['cableoperator']['site']

            # Leer GIRL desde AssetID
            try:
                operator = CableOperator.objects.get(cableoperator_id=cableoperator_id)
                vimg = operator.image
            except Asset.DoesNotExist as e:
                request.session['list_CableOperator_message'] = "Error al Guardar Categoria. (" + e.message + ")"
                request.session['list_CableOperator_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return
            except Image.DoesNotExist as e:
                vimg = Image()

            if (request.FILES.has_key('ThumbHor')):
                if request.FILES['ThumbHor'].name != '':
                    # TRATAMIENTO DE IMAGEN Landscape
                    vimg.landscape = request.FILES['ThumbHor']
                    extension = os.path.splitext(vimg.landscape.name)[1]
                    varchivo = pathfilesland.value + vimg.name + extension
                    vimg.landscape.name = varchivo
                    varchivo_server = base_dir.value + varchivo
                    if os.path.isfile(varchivo_server):
                        os.remove(varchivo_server)
                    vimg.save()
                    operator.image = vimg

            #Actualiza CableOperator
            operator.save()
            # Publicar en BKD
            co_id = operator.cableoperator_id
            for z in zones:
                self.publish_cableoperator(co_id, co_url, api_key, z)
            # Eliminar cola de publicacion para el item en estado Queued
            try:
                ph = PublishHelper()
                ph.func_publish_image(request, vimg)
            except Exception as e:
                request.session['list_CableOperator_message'] = "Error al Guardar Imagen de Cable Operador. (" + str(e.message) + ")"
                request.session['list_CableOperator_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return

            request.session['list_CableOperator_message'] = 'Guardado Correctamente'
            request.session['list_CableOperator_flag'] = FLAG_SUCCESS

        context = {'operator':operator, 'imgland':imgland, 'countries':countries,'imgland': imgland }
        # checks:
        return render(request, 'cawas/cableoperators/edit.html', context)




    def list(self, request):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        usuario = request.user
        message = ''
        flag = ''
        page = request.GET.get('page')
        request.POST.get('page')
        categories_list = None

        if request.session.has_key('list_CableOperator_message'):
            if request.session['list_CableOperator_message'] != '':
                message = request.session['list_CableOperator_message']
                request.session['list_CableOperator_message'] = ''

        if request.session.has_key('list_CableOperator_flag'):
            if request.session['list_CableOperator_flag'] != '':
                flag = request.session['list_CableOperator_flag']
                request.session['list_CableOperator_flag'] = ''

        if self.message_return !='':
            message = self.message_return
            self.message_return =''
            flag='success'

        operators = CableOperator.objects.all()
        if request.POST:
            titulo = request.POST['inputTitulo']
            selectestado = request.POST['selectestado']
            operators = CableOperator.objects.all()

            if request.POST:
                titulo = request.POST['inputTitulo']
                selectestado = request.POST['selectestado']
                if titulo != '':
                    operators = CableOperator.objects.filter(name__icontains=titulo)
                else:
                    operators = CableOperator.objects.all()


            paginator = Paginator(operators, 20)  # Show 25 contacts per page
            try:
                operators = paginator.page(page)
            except PageNotAnInteger:
                operators = paginator.page(1)
            except EmptyPage:
                operators = paginator.page(paginator.num_pages)

        context = {'message': message, 'flag':flag, 'registros':operators, 'usuario':usuario}
        return render(request, 'cawas/cableoperators/list.html', context)



    def unpublish(self, request, id):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        try:
            print 'debugmetadata'
            # si es la ultima categoria metadata, se debe eliminar la metadata y la categoria
            operator = CableOperator.objects.get(id=id)

            # 1 - VERIFICAR, si estado de publicacion esta en Q, se debe eliminar
            publishs = PublishQueue.objects.filter(item_id=operator.cableoperator_id, status='Q')
            if publishs.count > 0:
                publishs.delete()

            #Realizar delete al backend
            setting = Setting.objects.get(code='backend_CableOperator_url')
            api_key = Setting.objects.get(code='backend_api_key')
            vzones = PublishZone.objects.filter(enabled=True)
            for zone in vzones:
                abr = ApiBackendResource(zone.backend_url, setting.value, api_key.value)
                param = {"cableoperator_name": operator.name}
                abr.delete(param)

            #Actualizar Activated a False
            CableOperator.activated = False
            CableOperator.save()

            self.code_return = 0
            request.session['list_CableOperator_message'] = ' en ' + operator.name + ' de Categoria ' + operator.cableoperator_id + ' Despublicado Correctamente'
            request.session['list_CableOperator_flag'] = FLAG_SUCCESS

        except PublishZone.DoesNotExist as e:
            request.session['list_CableOperator_message'] = "PublishZone no Existe. (" + str(e.message) + ")"
            request.session['list_CableOperator_flag'] = FLAG_ALERT
            self.code_return = -1

        except ApiBackendException as e:
            request.session['list_CableOperator_message'] = "Error al despublicar (" + str(e.message) + ")"
            request.session['list_CableOperator_flag'] = FLAG_ALERT
            self.code_return = -1

        return self.code_return



    def publish(self, request, id):
        try:
            co = CableOperator.objects.get(id=id)
            co.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
            co.queue_status = 'Q'
            co.save()
            ph = PublishHelper()
            ph.func_publish_image(request, co.image)
            request.session['list_CableOperator_message'] = ' en ' + co.name + ' de Categoria ' + co.cableoperator_id + ' Guardado en Cola de Publicacion'
            request.session['list_CableOperator_flag'] = FLAG_SUCCESS
            self.code_return = 0

        except Exception as e:
            request.session['list_CableOperator_message'] = "Error al Publicar (" + str(e.message) + ")"
            request.session['list_CableOperator_flag'] = FLAG_ALERT
            self.code_return = -1
        return self.code_return



    def publish_cableoperator(self, co_id, co_url, apikey, publish_zone):
        co = self.cableoperator_serializer(co_id)
        endpoint = publish_zone.backend_url
        ep = ApiBackendResource(endpoint, co_url, apikey)
        try:
            print co
            ep.add(co)
            return 0, "success"
        except ApiBackendException as err:
            return -1, str(err.value)


    def cableoperator_serializer(self, co_id):
        try:
            co = CableOperator.objects.get(cableoperator_id=co_id)
        except ObjectDoesNotExist:
            msg = "Cable Operator with ID %s does not exist" % co_id
            raise SerializerException(msg)

        try:
            CDNURL = Setting.objects.get(code="image_cdn_landscape").value
        except:
            msg = "Setting with code image_cdn_landscape does not exist"
            raise SerializerException(msg)

        co_dict = co.toDict()
        co_dict['co_media_url'] = "%s%s" % (CDNURL, co_dict['co_media_url'])

        return co_dict


class SerializerException(Exception):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)

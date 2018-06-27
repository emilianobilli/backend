import os, datetime, json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from LogController import LogController
from ..backend_sdk import  ApiBackendServer, ApiBackendResource, ApiBackendException
from ..Helpers.GlobalValues import *
from ..Helpers.PublishHelper import PublishHelper
from ..models import Asset, Setting,  Category, Language ,PublishZone, PublishQueue,Image, CategoryMetadata
from django.db.models import Q

#ApiBackendResource, ApiBackendException,ApiBackendServer
class CategoryController(object):
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
            vcategory = Category()
            try:
                pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
                pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
                base_dir = Setting.objects.get(code='dam_base_dir')
                vcategory.original_name = decjson['Category']['original_name']
                vgrabarypublicar = decjson['Category']['publicar']
                vcategory.save()

                vimg.name = vcategory.category_id
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


                # IMAGEN Landscape
                if (request.FILES.has_key('ThumbVer')):
                    if request.FILES['ThumbVer'].name != '':
                        # Landscape
                        vimg.portrait = request.FILES['ThumbVer']
                        extension = os.path.splitext(vimg.portrait.name)[1]
                        varchivo = pathfilesport.value + vimg.name + extension
                        vimg.portrait.name = varchivo
                        # si existe archivo, lo borra
                        varchivo_server = base_dir.value + varchivo
                        if os.path.isfile(varchivo_server):
                            os.remove(varchivo_server)
                vimg.save()
                vcategory.image = vimg

                vcategory.save()

            except Setting.DoesNotExist as e:
                request.session['list_category_message'] = "Error al Guardar Category. (" + e.message + ")"
                request.session['list_category_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return
            except Exception as e:
                request.session['list_category_message'] = "Error al Guardar Category. (" + str(e.message) + ")"
                request.session['list_category_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return

            # Eliminar cola de publicacion para el item en estado Queued
            ph = PublishHelper()
            # CREAR METADATA
            vcategorymetadatas = decjson['Category']['Categorymetadatas']
            for item in vcategorymetadatas:
                vlanguage = Language.objects.get(code=item['Categorymetadata']['language'])
                # Luego del POST redirige a pagina principal
                try:
                    gmd = CategoryMetadata.objects.get(category=vcategory, language=vlanguage)
                except CategoryMetadata.DoesNotExist as e:
                    gmd = CategoryMetadata()

                if (item['Categorymetadata']['date'] is None):
                    vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                else:
                    vschedule_date = datetime.datetime.strptime(item['Categorymetadata']['date'], '%d-%m-%Y').strftime('%Y-%m-%d')

                gmd.language = vlanguage
                gmd.name = item['Categorymetadata']['name']
                gmd.category = vcategory
                gmd.save()

                #PUBLICAR METADATA
                if vgrabarypublicar == '1':
                    ph = PublishHelper()
                    ph.func_publish_image(request, vimg)
                    ph.func_publish_queue(request, gmd.category.category_id, gmd.language, 'CA', 'Q', vschedule_date)


            request.session['list_category_message'] = 'Guardado Correctamente'
            request.session['list_category_flag'] = FLAG_SUCCESS

            #FIN DE POST

        if request.method =='GET':
            # Cargar variables para presentar en templates
            vcategories = Category.objects.all().order_by('original_name')
            vlanguages = Language.objects.all()

            vtypecategory = {"pornstar": "Pornstar", "playmate": "Playmate"}
            context = { 'vcategories': vcategories, 'vlanguages': vlanguages,
                       'vtypecategory': vtypecategory
                       }
            return render(request, 'cawas/categories/add.html', context)




    #EDICION DE GIRL
    def edit(self, request, category_id):
        #AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))


        #VARIABLES PARA GET - CARGA CATEGORIA
        try:
            vlangmetadata = []
            pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            base_dir = Setting.objects.get(code='dam_base_dir')
            vcategory = Category.objects.get(category_id=category_id)
            vtypecategory = {"pornstar": "Pornstar", "playmate": "Playmate"}
            vlanguages = Language.objects.all()
            # carga imagenes
            print 'debug 1'
            i = len(vcategory.image.portrait.name)
            imgport = vcategory.image.portrait.name[5:i]
            i = len(vcategory.image.landscape.name)
            imgland = vcategory.image.landscape.name[5:i]
            #Nuevo diccionario para completar lenguages y metadata
            for itemlang in vlanguages:
                vcategorymetadata = None
                try:
                    vcategorymetadata = CategoryMetadata.objects.get(category=vcategory, language=itemlang)
                    vlangmetadata.append({'checked': True, 'code': itemlang.code, 'idioma':itemlang.name ,'name': vcategorymetadata.name, 'publish_date':vcategorymetadata.publish_date})
                except CategoryMetadata.DoesNotExist as a:
                    vlangmetadata.append({'checked': False, 'code': itemlang.code,'idioma':itemlang.name, 'name':'' , 'publish_date':'' })
        except Setting.DoesNotExist as e:
            request.session['list_category_message'] = "Error al Guardar Categoria. (" + e.message + ")"
            request.session['list_category_flag'] = FLAG_ALERT
            self.code_return = -1
            return self.code_return
        except Category.DoesNotExist as e:
            request.session['list_category_message'] = "Error al Guardar Categoria. (" + e.message + ")"
            request.session['list_category_flag'] = FLAG_ALERT
            self.code_return = -1
            return self.code_return
        except Asset.DoesNotExist as e:
            request.session['list_category_message'] = "Error al Guardar Categoria. (" + e.message + ")"
            request.session['list_category_flag'] = FLAG_ALERT
            self.code_return = -1
            return self.code_return
        except Category.DoesNotExist as e:
            request.session['list_category_message'] = "Error al Guardar Categoria. (" + e.message + ")"
            request.session['list_category_flag'] = FLAG_ALERT
            self.code_return = -1
            return self.code_return
        except CategoryMetadata.DoesNotExist as e:
            request.session['list_category_message'] = "Error al Guardar Categoria. (" + e.message + ")"
            request.session['list_category_flag'] = FLAG_ALERT
            self.code_return = -1
            return self.code_return




        if request.method == 'POST':
            #VARIABLES
            vasset = Asset()
            vcategory = Category()
            # Parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson.replace('\r','\\r').replace('\n','\\n'))
            try:
                print 'debug 2'
                vcategory = Category.objects.get(category_id=category_id)
                vimg      = Image.objects.get(name=vcategory.category_id)
            except Asset.DoesNotExist as e:
                request.session['list_category_message'] = "Error al Guardar Categoria. (" + e.message + ")"
                request.session['list_category_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return
            except CategoryMetadata.DoesNotExist as e:
                request.session['list_category_message'] = "Error al Guardar Categoria. (" + e.message + ")"
                request.session['list_category_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return
            except Image.DoesNotExist as e:
                vimg = Image()

            # IMAGEN Portrait
            vimg.name = vcategory.category_id
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

            # IMAGEN Landscape
            if (request.FILES.has_key('ThumbVer')):
                if request.FILES['ThumbVer'].name != '':
                    # Landscape
                    vimg.portrait = request.FILES['ThumbVer']
                    extension = os.path.splitext(vimg.portrait.name)[1]
                    varchivo = pathfilesport.value + vimg.name + extension
                    vimg.portrait.name = varchivo
                    # si existe archivo, lo borra
                    varchivo_server = base_dir.value + varchivo
                    if os.path.isfile(varchivo_server):
                        os.remove(varchivo_server)

            vimg.save()

            vcategory.original_name  = decjson['Category']['original_name']
            vcategory.image = vimg
            vcategory.save()
            print 'debug 3'

            # Eliminar cola de publicacion para el item en estado Queued
            ph = PublishHelper()
            vcategorymetadatas = decjson['Category']['Categorymetadatas']
            for item in vcategorymetadatas:
                vlanguage = Language.objects.get(code=item['Categorymetadata']['language'])
                #Solo se agrega la metadata nueva. No se modifica la existente.
                try:
                    gmd = CategoryMetadata.objects.get(category=vcategory, language=vlanguage)
                except CategoryMetadata.DoesNotExist as e:
                    gmd = CategoryMetadata()

                if (item['Categorymetadata']['date'] is None ):
                    vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                elif (item['Categorymetadata']['date'] == '' ):
                    vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                else:
                    vschedule_date = datetime.datetime.strptime(item['Categorymetadata']['date'],'%d-%m-%Y').strftime('%Y-%m-%d')

                gmd.language     = vlanguage
                gmd.name         = item['Categorymetadata']['name']
                print 'debug 4'
                gmd.category     = vcategory
                gmd.publish_date = vschedule_date
                gmd.queue_status = 'Q'
                gmd.save()

                ph.func_publish_queue(request, gmd.category.category_id, gmd.language, 'CA', 'Q', vschedule_date)
                ph.func_publish_image(request, vimg)

            request.session['list_category_message'] = 'Guardado Correctamente'
            request.session['list_category_flag'] = FLAG_SUCCESS

        context = { 'vlanguages': vlanguages,
                    'vcategory':vcategory,
                    'vtypecategory':vtypecategory,
                    'vlangmetadata':vlangmetadata,
                    'imgport':imgport,
                    'imgland':imgland,
                   }
        # checks:
        return render(request, 'cawas/categories/edit.html', context)




    def list(self, request):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        usuario = request.user
        message = ''
        flag = ''
        page = request.GET.get('page')
        request.POST.get('page')

        filter = False

        # Filtro de busqueda
        if request.GET.has_key('search'):
            search = request.GET.get('search')
            if search != '':
                filter = True
                registros = CategoryMetadata.objects.filter(Q(category__original_name__icontains=search) | Q(category__category_id__icontains=search)).order_by('-id')

        if filter == False:
            registros = CategoryMetadata.objects.all().order_by('-id')
            paginator = Paginator(registros, 25)
            page = request.GET.get('page')
            try:
                registros = paginator.page(page)
            except PageNotAnInteger:
                registros = paginator.page(1)
            except EmptyPage:
                registros = paginator.page(paginator.num_pages)

        if request.session.has_key('list_category_message'):
            if request.session['list_category_message'] != '':
                message = request.session['list_category_message']
                request.session['list_category_message'] = ''

        if request.session.has_key('list_category_flag'):
            if request.session['list_category_flag'] != '':
                flag = request.session['list_category_flag']
                request.session['list_category_flag'] = ''

        if self.message_return !='':
            message = self.message_return
            self.message_return =''
            flag='success'

        context = {'message': message, 'flag':flag, 'registros':registros, 'usuario':usuario}
        return render(request, 'cawas/categories/list.html', context)



    def unpublish(self, request, id):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        try:

            # si es la ultima categoria metadata, se debe eliminar la metadata y la categoria
            categorymetadata = CategoryMetadata.objects.get(id=id)
            c = categorymetadata.category
            borrarcategory = False
            if CategoryMetadata.objects.filter(category=c).count()==1:
                borrarcategory = True

            #print 'debug1metadata' + categorymetadata
            if not categorymetadata.activated:
                categorymetadata.delete()
                if borrarcategory==True:
                    c.delete()

                self.code_return = 0
                request.session['list_category_message'] = 'Categoria Eliminada Correctamente '
                request.session['list_category_flag'] = FLAG_SUCCESS
                return self.code_return

            # 1 - VERIFICAR, si estado de publicacion esta en Q, se debe eliminar
            publishs = PublishQueue.objects.filter(item_id=categorymetadata.category.category_id, status='Q')
            if publishs.count > 0:
                publishs.delete()

            #Realizar delete al backend
            setting = Setting.objects.get(code='backend_category_url')
            api_key = Setting.objects.get(code='backend_api_key')
            vzones = PublishZone.objects.filter(enabled=True)
            for zone in vzones:
                abr = ApiBackendResource(zone.backend_url, setting.value, api_key.value)
                param = {"category_name": categorymetadata.category.original_name,
                         "lang": categorymetadata.language.code}
                abr.delete(param)

            #Actualizar Activated a False
            categorymetadata.activated = False
            categorymetadata.save()

            self.code_return = 0
            request.session['list_category_message'] = 'Metadata en ' + categorymetadata.language.name + ' de Categoria ' + categorymetadata.category.category_id + ' Despublicado Correctamente'
            request.session['list_category_flag'] = FLAG_SUCCESS

        except PublishZone.DoesNotExist as e:
            request.session['list_category_message'] = "PublishZone no Existe. (" + str(e.message) + ")"
            request.session['list_category_flag'] = FLAG_ALERT
            self.code_return = -1
        except CategoryMetadata.DoesNotExist as e:
            request.session['list_category_message'] = "Metadata de Category no Existe. (" + str(e.message) + ")"
            request.session['list_category_flag'] = FLAG_ALERT
            self.code_return = -1
        except ApiBackendException as e:
            request.session['list_category_message'] = "Error al despublicar (" + str(e.message) + ")"
            request.session['list_category_flag'] = FLAG_ALERT
            self.code_return = -1

        return self.code_return



    def publish(self, request, id):
        try:
            gmd = CategoryMetadata.objects.get(id=id)

            gmd.queue_status = 'Q'
            gmd.save()
            ph = PublishHelper()
            ph.func_publish_queue(request, gmd.category.category_id, gmd.language, 'CA', 'Q', datetime.datetime.now().strftime('%Y-%m-%d'))
            ph.func_publish_image(request, gmd.category.image)
            request.session['list_category_message'] = 'Metadata en ' + gmd.language.name + ' de Categoria ' + gmd.category.category_id + ' Guardado en Cola de Publicacion'
            request.session['list_category_flag'] = FLAG_SUCCESS
            self.code_return = 0
        except CategoryMetadata.DoesNotExist as e:
            request.session['list_category_message'] = 'Error en Publicacion ' + str(e.message)
            request.session['list_category_flag'] = FLAG_ALERT
            self.code_return = -1

        return self.code_return



    def publish_all(self, request,param_category, param_lang ):
        #Publica nuevamente la Category para todos los idiomas

        mditems = CategoryMetadata.objects.filter(category=param_category, language=param_lang)
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        #Actualizar la fecha de publicacion
        for md in mditems:
            #md.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
            md.activated = True
            md.save()
            #Dejar en cola de publicacion para cada idioma
            ph = PublishHelper()
            ph.func_publish_queue(request, md.category.asset.asset_id, md.language, 'CA', 'Q', date_str)
            ph.func_publish_image(request, md.category.image)
            self.code_return = 0

        return self.code_return



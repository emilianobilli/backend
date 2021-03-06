
import os, datetime, json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from LogController import LogController
from ..backend_sdk import ApiBackendServer, ApiBackendResource, ApiBackendException
from ..Helpers.GlobalValues import *
from ..Helpers.PublishHelper import PublishHelper
from ..models import Asset, Setting, Movie,MovieMetadata, Girl,Country, GirlMetadata, Category, Language, Image,PublishZone, PublishQueue
from django.db.models import Q
from django.forms import model_to_dict

from urlparse import urlparse
import httplib2
import socket
from django.http import JsonResponse


#ApiBackendResource, ApiBackendException,ApiBackendServer
class GirlController(object):
    #Atributos
    decjson=""
    vimg=Image()
    vgirl=Girl()
    code_return=0
    message_return=''
    #0 = ok, -1= error


    #respuestas, 0 = ok, 2= login
    def add(self, request):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        flag = ''
        message = ''
        vimg = Image()
        vgrabarypublicar=''
        try:
            pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            base_dir = Setting.objects.get(code='dam_base_dir')
        except Setting.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})

        # POST - Obtener datos del formulario y guardar la metadata
        if request.method == 'POST':
            # parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson.replace('\r','\\r').replace('\n','\\n'))
            print 'debug1'
            # VARIABLES - (esta logica pasa al controlador)
            vgirl = Girl()
            vasset = Asset()
            vasset.asset_type = "girl"
            vasset.save()
            print 'debug2'
            #try:
            vimg.name = vasset.asset_id



            # IMAGEN Portrait
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
            print 'debug3'
            # CREAR GIRL
            vgirl.asset = vasset
            vgirl.name = decjson['Girl']['name']
            vgirl.type = decjson['Girl']['type_girl']
            vgrabarypublicar = decjson['Girl']['publicar']
            if (decjson['Girl']['birth_date'] is not None):
                vgirl.birth_date = datetime.datetime.strptime(decjson['Girl']['birth_date'], '%d-%m-%Y').strftime(
                    '%Y-%m-%d')
            else:
                vgirl.birth_date = datetime.datetime.now().strftime('%Y-%m-%d')

            vgirl.height = decjson['Girl']['height']
            vgirl.weight = decjson['Girl']['weight']
            vgirl.image = vimg
            print 'debug4'
            vgirl.save()

            # CARGAR Countries al Asset
            if (decjson['Girl']['countries'] is not None):
                countries = decjson['Girl']['countries']
                for item in countries:
                    try:
                        country = Country.objects.get(id=item['country_id'])
                        vgirl.asset.target_country.add(country)
                    except Country.DoesNotExist as e:
                        request.session['list_girl_message'] = "Error: No Existe Pais (" + str(e.message) + ")"
                        request.session['list_girl_flag'] = FLAG_ALERT
                        self.code_return = -1

            # CREAR METADATA
            print 'debug6'

            # Eliminar cola de publicacion para el item en estado Queued
            ph = PublishHelper()

            vgirlmetadatas = decjson['Girl']['Girlmetadatas']
            for item in vgirlmetadatas:
                vlanguage = Language.objects.get(code=item['Girlmetadata']['language'])
                # Luego del POST redirige a pagina principal
                try:
                    gmd = GirlMetadata.objects.get(girl=vgirl, language=vlanguage)
                except GirlMetadata.DoesNotExist as e:
                    gmd = GirlMetadata()

                #if (item['Girlmetadata']['schedule_date'] != ''):
                #    vschedule_date = datetime.datetime.strptime(item['Girlmetadata']['schedule_date'],'%d-%m-%Y').strftime('%Y-%m-%d')
                #else:
                vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')

                gmd.language = vlanguage
                gmd.description = item['Girlmetadata']['description']
                gmd.nationality = item['Girlmetadata']['nationality']
                #gmd.publish_date = vschedule_date
                gmd.girl = vgirl
                gmd.save()

                #PUBLICAR METADATA
                if vgrabarypublicar == '1':
                    try:
                        ph = PublishHelper()
                        ph.func_publish_image(request, vimg)
                        ph.func_publish_queue(request, gmd.girl.asset.asset_id, gmd.language, 'AS', 'Q', vschedule_date)
                        gmd.queue_status = 'Q'
                    except GirlMetadata.DoesNotExist as e:
                        request.session['list_girl_message'] = 'No existe GirlMetadata ' + e.message
                        request.session['list_girl_flag'] = FLAG_ALERT
                        return -1

            request.session['list_girl_message'] = 'Guardado Correctamente'
            request.session['list_girl_flag'] = FLAG_SUCCESS

            #FIN DE POST

        if request.method =='GET':
            # Cargar variables para presentar en templates
            vgirls = Girl.objects.all().order_by('name')
            vcategories = Category.objects.all().order_by('name')
            vlanguages = Language.objects.all()
            countries = Country.objects.all().order_by('name')

            vtypegirl = {"pornstar": "Pornstar", "playmate": "Playmate"}
            context = {'vgirls': vgirls, 'vcategories': vcategories, 'vlanguages': vlanguages,
                       'vtypegirl': vtypegirl, 'countries':countries
                       }
            return render(request, 'cawas/girls/add.html', context)




    #EDICION DE GIRL
    def edit(self, request, asset_id):
     #AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        #VARIABLES PARA GET - CARGAR GIRL
        try:
            message = ''
            flag = ''
            vlangmetadata = []
            pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            base_dir = Setting.objects.get(code='dam_base_dir')
            vasset = Asset.objects.get(asset_id=asset_id)
            vgirl = Girl.objects.get(asset=vasset)
            vtypegirl = {"pornstar": "Pornstar", "playmate": "Playmate"}
            vlanguages = Language.objects.all()
            # carga imagenes
            i = len(vgirl.image.portrait.name)
            imgport = vgirl.image.portrait.name[5:i]
            i = len(vgirl.image.landscape.name)
            imgland = vgirl.image.landscape.name[5:i]

            countries_selected = vgirl.asset.target_country.all().order_by('name')
            countries_notselected = Country.objects.exclude(id__in=countries_selected).order_by('name')

            #Nuevo diccionario para completar lenguages y metadata
            for itemlang in vlanguages:
                vgirlmetadata = None
                try:
                    vgirlmetadata = GirlMetadata.objects.get(girl=vgirl, language=itemlang)
                    vlangmetadata.append(
                        {'checked': True, 'code': itemlang.code, 'name': itemlang.name,
                         'description': vgirlmetadata.description,
                         'nationality': vgirlmetadata.nationality})
                except GirlMetadata.DoesNotExist as a:
                    vlangmetadata.append({'checked': False, 'code': itemlang.code, 'name': itemlang.name, 'description': '', 'nationality': ''})
        except Setting.DoesNotExist as e:
            request.session['list_girl_message'] = 'No existe Setting ' + e.message
            request.session['list_girl_flag'] = FLAG_ALERT
            return -1
        except Girl.DoesNotExist as e:
            request.session['list_girl_message'] = 'No existe Girl ' + e.message
            request.session['list_girl_flag'] = FLAG_ALERT
            return -1
        except Asset.DoesNotExist as e:
            request.session['list_girl_message'] = 'No existe Asset ' + e.message
            request.session['list_girl_flag'] = FLAG_ALERT
            return -1
        except Category.DoesNotExist as e:
            request.session['list_girl_message'] = 'No existe Categoria ' + e.message
            request.session['list_girl_flag'] = FLAG_ALERT
            return -1
        except GirlMetadata.DoesNotExist as e:
            request.session['list_girl_message'] = 'No existe Metadata de Categoria ' + e.message
            request.session['list_girl_flag'] = FLAG_ALERT
            return -1

        if request.method == 'POST':
            #VARIABLES
            vasset = Asset()
            vgirl = Girl()
            # Parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson.replace('\r','\\r').replace('\n','\\n'))
            #print 'idioma' + request.GET['HTTP_ACCEPT_LANGUAGE']
            # Leer GIRL desde AssetID
            try:
                vasset = Asset.objects.get(asset_id=decjson['Girl']['asset_id'])
                vgirl = Girl.objects.get(asset=vasset)
                #verificar imagen
                vimg = Image.objects.get(name=vasset.asset_id)

            except Asset.DoesNotExist as e:
                request.session['list_girl_message'] = 'No existe Asset ' + e.message
                request.session['list_girl_flag'] = FLAG_ALERT
                return -1
            except GirlMetadata.DoesNotExist as e:
                request.session['list_girl_message'] = 'No existe Girl Metadata ' + e.message
                request.session['list_girl_flag'] = FLAG_ALERT
                return -1
            except Image.DoesNotExist as e:
                vimg = Image()

            vimg.name = vasset.asset_id
            # IMAGEN Portrait
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
            # CARGAR Countries al Asset
            vgirl.asset.target_country = []
            if (decjson['Girl']['countries'] is not None):
                countries = decjson['Girl']['countries']
                for item in countries:
                    try:
                        country = Country.objects.get(id=item['country_id'])
                        vgirl.asset.target_country.add(country)
                    except Country.DoesNotExist as e:
                        request.session['list_girl_message'] = "Error: No Existe Pais (" + str(e.message) + ")"
                        request.session['list_girl_flag'] = FLAG_ALERT
                        self.code_return = -1

            #Actualiza Girl
            try:
                vgirl.name = decjson['Girl']['name']
                vgirl.type = decjson['Girl']['type_girl']
                vgirl.birth_date = datetime.datetime.strptime(decjson['Girl']['birth_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
                vgirl.height = decjson['Girl']['height']
                vgirl.weight = decjson['Girl']['weight']
                vgirl.image = vimg
                vgirl.save()
            except Exception as e:
                request.session['list_girl_message'] = 'Error al Guardar Chica ' + e.message
                request.session['list_girl_flag'] = FLAG_ALERT
                return -1


            # Eliminar cola de publicacion para el item en estado Queued
            ph = PublishHelper()

            #BORRAR Y CREAR METADATA
            vgirlmetadatas = decjson['Girl']['Girlmetadatas']
            for item in vgirlmetadatas:
                vlanguage = Language.objects.get(code=item['Girlmetadata']['language'])
                try:
                    gmd = GirlMetadata.objects.get(girl=vgirl, language=vlanguage)
                except GirlMetadata.DoesNotExist as e:
                    gmd = GirlMetadata()

                vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')

                gmd.language = vlanguage
                gmd.description = item['Girlmetadata']['description']
                gmd.nationality = item['Girlmetadata']['nationality']
                #gmd.publish_date = vschedule_date
                gmd.girl = vgirl
                gmd.queue_status = 'Q'
                gmd.save()

                # Publica en PublishQueue
                ph = PublishHelper()
                ph.func_publish_queue(request, vasset.asset_id, vlanguage, 'AS', 'Q', vschedule_date)
                # Publica en PublishImage
                ph.func_publish_image(request, vimg)

            flag = 'success'
            message = 'Guardado Correctamente.'
            request.session['list_girl_message'] = 'Guardado Correctamente'
            request.session['list_girl_flag'] = FLAG_SUCCESS

        context = { 'vlanguages': vlanguages, 'vgirl':vgirl,
                   'vtypegirl':vtypegirl,'vlangmetadata':vlangmetadata,
                   'imgport':imgport, 'imgland':imgland,
                   'flag':flag, 'message':message,
                   'countries_selected': countries_selected, 'countries_notselected': countries_notselected
                    }
        # checks:

        return render(request, 'cawas/girls/edit.html', context)




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
                registros = GirlMetadata.objects.filter(
                    Q(girl__name__icontains=search) | Q(girl__asset__asset_id__icontains=search)).order_by('-id')

        if filter == False:
            registros = GirlMetadata.objects.all().order_by('-id')
            paginator = Paginator(registros, 25)
            page = request.GET.get('page')
            try:
                registros = paginator.page(page)
            except PageNotAnInteger:
                registros = paginator.page(1)
            except EmptyPage:
                registros = paginator.page(paginator.num_pages)

        if request.session.has_key('list_girl_message'):
            if request.session['list_girl_message'] != '':
                message = request.session['list_girl_message']
                request.session['list_girl_message'] = ''

        if request.session.has_key('list_girl_flag'):
            if request.session['list_girl_flag'] != '':
                flag = request.session['list_girl_flag']
                request.session['list_girl_flag'] = ''

        if self.message_return !='':
            message = self.message_return
            self.message_return =''
            flag='success'

        context = {'message': message,'flag':flag, 'registros': registros,  'usuario': usuario}
        return render(request, 'cawas/girls/list.html', context)




    def unpublish(self, request, id):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        try:
            girlmetadata = GirlMetadata.objects.get(id=id)
            vasset_id = girlmetadata.girl.asset.asset_id

            # 1 - VERIFICAR, si estado de publicacion esta en Q, se debe eliminar
            publishs = PublishQueue.objects.filter(item_id=vasset_id, status='Q', item_lang=girlmetadata.language)
            if publishs.count > 0:
                publishs.delete()

            # Buscar todas Movies con esa chica
            girl = girlmetadata.girl
            movies = Movie.objects.filter(girls__in=[girl])
            for movie in movies:
                # Quitar la asocicacion de Chica-Movie
                movie.girls.remove(girl)
                movie.save()

                # Las movies modificadas, volver a publicarlas PublishQueue
                metadatas = MovieMetadata.objects.filter(movie=movie, activated=True)
                for metadata in metadatas:
                    ph = PublishHelper()
                    ph.func_publish_queue(request, movie.asset.asset_id, metadata.language, 'AS', 'Q', datetime.datetime.now().strftime('%Y-%m-%d'))
                    print 'asset_id Despublicacion: '+ movie.asset.asset_id

            #  Realizar delete al backend
            setting = Setting.objects.get(code='backend_asset_url')
            api_key = Setting.objects.get(code='backend_api_key')
            vzones = PublishZone.objects.filter(enabled=True)
            for zone in vzones:
                abr = ApiBackendResource(zone.backend_url, setting.value, api_key.value)
                param = {"asset_id": girlmetadata.girl.asset.asset_id,
                          "asset_type": "girl",
                          "lang": girlmetadata.language.code}
                #print 'param: ' + param
                abr.delete(param)

            #  Actualizar Activated a False
            girlmetadata.activated = False
            girlmetadata.save()


            self.code_return = 0
            request.session['list_girl_message'] = 'Metadata en ' + girlmetadata.language.name + ' de Chica ' + girlmetadata.girl.asset.asset_id + ' Despublicado Correctamente'
            request.session['list_girl_flag'] = FLAG_SUCCESS

        except PublishZone.DoesNotExist as e:
            request.session['list_girl_message'] = 'No existe PublishZone ' +e.message
            request.session['list_girl_flag'] = FLAG_ALERT
            return -1
        except GirlMetadata.DoesNotExist as e:
            request.session['list_girl_message'] = 'No existe Metadata de Chica ' + e.message
            request.session['list_girl_flag'] = FLAG_ALERT
            return -1
        except ApiBackendException as e:
            request.session['list_girl_message'] = 'Error al Despublicar ' + e.message
            request.session['list_girl_flag'] = FLAG_ALERT
            return -1

        return self.code_return






    def publish(self, request, id):

        gmd = GirlMetadata.objects.get(id=id)
        #gmd.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
        #gmd.activated = True
        gmd.queue_status = 'Q'
        gmd.save()
        ph = PublishHelper()
        #verifica si existe cola de publicacion en Q para el item, se borra

        ph.func_publish_queue(request, gmd.girl.asset.asset_id, gmd.language, 'AS', 'Q', datetime.datetime.now().strftime('%Y-%m-%d'))
        ph.func_publish_image(request, gmd.girl.image)
        request.session['list_girl_message'] = 'Metadata en ' + gmd.language.name + ' de Chica ' + gmd.girl.asset.asset_id + ' Guardado en Cola de Publicacion'
        request.session['list_girl_flag'] = FLAG_SUCCESS
        self.code_return = 0

        return self.code_return

    def publish_all(self, request,param_girl, param_lang ):
        #Publica nuevamente la Girl para todos los idiomas

        mditems = GirlMetadata.objects.filter(girl=param_girl, language=param_lang)
        #Actualizar la fecha de publicacion
        for md in mditems:

            #Dejar en cola de publicacion para cada idioma
            ph = PublishHelper()
            ph.func_publish_queue(request, md.girl.asset.asset_id, md.language, 'AS', 'Q', datetime.datetime.now().strftime('%Y-%m-%d'))
            ph.func_publish_image(request, md.girl.image)
            self.code_return = 0

        return self.code_return
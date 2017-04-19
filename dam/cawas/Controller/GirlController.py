
import os, datetime, json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from LogController import LogController
from backend_sdk import ApiBackendServer, ApiBackendResource
from ..Helpers.GlobalValues import *
from ..Helpers.PublishHelper import PublishHelper
from ..models import Asset, Setting, Movie,MovieMetadata, Girl, GirlMetadata, Category, Language, Image,PublishZone, PublishQueue


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
        except Setting.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})

        # POST - Obtener datos del formulario y guardar la metadata
        if request.method == 'POST':
            # parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)

            # VARIABLES - (esta logica pasa al controlador)
            vgirl = Girl()
            vasset = Asset()
            vasset.asset_type = "girl"
            vasset.save()

            try:
                vimg.name = vasset.asset_id
               # IMAGEN Portrait
                if (request.FILES.has_key('ThumbHor')):
                    if request.FILES['ThumbHor'].name != '':
                        vimg.portrait = request.FILES['ThumbHor']
                        extension = os.path.splitext(vimg.portrait.name)[1]
                        varchivo = pathfilesport.value  + vimg.name + extension
                        vimg.portrait.name = varchivo
                        if os.path.isfile(varchivo):
                            os.remove(varchivo)

                # IMAGEN Landscape
                if (request.FILES.has_key('ThumbVer')):
                    if request.FILES['ThumbVer'].name != '':
                        vimg.landscape = request.FILES['ThumbVer']
                        extension = os.path.splitext(vimg.landscape.name)[1]
                        varchivo = pathfilesland.value + vimg.name + extension
                        vimg.landscape.name = varchivo
                        if os.path.isfile(varchivo):
                            os.remove(varchivo)
                vimg.save()

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
                vgirl.save()
            except Exception as e:
                return render(request, 'cawas/error.html', {"message": "Error al Guardar Girl. (" + e.message + ")."})

            # CREAR METADATA
            vgirlmetadatas = decjson['Girl']['Girlmetadatas']
            for item in vgirlmetadatas:
                vlanguage = Language.objects.get(code=item['Girlmetadata']['language'])
                # Luego del POST redirige a pagina principal
                try:
                    gmd = GirlMetadata.objects.get(girl=vgirl, language=vlanguage)
                except GirlMetadata.DoesNotExist as e:
                    gmd = GirlMetadata()

                vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                gmd.language = vlanguage
                gmd.description = item['Girlmetadata']['description']
                gmd.nationality = item['Girlmetadata']['nationality']
                gmd.publish_date = vschedule_date
                gmd.girl = vgirl
                gmd.save()

            #PUBLICAR METADATA
            if vgrabarypublicar == '1':
                try:
                    ph = PublishHelper()
                    ph.func_publish_image(request, vimg)
                    metadatas = GirlMetadata.objects.filter(girl=vgirl)
                    for mdi in metadatas:
                        # Publica en PublishQueue
                        ph.func_publish_queue(request, mdi.girl.asset.asset_id, mdi.language, 'AS', 'Q', vschedule_date)
                except GirlMetadata.DoesNotExist as e:
                    return render(request, 'cawas/error.html',
                                  {"message": "No existe Metadata Para el Chica. (" + e.message + ")"})

            request.session['list_girl_message'] = 'Guardado Correctamente'
            request.session['list_girl_flag'] = FLAG_SUCCESS

            #FIN DE POST

        if request.method =='GET':
            # Cargar variables para presentar en templates
            vgirls = Girl.objects.all().order_by('name')
            vcategories = Category.objects.all().order_by('name')
            vlanguages = Language.objects.all()

            vtypegirl = {"pornstar": "Pornstar", "playmate": "Playmate"}
            context = {'vgirls': vgirls, 'vcategories': vcategories, 'vlanguages': vlanguages,
                       'vtypegirl': vtypegirl
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
            vasset = Asset.objects.get(asset_id=asset_id)
            vgirl = Girl.objects.get(asset=vasset)
            vtypegirl = {"pornstar": "Pornstar", "playmate": "Playmate"}
            vlanguages = Language.objects.all()
        # carga imagenes
            i = len(vgirl.image.portrait.name)
            imgport = vgirl.image.portrait.name[5:i]
            i = len(vgirl.image.landscape.name)
            imgland = vgirl.image.landscape.name[5:i]
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
            return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})
        except Girl.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Asset no se encuentra Vinculado a Girl. (" + e.message + ")"})
        except Asset.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Asset no Existe. (" + e.message + ")"})
        except Category.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Categoria no Existe. (" + e.message + ")"})
        except GirlMetadata.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "GirlMetaData No Existe . (" + e.message + ")"})


        if request.method == 'POST':
            #VARIABLES
            vasset = Asset()
            vgirl = Girl()
            # Parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)

            # Leer GIRL desde AssetID
            try:
                vasset = Asset.objects.get(asset_id=decjson['Girl']['asset_id'])
                vgirl = Girl.objects.get(asset=vasset)
                #verificar imagen
                vimg = Image.objects.get(name=vasset.asset_id)

            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "Asset no Existe. (" + e.message + ")"})
            except GirlMetadata.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "GirlMetaData No Existe . (" + e.message + ")"})
            except Image.DoesNotExist as e:
                vimg = Image()

            # IMAGEN Portrait
            if (request.FILES.has_key('ThumbHor')):
                if request.FILES['ThumbHor'].name != '':
                    vimg.portrait = request.FILES['ThumbHor']
                    extension = os.path.splitext(vimg.portrait.name)[1]
                    vimg.name = vasset.asset_id
                    varchivo = pathfilesport.value + vimg.name + extension
                    vimg.portrait.name = varchivo
                    if os.path.isfile(varchivo):
                        os.remove(varchivo)

            # IMAGEN Landscape
            if (request.FILES.has_key('ThumbVer')):
                if request.FILES['ThumbVer'].name != '':
                    vimg.landscape = request.FILES['ThumbVer']
                    extension = os.path.splitext(vimg.landscape.name)[1]
                    varchivo = pathfilesland.value + vimg.name + extension
                    vimg.landscape.name = varchivo
                    if os.path.isfile(varchivo):
                        os.remove(varchivo)

            vimg.save()

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
                return render(request, 'cawas/error.html', {"message": "Error al Guardar Girl. (" + str(e.message) + ")."})


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
                gmd.publish_date = vschedule_date
                gmd.girl = vgirl

                metadatas = GirlMetadata.objects.filter(girl=vgirl, language=vlanguage)
                # Si no existe METADATA, se genera
                if metadatas.count() < 1:
                    gmd.save()

                # Publica en PublishQueue
                ph = PublishHelper()
                ph.func_publish_queue(request, vasset.asset_id, vlanguage, 'AS', 'Q', vschedule_date)
                # Publica en PublishImage
                ph.func_publish_image(request, vimg)

            flag='success'
            message = 'Guardado Correctamente.'
            request.session['list_girl_message'] = 'Guardado Correctamente'
            request.session['list_girl_flag'] = FLAG_SUCCESS


        context = { 'vlanguages': vlanguages, 'vgirl':vgirl,
                   'vtypegirl':vtypegirl,'vlangmetadata':vlangmetadata,
                   'imgport':imgport, 'imgland':imgland,
                   'flag':flag,
                   'message':message}
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
        girls_list = None

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

        if request.POST:
            titulo = request.POST['inputTitulo']
            selectestado = request.POST['selectestado']

            #FILTROS
            if titulo != '':
                girls_sel = Girl.objects.filter(name__icontains=titulo)
            else:
                girls_sel = Girl.objects.all()

            if selectestado != '':
                girls_list = GirlMetadata.objects.filter(girl__in=girls_sel, publish_status=selectestado).order_by('girl_id')
            else:
                girls_list = GirlMetadata.objects.filter(girl__in=girls_sel).order_by('girl_id')


        if girls_list is None:
            girls_list = GirlMetadata.objects.all().order_by('girl_id')

        paginator = Paginator(girls_list, 20)  # Show 25 contacts per page
        try:
            girls = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            girls = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            girls = paginator.page(paginator.num_pages)

        context = {'message': message,'flag':flag, 'registros': girls,  'usuario': usuario}
        return render(request, 'cawas/girls/list.html', context)




    def unpublish(self, request, id):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        try:
            girlmetadata = GirlMetadata.objects.get(id=id)
            vasset_id = girlmetadata.girl.asset.asset_id

            # 1 - VERIFICAR, si estado de publicacion esta en Q, se debe eliminar
            publishs = PublishQueue.objects.filter(item_id=vasset_id, status='Q')
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
                metadatas = MovieMetadata.objects.filter(movie=movie)
                for metadata in metadatas:
                    ph = PublishHelper()
                    ph.func_publish_queue(request, movie.asset.asset_id, metadata.language, 'AS', 'Q', metadata.publish_date)
                    print 'asset_id Despublicacion: '+ movie.asset.asset_id

            #  Realizar delete al backend
            setting = Setting.objects.get(code='backend_asset_url')
            vzones = PublishZone.objects.filter(enabled=True)
            for zone in vzones:
                abr = ApiBackendResource(zone.backend_url, setting.value)
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
            return render(request, 'cawas/error.html', {"message": "PublishZone no Existe. (" + str(e.message) + ")"})
        except GirlMetadata.DoesNotExist as e:
            return render(request, 'cawas/error.html',
                          {"message": "Metadata de Girl no Existe. (" + str(e.message) + ")"})

        return self.code_return





    def publish(self, request, id):

        gmd = GirlMetadata.objects.get(id=id)
        gmd.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
        gmd.activated = True
        gmd.save()
        ph = PublishHelper()
        ph.func_publish_queue(request, gmd.girl.asset.asset_id, gmd.language, 'AS', 'Q', datetime.datetime.now().strftime('%Y-%m-%d'))
        ph.func_publish_image(request,gmd.girl.image)
        request.session['list_girl_message'] = 'Metadata en ' + gmd.language.name + ' de Chica ' + gmd.girl.asset.asset_id + ' Publicada Correctamente'
        request.session['list_girl_flag'] = FLAG_SUCCESS
        self.code_return = 0

        return self.code_return

    def publish_all(self, request,param_girl, param_lang ):
        #Publica nuevamente la Girl para todos los idiomas

        mditems = GirlMetadata.objects.filter(girl=param_girl, language=param_lang)
        #Actualizar la fecha de publicacion
        for md in mditems:
            md.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
            md.activated = True
            md.save()
            #Dejar en cola de publicacion para cada idioma
            ph = PublishHelper()
            ph.func_publish_queue(request, md.girl.asset.asset_id, md.language, 'AS', 'Q', md.publish_date)
            ph.func_publish_image(request, md.girl.image)
            self.code_return = 0

        return self.code_return

import os, datetime, json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from LogController import LogController
from backend_sdk import ApiBackendServer, ApiBackendResource
from ..Helpers.GlobalValues import *
from ..Helpers.PublishHelper import PublishHelper
from ..models import Asset, Setting,  Category, Language ,PublishZone, PublishQueue,Image, CategoryMetadata


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
            decjson = json.loads(strjson)
            vimg = Image()
            vcategory = Category()
            try:
                pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
                vcategory.original_name = decjson['Category']['original_name']
                #vgrabarypublicar = decjson['Category']['publicar']
                vcategory.save()
                if (request.FILES.has_key('ThumbHor')):
                    if request.FILES['ThumbHor'].name != '':
                        vimg.name = vcategory.category_id
                        vimg.landscape = request.FILES['ThumbHor']
                        extension = os.path.splitext(vimg.landscape.name)[1]
                        varchivo = pathfilesland.value + vimg.name + extension
                        vimg.landscape.name = varchivo
                        if os.path.isfile(varchivo):
                            os.remove(varchivo)
                        vimg.save()
                        vcategory.image = vimg
                        vcategory.save()
                        print 'debug1'
            except Setting.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})
            except Exception as e:
                return render(request, 'cawas/error.html', {"message": "Error al Guardar Category. (" + e.message + ")."})

            # CREAR METADATA
            vcategorymetadatas = decjson['Category']['Categorymetadatas']
            for item in vcategorymetadatas:
                vlanguage = Language.objects.get(code=item['Categorymetadata']['language'])
                # Luego del POST redirige a pagina principal
                try:
                    gmd = CategoryMetadata.objects.get(category=vcategory, language=vlanguage)
                except CategoryMetadata.DoesNotExist as e:
                    gmd = CategoryMetadata()
                vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                gmd.language = vlanguage
                gmd.name = item['Categorymetadata']['name']
                gmd.publish_date = vschedule_date
                gmd.category = vcategory
                gmd.save()

            #PUBLICAR METADATA
            if vgrabarypublicar == '1':
                try:
                    ph = PublishHelper()
                    ph.func_publish_image(request, vimg)
                    metadatas = CategoryMetadata.objects.filter(category=vcategory)
                    for mdi in metadatas:
                        # Publica en PublishQueue
                        ph.func_publish_queue(request, mdi.category.category_id, mdi.language, 'AS', 'Q', vschedule_date)
                except CategoryMetadata.DoesNotExist as e:
                    return render(request, 'cawas/error.html',
                                  {"message": "No existe Metadata de Categoria. (" + e.message + ")"})

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


        #VARIABLES PARA GET - CARGAR GIRL
        try:
            message = ''
            flag = ''
            vlangmetadata = []
            pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            #vasset = Asset.objects.get(asset_id=asset_id)
            vcategory = Category.objects.get(category_id=category_id)
            vtypecategory = {"pornstar": "Pornstar", "playmate": "Playmate"}
            vlanguages = Language.objects.all()
        # carga imagenes
            i = len(vcategory.image.portrait.name)
            imgport = vcategory.image.portrait.name[5:i]
            i = len(vcategory.image.landscape.name)
            imgland = vcategory.image.landscape.name[5:i]
        #Nuevo diccionario para completar lenguages y metadata
            for itemlang in vlanguages:
                vcategorymetadata = None
                try:
                    vcategorymetadata = CategoryMetadata.objects.get(category=vcategory, language=itemlang)
                    vlangmetadata.append(
                        {'checked': True, 'code': itemlang.code, 'idioma':itemlang.name ,'name': vcategorymetadata.name, 'publish_date':vcategorymetadata.publish_date})
                except CategoryMetadata.DoesNotExist as a:
                    vlangmetadata.append({'checked': False, 'code': itemlang.code,'idioma':itemlang.name, 'name':'' , 'publish_date':'' })
        except Setting.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})
        except Category.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Asset no se encuentra Vinculado a Category. (" + e.message + ")"})
        except Asset.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Asset no Existe. (" + e.message + ")"})
        except Category.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Categoria no Existe. (" + e.message + ")"})
        except CategoryMetadata.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "CategoryMetaData No Existe . (" + e.message + ")"})


        if request.method == 'POST':
            #VARIABLES
            vasset = Asset()
            vcategory = Category()
            # Parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)

            # Leer GIRL desde AssetID
            try:
                vcategory = Category.objects.get(category_id=category_id)
                vimg = Image.objects.get(name=vcategory.category_id)

            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "Asset no Existe. (" + e.message + ")"})
            except CategoryMetadata.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "CategoryMetaData No Existe . (" + e.message + ")"})
            except Image.DoesNotExist as e:
                vimg = Image()

            # IMAGEN Portrait
            vimg.name = vcategory.category_id

            if (request.FILES.has_key('ThumbHor')):
                if request.FILES['ThumbHor'].name != '':
                    vimg.landscape = request.FILES['ThumbHor']
                    extension = os.path.splitext(vimg.landscape.name)[1]
                    varchivo = pathfilesland.value + vimg.name + extension
                    vimg.landscape.name = varchivo
                    if os.path.isfile(varchivo):
                        os.remove(varchivo)

            # IMAGEN Landscape
            if (request.FILES.has_key('ThumbVer')):
                if request.FILES['ThumbVer'].name != '':
                    vimg.portrait = request.FILES['ThumbVer']
                    extension = os.path.splitext(vimg.portrait.name)[1]
                    varchivo = pathfilesport.value + vimg.name + extension
                    vimg.portrait.name = varchivo
                    if os.path.isfile(varchivo):
                        os.remove(varchivo)

            vimg.save()

            #Actualiza Category
            try:
                vcategory.name = decjson['Category']['name']
                vcategory.image = vimg
                vcategory.save()
            except Exception as e:
                return render(request, 'cawas/error.html', {"message": "Error al Guardar Category. (" + str(e.message) + ")."})


            #BORRAR Y CREAR METADATA
            vcategorymetadatas = decjson['Category']['Categorymetadatas']
            for item in vcategorymetadatas:
                vlanguage = Language.objects.get(code=item['Categorymetadata']['language'])
                try:
                    gmd = CategoryMetadata.objects.get(category=vcategory, language=vlanguage)
                except CategoryMetadata.DoesNotExist as e:
                    gmd = CategoryMetadata()

                vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                gmd.language = vlanguage
                gmd.name = item['Categorymetadata']['name']
                gmd.publish_date = vschedule_date
                gmd.category = vcategory

                metadatas = CategoryMetadata.objects.filter(category=vcategory, language=vlanguage)
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
            request.session['list_category_message'] = 'Guardado Correctamente'
            request.session['list_category_flag'] = FLAG_SUCCESS


        context = { 'vlanguages': vlanguages, 'vcategory':vcategory,
                   'vtypecategory':vtypecategory,'vlangmetadata':vlangmetadata,
                   'imgport':imgport, 'imgland':imgland,
                   'flag':flag,
                   'message':message}
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
        categories_list = None

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

        if request.POST:
            titulo = request.POST['inputTitulo']
            selectestado = request.POST['selectestado']

            #FILTROS
            if titulo != '':
                categories_sel = Category.objects.filter(original_name__icontains=titulo).order_by('oringinal_name')
            else:
                categories_sel = Category.objects.all().order_by('oringinal_name')

            if selectestado != '':
                categories_list = CategoryMetadata.objects.filter(category__in=categories_sel, publish_status=selectestado).order_by('category_id')
            else:
                categories_list = CategoryMetadata.objects.filter(category__in=categories_sel).order_by('category_id')


        if categories_list is None:
            categories_list = CategoryMetadata.objects.all()

        paginator = Paginator(categories_list, 20)  # Show 25 contacts per page
        try:
            categories = paginator.page(page)
        except PageNotAnInteger:
            categories = paginator.page(1)
        except EmptyPage:
            categories = paginator.page(paginator.num_pages)

        context = {'message': message, 'flag':flag, 'registros':categories, 'usuario':usuario}
        return render(request, 'cawas/categories/list.html', context)




    def unpublish(self, request, id):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        try:
            categorymetadata = CategoryMetadata.objects.get(id=id)
            vasset_id = categorymetadata.category.asset.asset_id

            # 1 - VERIFICAR, si estado de publicacion esta en Q, se debe eliminar
            publishs = PublishQueue.objects.filter(item_id=vasset_id, status='Q')
            if publishs.count > 0:
                publishs.delete()

            # Buscar todas Movies con esa chica
            category = categorymetadata.category
            movies = Category.objects.filter(categorys__in=[category])
            for movie in movies:
                # Quitar la asocicacion de Chica-Movie
                movie.categorys.remove(category)
                movie.save()

                # Las movies modificadas, volver a publicarlas PublishQueue
                metadatas = CategoryMetadata.objects.filter(movie=movie)
                for metadata in metadatas:
                    ph = PublishHelper()
                    ph.func_publish_queue(request, movie.asset.asset_id, metadata.language, 'AS', 'Q', metadata.publish_date)
                    print 'asset_id Despublicacion: '+ movie.asset.asset_id

            #  Realizar delete al backend
            setting = Setting.objects.get(code='backend_asset_url')
            vzones = PublishZone.objects.filter(enabled=True)
            for zone in vzones:
                abr = ApiBackendResource(zone.backend_url, setting.value)
                param = {"asset_id": categorymetadata.category.asset.asset_id,
                          "asset_type": "category",
                          "lang": categorymetadata.language.code}
                #print 'param: ' + param
                abr.delete(param)

            #  Actualizar Activated a False
            categorymetadata.activated = False
            categorymetadata.save()


            self.code_return = 0
            request.session['list_category_message'] = 'Metadata en ' + categorymetadata.language.name + ' de Chica ' + categorymetadata.category.asset.asset_id + ' Despublicado Correctamente'
            request.session['list_category_flag'] = FLAG_SUCCESS

        except PublishZone.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "PublishZone no Existe. (" + str(e.message) + ")"})
        except CategoryMetadata.DoesNotExist as e:
            return render(request, 'cawas/error.html',
                          {"message": "Metadata de Category no Existe. (" + str(e.message) + ")"})

        return self.code_return





    def publish(self, request, id):

        gmd = CategoryMetadata.objects.get(id=id)
        gmd.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
        gmd.activated = True
        gmd.save()
        ph = PublishHelper()
        ph.func_publish_queue(request, gmd.category.asset.asset_id, gmd.language, 'AS', 'Q', datetime.datetime.now().strftime('%Y-%m-%d'))
        ph.func_publish_image(request,gmd.category.image)
        request.session['list_category_message'] = 'Metadata en ' + gmd.language.name + ' de Chica ' + gmd.category.asset.asset_id + ' Publicada Correctamente'
        request.session['list_category_flag'] = FLAG_SUCCESS
        self.code_return = 0

        return self.code_return

    def publish_all(self, request,param_category, param_lang ):
        #Publica nuevamente la Category para todos los idiomas

        mditems = CategoryMetadata.objects.filter(category=param_category, language=param_lang)
        #Actualizar la fecha de publicacion
        for md in mditems:
            md.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
            md.activated = True
            md.save()
            #Dejar en cola de publicacion para cada idioma
            ph = PublishHelper()
            ph.func_publish_queue(request, md.category.asset.asset_id, md.language, 'AS', 'Q', md.publish_date)
            ph.func_publish_image(request, md.category.image)
            self.code_return = 0

        return self.code_return
import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import Asset, Setting, Movie, MovieMetadata, MovieMetadata, Category, Language, Image, Girl, PublishZone, Channel, PublishQueue, ImageQueue
from ..Helpers.PublishHelper import PublishHelper
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..Helpers.GlobalValues import *
from ..backend_sdk import ApiBackendServer, ApiBackendResource, ApiBackendException
from django.db.models import Q


class MovieController(object):




    def add(self, request):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))
        # return redirect(login_view)
        # ALTA - MOVIE: en el GET debe cargar variables, y en POST debe leer JSON
        # cawas/static/images/landscape/  cawas/static/images/portrait/

        vflag = ''
        message = ''
        vgrabarypublicar=''
        ph = PublishHelper()
        pathfilesport= ''
        pathfilesland = ''
        if request.method == 'POST':

            # parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)
            vgrabarypublicar = decjson['Movie']['publicar']

            # DECLARACION DE OBJECTOS
            mv = Movie()
            vasset = Asset()

            # CARGAR MOVIE
            try:
                vasset = Asset.objects.get(asset_id=decjson['Movie']['asset_id'])
            except Asset.DoesNotExist as e:
                request.session['list_movie_message'] = "Error: No existe asset (" + str(e.message) + ")"
                request.session['list_movie_flag'] = FLAG_ALERT
                self.code_return = -1

            #obtiene las variables
            try:
                pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
                pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            except Setting.DoesNotExist as e:
                request.session['list_movie_message'] = "Error: No existe Setting (" + str(e.message) + ")"
                request.session['list_movie_flag'] = FLAG_ALERT
                self.code_return = -1

            # VALIDAR IMAGEN
            try:
                img = Image.objects.get(name=vasset.asset_id)
            except Image.DoesNotExist as e:
                vflag = "error"
                img = Image()

            # TRATAMIENTO DE IMAGEN Portrait
            img.portrait = request.FILES['ThumbHor']
            extension = os.path.splitext(img.portrait.name)[1]
            img.name = vasset.asset_id
            varchivo = pathfilesport.value + img.name + extension
            img.portrait.name = varchivo

            if os.path.isfile(varchivo):
                os.remove(varchivo)

            # Landscape
            img.landscape = request.FILES['ThumbVer']
            extension = os.path.splitext(img.landscape.name)[1]
            varchivo = pathfilesland.value + img.name + extension
            img.landscape.name = varchivo
            # si existe archivo, lo borra
            if os.path.isfile(varchivo):
                os.remove(varchivo)

            img.save()
            mv.image = img

            # Channel
            try:
                vchannel = Channel.objects.get(pk=decjson['Movie']['channel_id'])
            except Asset.DoesNotExist as e:
                request.session['list_movie_message'] = "Error: No existe Canal (" + str(e.message) + ")"
                request.session['list_movie_flag'] = FLAG_ALERT
                self.code_return = -1

            mv.asset = vasset
            mv.channel = vchannel
            mv.original_title = decjson['Movie']['original_title']

            if (decjson['Movie']['year'] is not None):
                mv.year = decjson['Movie']['year']
            if (decjson['Movie']['cast'] is not None):
                mv.cast = decjson['Movie']['cast']
            if (decjson['Movie']['directors'] is not None):
                mv.cast = decjson['Movie']['directors']

            mv.display_runtime = decjson['Movie']['display_runtime']
            mv.save()

            # CARGAR GIRLS
            if (decjson['Movie']['girls'] is not None):
                vgirls = decjson['Movie']['girls']
                for item in vgirls:
                    try:
                        vgirl = Girl.objects.get(pk=item['girl_id'])
                        mv.girls.add(vgirl)
                    except Girl.DoesNotExist as e:
                        request.session['list_movie_message'] = "Error: No existe Chica (" + str(e.message) + ")"
                        request.session['list_movie_flag'] = FLAG_ALERT
                        self.code_return = -1

            # CARGAR CATEGORIES
            vcategories = decjson['Movie']['categories']
            for item in vcategories:
                try:
                    vcategory = Category.objects.get(pk=item['category_id'])
                    mv.category.add(vcategory)
                except Category.DoesNotExist as e:
                    vflag = "error"
                    request.session['list_movie_message'] = "Error: No existe Categoria (" + str(e.message) + ")"
                    request.session['list_movie_flag'] = FLAG_ALERT
                    self.code_return = -1

            # ACTUALIZAR EL ASSET A MOVIE
            vasset.asset_type = "movie"
            vasset.save()

            # GUARDAR METADATA
            vmoviesmetadata = decjson['Movie']['Moviesmetadata']

            for item in vmoviesmetadata:
                try:
                    # CREAR METADATA POR IDIOMA
                    vlanguage = Language.objects.get(code=item['Moviemetadata']['language'])
                    #si no esta cargada la fecha, se guarda con la fecha de hoy
                    if (item['Moviemetadata']['schedule_date'] != ''):
                        vpublishdate = datetime.datetime.strptime(item['Moviemetadata']['schedule_date'],'%d-%m-%Y').strftime('%Y-%m-%d')
                    else:
                        vpublishdate = datetime.datetime.now().strftime('%Y-%m-%d')

                    try:
                        mmd = MovieMetadata.objects.get(movie=mv, language=vlanguage)
                    except MovieMetadata.DoesNotExist as e:
                        mmd = MovieMetadata();

                    mmd.language = vlanguage
                    mmd.title = item['Moviemetadata']['title']
                    mmd.summary_short = item['Moviemetadata']['summary_short']
                    mmd.summary_long = item['Moviemetadata']['summary_long']
                    mmd.publish_date = vpublishdate
                    mmd.movie = mv

                    #Si no existe METADATA, se GENERA
                    metadatas = MovieMetadata.objects.filter(movie=mv, language=mmd.language)
                    if metadatas.count() < 1:
                        mmd.save()

                except Language.DoesNotExist as e:
                    self.code_return = -1
                    request.session['list_category_message'] = 'Error ' + e.message
                    request.session['list_category_flag'] = FLAG_ALERT
                    return self.code_return

                except Exception as e:
                    self.code_return = -1
                    request.session['list_category_message'] = 'Error ' + e.message
                    request.session['list_category_flag'] = FLAG_ALERT
                    return self.code_return



            # PUBLICAR METADATA
            if vgrabarypublicar == '1':
                metadatas = MovieMetadata.objects.filter(movie=mv)
                for mdi in metadatas:
                    if ph.func_publish_queue(request, mdi.movie.asset.asset_id, mdi.language, 'AS', 'Q', mdi.publish_date) == RETURN_ERROR:
                        request.session['list_movie_message'] = 'Error' + request.session['message']
                        request.session['list_movie_flag'] = FLAG_ALERT
                        return RETURN_ERROR

            # PUBLICAR METADATA IMAGEN
            if vgrabarypublicar == '1':
                if ph.func_publish_image(request, img) == RETURN_ERROR:
                    request.session['list_movie_message'] = 'Error' + request.session['message']
                    request.session['list_movie_flag'] = FLAG_ALERT
                    return RETURN_ERROR

            request.session['list_movie_message'] = 'Guardado Correctamente'
            request.session['list_movie_flag'] = FLAG_SUCCESS
            vflag = "success"
            message = 'Registrado correctamente'
            # FIN DE POST

        # VARIABLES PARA GET
        # CARGAR VARIABLES USADAS EN FRONT
        assets = Asset.objects.filter(asset_type="unknown")
        vmovies = Movie.objects.all().order_by('original_title')
        channels = Channel.objects.all().order_by('name')
        girls = Girl.objects.all().order_by('name')
        categories = Category.objects.all().order_by('original_name')
        vlanguages = Language.objects.all()
        title = 'Nueva Movie'
        context = {'title': title, 'assets': assets, 'channels': channels, 'girls': girls, 'categories': categories,
                   'movies': vmovies, 'vlanguages': vlanguages, 'flag': vflag, 'message': message}
        return render(request, 'cawas/movies/add.html', context)





    def edit(self, request, asset_id):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))
        # EDIT - MOVIE: en el GET debe cargar variables, y en POST debe leer JSON
        vlangmetadata = []
        flag=''
        message= ''
        pathfilesport = ''
        pathfilesland = ''

        try:
            pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
        except Setting.DoesNotExist as e:
            request.session['list_movie_message'] = "Error: No existe Setting (" + str(e.message) + ")"
            request.session['list_movie_flag'] = FLAG_ALERT
            self.code_return = -1

        # Post Movie - Graba datos
        if request.method == 'POST':
            # parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)

            # DECLARACION DE OBJECTOS
            mv = Movie()
            vasset = Asset()

            # Leer Movie desde AssetID
            # CARGAR MOVIE
            try:
                vasset = Asset.objects.get(asset_id=asset_id)
                mv = Movie.objects.get(asset=vasset)
                img = Image.objects.get(name=vasset.asset_id)

                vchannel = Channel.objects.get(pk=decjson['Movie']['channel_id'])
            except Asset.DoesNotExist as e:
                request.session['list_movie_message'] = "Error: No existe Asset (" + str(e.message) + ")"
                request.session['list_movie_flag'] = FLAG_ALERT
                self.code_return = -1
            except Movie.DoesNotExist as e:
                request.session['list_movie_message'] = "Error: No existe Movie asociada al Asset (" + str(e.message) + ")"
                request.session['list_movie_flag'] = FLAG_ALERT
                self.code_return = -1

            except Image.DoesNotExist as e:
                img = Image()
            except Asset.DoesNotExist as e:
                request.session['list_movie_message'] = "Error: No existe Asset (" + str(e.message) + ")"
                request.session['list_movie_flag'] = FLAG_ALERT
                self.code_return = -1

            # IMAGEN Portrait
            if (request.FILES.has_key('ThumbHor')):
                if request.FILES['ThumbHor'].name != '':
                    img.portrait = request.FILES['ThumbHor']
                    extension = os.path.splitext(img.portrait.name)[1]
                    img.name = vasset.asset_id
                    varchivo = pathfilesport.value + img.name + extension
                    img.portrait.name = varchivo
                    if os.path.isfile(varchivo):
                        os.remove(varchivo)

            # IMAGEN Landscape
            if (request.FILES.has_key('ThumbVer')):
                if request.FILES['ThumbVer'].name != '':
                    img.landscape = request.FILES['ThumbVer']
                    extension = os.path.splitext(img.landscape.name)[1]
                    varchivo = pathfilesland.value + img.name + extension
                    img.landscape.name = varchivo
                    if os.path.isfile(varchivo):
                        os.remove(varchivo)

            img.save()
            mv.image = img
            mv.asset = vasset
            mv.channel = vchannel
            mv.original_title = decjson['Movie']['original_title']

            if (decjson['Movie']['year'] is not None):
                mv.year = decjson['Movie']['year']
            if (decjson['Movie']['cast'] is not None):
                mv.cast = decjson['Movie']['cast']
            if (decjson['Movie']['directors'] is not None):
                mv.directors = decjson['Movie']['directors']

            mv.display_runtime = decjson['Movie']['display_runtime']
            # calcular runtime
            # mv.runtime

            # CARGAR GIRLS
            mv.girls = []
            mv.save()
            if (decjson['Movie']['girls'] is not None):
                vgirls = decjson['Movie']['girls']
                for item in vgirls:
                    try:
                        vgirl = Girl.objects.get(id=item['girl_id'])
                        mv.girls.add(vgirl)
                    except Girl.DoesNotExist as e:
                        request.session['list_movie_message'] = "Error: No existe Girl (" + str(e.message) + ")"
                        request.session['list_movie_flag'] = FLAG_ALERT
                        self.code_return = -1
                mv.save()
            print 'debug1'
            # CARGAR CATEGORIES
            vcategories = decjson['Movie']['categories']
            mv.category = []
            mv.save()
            for item in vcategories:
                try:
                    vcategory = Category.objects.get(id=item['category_id'])
                    mv.category.add(vcategory)
                except Category.DoesNotExist as e:
                    request.session['list_movie_message'] = "Error: No existe Categoria (" + str(e.message) + ")"
                    request.session['list_movie_flag'] = FLAG_ALERT
                    self.code_return = -1
            mv.save()
            # ACTUALIZAR EL ASSET A MOVIE
            # CARGAR METADATA
            vmoviesmetadata = decjson['Movie']['Moviesmetadata']
            # eliminar las movies metadata existentes

            mv.save()
            for item in vmoviesmetadata:
                vlanguage = Language.objects.get(code=item['Moviemetadata']['language'])
                try:
                    mmd = MovieMetadata.objects.get(movie=mv, language=vlanguage)
                    print 'encontrado'
                except MovieMetadata.DoesNotExist as e:
                    mmd = MovieMetadata()
                    print 'no lo encontro'

                try:
                    # CREAR METADATA POR IDIOMA
                    if (item['Moviemetadata']['schedule_date'] != ''):
                        vpublishdate = datetime.datetime.strptime(item['Moviemetadata']['schedule_date'],'%d-%m-%Y').strftime('%Y-%m-%d')
                    else:
                        vpublishdate = datetime.datetime.now().strftime('%Y-%m-%d')

                    mmd.language = vlanguage
                    mmd.movie = mv
                    mmd.title = item['Moviemetadata']['title']
                    mmd.summary_short = item['Moviemetadata']['summary_short']
                    mmd.summary_long = item['Moviemetadata']['summary_long']
                    mmd.publish_date = vpublishdate
                    mmd.save()
                    # Si no existe METADATA, se GENERA

                    # CREAR COLA DE PUBLICACION
                    ph = PublishHelper()
                    ph.func_publish_queue(request, mmd.movie.asset.asset_id, mmd.language, 'AS', 'Q', vpublishdate)
                except Language.DoesNotExist as e:
                    request.session['list_movie_message'] = "Error: No existe Lenguaje (" + str(e.message) + ")"
                    request.session['list_movie_flag'] = FLAG_ALERT
                    self.code_return = -1
                except Exception as e:
                    request.session['list_movie_message'] = "Error: al Guardar (" + str(e.message) + ")"
                    request.session['list_movie_flag'] = FLAG_ALERT
                    self.code_return = -1

            mv.save()
            # COLA DE PUBLICACION PARA IMAGENES
            try:
                ph = PublishHelper()
                ph.func_publish_image(request, img)
            except Exception as e:
                request.session['list_movie_message'] = "Error al generar cola de imagen (" + str(e.message) + ")"
                request.session['list_movie_flag'] = FLAG_ALERT
                self.code_return = -1

            request.session['list_movie_message'] = 'Guardado Correctamente'
            request.session['list_movie_flag'] = FLAG_SUCCESS
            vflag = "success"
            message = 'Registrado correctamente'


        # VARIABLES PARA GET - CARGAR MOVIE
        try:
            vasset = Asset.objects.get(asset_id=asset_id)
            vmovie = Movie.objects.get(asset=vasset)

            i = len(vmovie.image.portrait.name)
            imgport = vmovie.image.portrait.name[5:i]

            i = len(vmovie.image.landscape.name)
            imgland = vmovie.image.landscape.name[5:i]

            vgirlselected = vmovie.girls.all().order_by('name')
            vgirlnotselected = Girl.objects.exclude(id__in=vgirlselected).order_by('name')

            vmoviemetadata = MovieMetadata.objects.filter(movie=vmovie)
            vcategoryselected = vmovie.category.all().order_by('original_name')
            vcategorynotselected = Category.objects.exclude(id__in=vcategoryselected).order_by('original_name')
            languages = Language.objects.all()

            # nuevo diccionario para completar lenguages y metadata
            for itemlang in languages:
                vmoviemetadata = None
                try:
                    vmoviemetadata = MovieMetadata.objects.get(movie=vmovie, language=itemlang)
                    vlangmetadata.append(
                        {'checked': True, 'code': itemlang.code, 'name': itemlang.name, 'title': vmoviemetadata.title,
                         'summary_short': vmoviemetadata.summary_short, 'summary_long': vmoviemetadata.summary_long,
                         'publish_date': vmoviemetadata.publish_date})
                except MovieMetadata.DoesNotExist as a:
                    vlangmetadata.append({'checked': False, 'code': itemlang.code, 'name': itemlang.name, 'titulo': '',
                                          'descripcion': '', 'fechapub': ''})

        except Movie.DoesNotExist as e:
            request.session['list_movie_message'] = "Asset no se encuentra Vinculado a Movie. (" + e.message + ")"
            request.session['list_movie_flag'] = FLAG_ALERT
            self.code_return = -1

        except Asset.DoesNotExist as e:
            request.session['list_movie_message'] = "Error: No existe Asset. (" + e.message + ")"
            request.session['list_movie_flag'] = FLAG_ALERT
            self.code_return = -1

        except Category.DoesNotExist as e:
            request.session['list_movie_message'] = "Error: No existe Categoria. (" + e.message + ")"
            request.session['list_movie_flag'] = FLAG_ALERT
            self.code_return = -1

        except MovieMetadata.DoesNotExist as e:
            request.session['list_movie_message'] = "Error: No existe MovieMetadata. (" + e.message + ")"
            request.session['list_movie_flag'] = FLAG_ALERT
            self.code_return = -1

        # CARGAR VARIABLES USADAS EN FRONT
        assets = Asset.objects.filter(asset_type="unknown")
        channels = Channel.objects.all().order_by('name')
        girls = Girl.objects.all().order_by('name')
        categories = Category.objects.all().order_by('original_name')
        languages = Language.objects.all()


        title = 'Editar Movie'

        context = {'title': title, 'assets': assets, 'channels': channels, 'girls': girls, 'categories': categories,
                   'vmovie': vmovie, 'vgirlselected': vgirlselected, 'vgirlnotselected': vgirlnotselected,
                   'vcategoryselected': vcategoryselected, 'vcategorynotselected': vcategorynotselected,
                   'languages': languages, 'vmoviemetadata': vmoviemetadata, 'vlangmetadata': vlangmetadata,
                   'asset_id': asset_id, 'imgland': imgland, 'imgport': imgport,'flag':flag,'message':message}

        return render(request, 'cawas/movies/edit.html', context)



    def list(self, request):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        usuario = request.user
        titulo = ''
        page = request.GET.get('page')
        request.POST.get('page')
        movies_list = None

        message = ''
        flag = ''
        if request.session.has_key('list_movie_message'):
            if request.session['list_movie_message'] != '':
                message = request.session['list_movie_message']
                request.session['list_movie_message'] = ''

        if request.session.has_key('list_movie_flag'):
            if request.session['list_movie_flag'] != '':
                flag = request.session['list_movie_flag']
                request.session['list_movie_flag'] = ''

        if request.POST:
            titulo = request.POST['inputTitulo']
            selectestado = request.POST['selectestado']

            if titulo != '':
                assets = Asset.objects.filter(asset_id__icontains=titulo)
                movies_sel = Movie.objects.filter(Q(original_title__icontains=titulo)|Q(asset__in=assets))
            else:
                movies_sel = Movie.objects.all()

            if selectestado != '':
                movies_list = MovieMetadata.objects.filter(movie__in=movies_sel, publish_status=selectestado).order_by(
                    'movie_id')
            else:
                movies_list = MovieMetadata.objects.filter(movie__in=movies_sel).order_by('movie_id')

        if movies_list is None:
            movies_list = MovieMetadata.objects.all().order_by('movie_id')

        paginator = Paginator(movies_list, 20)  # Show 25 contacts per page
        try:
            movies = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            movies = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            movies = paginator.page(paginator.num_pages)

        context = {'message': message, 'flag':flag, 'registros': movies, 'titulo': titulo, 'usuario': usuario}

        return render(request, 'cawas/movies/list.html', context)





    def unpublish(self, request, id):
        # Despublicar
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        try:
            md = MovieMetadata.objects.get(id=id)
            vasset_id = md.movie.asset.asset_id

            # 1 - VERIFICAR, si estado de publicacion esta en Q, se debe eliminar
            publishs = PublishQueue.objects.filter(item_id=vasset_id, status='Q')
            if publishs.count > 0:
                publishs.delete()

            # Buscar todas Movies con esa chica
            # Realizar delete al backend
            setting = Setting.objects.get(code='backend_asset_url')
            api_key = Setting.objects.get(code='backend_api_key')
            vzones = PublishZone.objects.filter(enabled=True)
            for zone in vzones:
                abr = ApiBackendResource(zone.backend_url, setting.value, api_key.value)
                param = {"asset_id": md.movie.asset.asset_id,
                         "asset_type": "show",
                         "lang": md.language.code}
                abr.delete(param)

            # Actualizar Activated a False
            md.activated = False
            md.save()

            self.code_return = 0
            request.session['list_movie_message'] = 'Metadata en ' + md.language.name + ' de Movie ' + md.movie.asset.asset_id + ' Despublicado Correctamente'
            request.session['list_movie_flag'] = FLAG_SUCCESS

        except PublishZone.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "PublishZone no Existe. (" + str(e.message) + ")"})
        except MovieMetadata.DoesNotExist as e:
            return render(request, 'cawas/error.html',
                          {"message": "Metadata de Movie no Existe. (" + str(e.message) + ")"})
        except ApiBackendException as e:
            request.session['list_movie_message'] = "Error al despublicar (" + str(e.value) + ")"
            request.session['list_movie_flag'] = FLAG_ALERT

        return self.code_return





    def publish(self, request, id):
        md = MovieMetadata.objects.get(id=id)
        md.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
        #md.activated = True
        md.save()

        ph = PublishHelper()
        ph.func_publish_queue(request, md.movie.asset.asset_id, md.language, 'AS', 'Q', datetime.datetime.now().strftime('%Y-%m-%d'))
        ph.func_publish_image(request, md.movie.image)
        request.session['list_movie_message'] = 'Metadata en ' + md.language.name + ' de Movie ' + md.movie.asset.asset_id + ' Guardado en Cola de Publicacion'
        request.session['list_movie_flag'] = FLAG_SUCCESS
        self.code_return = 0

        return self.code_return


    def publish_all(self, request,param_movie, param_lang):
        #Publica nuevamente la movie para

        mditems = MovieMetadata.objects.filter(movie=param_movie, language=param_lang)
        #Actualizar la fecha de publicacion
        for md in mditems:
            md.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
            md.activated = True
            md.save()
            #Dejar en cola de publicacion para cada idioma
            ph = PublishHelper()
            ph.func_publish_queue(request, md.movie.asset.asset_id, md.language, 'AS', 'Q', md.publish_date)
            ph.func_publish_image(request, md.movie.image)
            self.code_return = 0

        return self.code_return
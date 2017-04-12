import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import Asset, Setting, Movie, MovieMetadata, MovieMetadata, Category, Language, Image, Girl, PublishZone, Channel, PublishQueue, ImageQueue
from ..Helpers.PublishHelper import PublishHelper
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..Helpers.GlobalValues import *
from backend_sdk import ApiBackendServer, ApiBackendResource


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
        if request.method == 'POST':

            # parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)

            # DECLARACION DE OBJECTOS
            mv = Movie()
            vasset = Asset()

            # CARGAR MOVIE
            try:
                vasset = Asset.objects.get(asset_id=decjson['Movie']['asset_id'])
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})

            # VALIDAR IMAGEN
            try:
                img = Image.objects.get(name=vasset.asset_id)
            except Image.DoesNotExist as e:
                vflag = "error"
                img = Image()

            try:
                pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
                pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            except Setting.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})

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
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})

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
            # calcular runtime
            # mv.runtime
            mv.save()

            # CARGAR GIRLS
            if (decjson['Movie']['girls'] is not None):
                vgirls = decjson['Movie']['girls']
                for item in vgirls:
                    try:
                        vgirl = Girl.objects.get(pk=item['girl_id'])
                        mv.girls.add(vgirl)
                    except Girl.DoesNotExist as e:
                        return render(request, 'cawas/error.html', {"message": "No existe Girl. (" + e.message + ")"})

            # CARGAR CATEGORIES
            vcategories = decjson['Movie']['categories']
            for item in vcategories:
                try:
                    vcategory = Category.objects.get(pk=item['category_id'])
                    mv.category.add(vcategory)
                except Category.DoesNotExist as e:
                    vflag = "error"
                    return render(request, 'cawas/error.html', {"message": "No existe Categoria. (" + e.message + ")"})

            # ACTUALIZAR EL ASSET A MOVIE
            vasset.asset_type = "movie"
            vasset.save()

            # CARGAR METADATA
            vmoviesmetadata = decjson['Movie']['Moviesmetadata']

            for item in vmoviesmetadata:
                try:
                    # CREAR METADATA POR IDIOMA
                    vlanguage = Language.objects.get(code=item['Moviemetadata']['language'])
                    if (item['Moviemetadata']['schedule_date'] != ''):
                        vpublishdate = datetime.datetime.strptime(item['Moviemetadata']['schedule_date'],
                                                                  '%d-%m-%Y').strftime('%Y-%m-%d')
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
                        # Recorrer el publicZone y genera un PublicQueue por cada idioma
                        ph = PublishHelper()
                        ph.func_publish_queue(request, vasset.asset_id, vlanguage, 'AS', 'Q', vpublishdate)
                        #vzones = PublishZone.objects.filter(enabled=True)
                        #for zone in vzones:
                            # CREAR COLA DE PUBLICACION
                        #    vpublish = PublishQueue()
                        #    vpublish.item_id = vasset.asset_id
                        #    vpublish.item_lang = vlanguage
                        #    vpublish.item_type = 'AS'
                        #    vpublish.status = 'Q'
                        #    vpublish.publish_zone = zone
                        #    vpublish.schedule_date = vpublishdate
                        #    vpublish.save()


                except Language.DoesNotExist as e:
                    return render(request, 'cawas/error.html', {"message": "No existe Lenguaje. (" + e.message + ")"})
                except Exception as e:
                    return render(request, 'cawas/error.html',
                                  {"message": "Error al Guardar metadata. (" + e.message + ")"})

            # COLA DE PUBLICACION PARA IMAGENES
            try:
                vzones = PublishZone.objects.filter(enabled=True)
                for zone in vzones:
                    imgQueue = ImageQueue()
                    imgQueue.image = img
                    imgQueue.publish_zone = zone
                    imgQueue.schedule_date = datetime.datetime.now()
                    imgQueue.save()
            except Exception as e:
                return render(request, 'cawas/error.html',
                              {"message": "Error al Generar Cola de Imagen. (" + e.message + ")"})
            vflag = "success"
            message = 'Registrado correctamente'
            # FIN DE POST

        # VARIABLES PARA GET
        # CARGAR VARIABLES USADAS EN FRONT
        assets = Asset.objects.filter(asset_type="unknown")
        vmovies = Movie.objects.all()
        channels = Channel.objects.all()
        girls = Girl.objects.all()
        categories = Category.objects.all()
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

        try:
            pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
        except Setting.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})

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
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})
            except Movie.DoesNotExist as e:
                return render(request, 'cawas/error.html',
                              {"message": "No existe Movie asociado al Asset. (" + e.message + ")"})
            except Image.DoesNotExist as e:
                img = Image()
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})

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
            mv.save()

            # CARGAR GIRLS
            if (decjson['Movie']['girls'] is not None):
                vgirls = decjson['Movie']['girls']
                for item in vgirls:
                    try:
                        vgirl = Girl.objects.get(pk=item['girl_id'])
                        mv.girls.add(vgirl)
                    except Girl.DoesNotExist as e:
                        return render(request, 'cawas/error.html', {"message": "No existe Girl. (" + e.message + ")"})

            # CARGAR CATEGORIES
            vcategories = decjson['Movie']['categories']
            for item in vcategories:
                try:
                    vcategory = Category.objects.get(pk=item['category_id'])
                    mv.category.add(vcategory)
                except Category.DoesNotExist as e:
                    return render(request, 'cawas/error.html', {"message": "No existe Categoria. (" + e.message + ")"})

            # ACTUALIZAR EL ASSET A MOVIE
            vasset.asset_type = "movie"
            vasset.save()

            # CARGAR METADATA
            vmoviesmetadata = decjson['Movie']['Moviesmetadata']
            # eliminar las movies metadata existentes


            MovieMetadata.objects.filter(movie=mv).delete()
            for item in vmoviesmetadata:
                if (item['Moviemetadata']['schedule_date'] != ''):
                    vpublishdate = datetime.datetime.strptime(item['Moviemetadata']['schedule_date'],
                                                              '%d-%m-%Y').strftime('%Y-%m-%d')
                else:
                    vpublishdate = datetime.datetime.now().strftime('%Y-%m-%d')

                try:
                    # CREAR METADATA POR IDIOMA
                    vlanguage = Language.objects.get(code=item['Moviemetadata']['language'])
                    try:
                        mmd = MovieMetadata.objects.get(movie=mv, language=vlanguage)
                    except MovieMetadata.DoesNotExist as e:
                        mmd = MovieMetadata();
                    mmd.language = vlanguage
                    mmd.movie = mv
                    mmd.title = item['Moviemetadata']['title']
                    mmd.summary_short = item['Moviemetadata']['summary_short']
                    mmd.summary_long = item['Moviemetadata']['summary_long']
                    mmd.publish_date = vpublishdate

                    # Si no existe METADATA, se GENERA
                    metadatas = MovieMetadata.objects.filter(movie=mv, language=mmd.language)
                    if metadatas.count() < 1:
                        mmd.save()
                        # Recorrer el publicZone y genera un PublicQueue por cada idioma
                        vzones = PublishZone.objects.filter(enabled=True)
                        for zone in vzones:
                            # CREAR COLA DE PUBLICACION
                            vpublish = PublishQueue()
                            vpublish.item_id = vasset.asset_id
                            vpublish.item_lang = vlanguage
                            vpublish.item_type = 'AS'
                            vpublish.status = 'Q'
                            vpublish.publish_zone = zone
                            vpublish.schedule_date = vpublishdate
                            vpublish.save()

                except Language.DoesNotExist as e:
                    return render(request, 'cawas/error.html', {"message": "No existe Lenguaje. (" + e.message + ")"})
                except Exception as e:
                    return render(request, 'cawas/error.html',
                                  {"message": "Error al Guardar metadata. (" + e.message + ")"})

            # COLA DE PUBLICACION PARA IMAGENES
            try:
                vzones = PublishZone.objects.filter(enabled=True)
                for zone in vzones:
                    imgQueue = ImageQueue()
                    imgQueue.image = img
                    imgQueue.publish_zone = zone
                    imgQueue.schedule_date = datetime.datetime.now()
                    imgQueue.save()
            except Exception as e:
                return render(request, 'cawas/error.html',
                              {"message": "Error al Generar Cola de Imagen. (" + e.message + ")"})
            flag = 'success'
            message='Guardado Correctamente'

        # VARIABLES PARA GET - CARGAR MOVIE
        try:
            vasset = Asset.objects.get(asset_id=asset_id)
            vmovie = Movie.objects.get(asset=vasset)

            i = len(vmovie.image.portrait.name)
            imgport = vmovie.image.portrait.name[5:i]

            i = len(vmovie.image.landscape.name)
            imgland = vmovie.image.landscape.name[5:i]

            vgirlselected = vmovie.girls.all()
            vgirlnotselected = Girl.objects.exclude(id__in=vgirlselected)
            vgirlselected = vmovie.girls.all()

            vmoviemetadata = MovieMetadata.objects.filter(movie=vmovie)
            vcategoryselected = vmovie.category.all()
            vcategorynotselected = Category.objects.exclude(id__in=vcategoryselected)
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
            return render(request, 'cawas/error.html',
                          {"message": "Asset no se encuentra Vinculado a Movie. (" + e.message + ")"})
        except Asset.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Asset no Existe. (" + e.message + ")"})
        except Category.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Categoria no Existe. (" + e.message + ")"})
        except MovieMetadata.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "MovieMetaData No Existe . (" + e.message + ")"})

        # CARGAR VARIABLES USADAS EN FRONT
        assets = Asset.objects.filter(asset_type="unknown")
        channels = Channel.objects.all()
        girls = Girl.objects.all()
        categories = Category.objects.all()
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
                movies_sel = Movie.objects.filter(original_title__icontains=titulo)
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
            #girl = md.movie
            #movies = Movie.objects.filter(girls__in=[girl])
            #for movie in movies:
            #    # Quitar la asocicacion de Chica-Movie
            #    movie.girls.remove(girl)
            #    movie.save()

                # Las movies modificadas, volver a publicarlas PublishQueue
            #    metadatas = MovieMetadata.objects.filter(movie=movie)
            #    for metadata in metadatas:
            #        ph = PublishHelper()
            #        ph.func_publish_queue(request, movie.asset.asset_id, metadata.language, 'AS', 'Q',
            #                              metadata.publish_date)
            #        print 'asset_id Despublicacion: ' + movie.asset.asset_id

            # Realizar delete al backend
            setting = Setting.objects.get(code='backend_asset_url')
            vzones = PublishZone.objects.filter(enabled=True)
            for zone in vzones:
                abr = ApiBackendResource(zone.backend_url, setting.value)
                param = {"asset_id": md.movie.asset.asset_id,
                         "asset_type": "show",
                         "lang": md.language.code}
                # print 'param: ' + param
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

        return self.code_return





    def publish(self, request, id):
        md = MovieMetadata.objects.get(id=id)
        md.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
        md.activated = True
        md.save()

        ph = PublishHelper()
        ph.func_publish_queue(request, md.movie.asset.asset_id, md.language, 'AS', 'Q', datetime.datetime.now().strftime('%Y-%m-%d'))
        ph.func_publish_image(request, md.movie.image)
        request.session['list_movie_message'] = 'Metadata en ' + md.language.name + ' de Movie ' + md.movie.asset.asset_id + ' Publicada Correctamente'
        request.session['list_movie_flag'] = FLAG_SUCCESS
        self.code_return = 0

        return self.code_return


    def publish_all(self, request,param_movie ):
        #Publica nuevamente la movie para

        mditems = MovieMetadata.objects.filter(movie=param_movie)
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
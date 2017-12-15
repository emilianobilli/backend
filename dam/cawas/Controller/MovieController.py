import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import Asset, Setting, Country, Movie, MovieMetadata, MovieMetadata, Category, Language, Image, Girl, PublishZone, Channel, PublishQueue, ImageQueue
from ..Helpers.PublishHelper import PublishHelper
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..Helpers.GlobalValues import *
from ..backend_sdk import ApiBackendServer, ApiBackendResource, ApiBackendException
from django.db.models import Q
from django.http import JsonResponse
from django.http import HttpResponse
import base64

class MovieController(object):


    def api_edit(self, request):
        respuesta = 500
        if request.is_ajax():
            if request.method == 'POST':
                respuesta = self.validateParseMovie(request.body, request)
                print 'respuesta:' + str(respuesta)

        return respuesta





    def validateParseMovie(self, body, request):
        nueva_movie= False
        publicar = False
        vasset = Asset()
        # CARGAR MOVIE
        try:
            json_data = json.loads(body)
            asset_id = json_data['movie']['asset_id']
            vasset = Asset.objects.get(asset_id=asset_id)
            mv = Movie.objects.get(asset=vasset)

            # Nueva movie
            if mv is None:
                mv = Movie()
                # ACTUALIZAR EL ASSET A MOVIE
                vasset.asset_type = "movie"
                vasset.save()
                nueva_movie = True

            vchannel = Channel.objects.get(pk=json_data['movie']['channel_id'])
            mv.asset = vasset
            mv.channel = vchannel
            mv.original_title = json_data['movie']['original_title']
            if (json_data['movie']['year'] is not None):
                mv.year = json_data['movie']['year']

            if (json_data['movie']['cast'] is not None):
                mv.cast = json_data['movie']['cast']

            if (json_data['movie']['directors'] is not None):
                mv.directors = json_data['movie']['directors']

            mv.display_runtime = json_data['movie']['display_runtime']
            print 'debug1'
            if (json_data['movie']['publicar'] is not None):
                print 'debug3' + str(json_data['movie']['publicar'])
                if json_data['movie']['publicar']==1:
                    publicar = True
            print 'debug2'
            mv.save()

            if (json_data['movie']['girls'] is not None):
                vgirls = json_data['movie']['girls']
                for item in vgirls:
                    vgirl = Girl.objects.get(pk=item['girl_id'])
                    mv.girls.add(vgirl)

            # CARGAR CATEGORIES
            if (json_data['movie']['categories'] is not None):
                vcategories = json_data['movie']['categories']
                for item in vcategories:
                    vcategory = Category.objects.get(id=item)
                    mv.category.add(vcategory)

            #ACTUALIZAR EL ASSET A MOVIE
            vasset.asset_type = "movie"
            vasset.save()

            # CARGAR Countries al Asset de la Movie
            if (json_data['movie']['countries'] is not None):
                countries = json_data['movie']['countries']
                mv.asset.target_country = []
                for item in countries:
                    country = Country.objects.get(id=item)

                    mv.asset.target_country.add(country)

            mv.save()
            # SI hay items en estado Queued, se elimina
            ph = PublishHelper()
            vmoviesmetadata = json_data['movie']['moviemetadatas']

            for item in vmoviesmetadata:
                # CREAR METADATA POR IDIOMA
                vlanguage = Language.objects.get(code=item['Moviemetadata']['language'])
                # si no esta cargada la fecha, se guarda con la fecha de hoy
                if (item['Moviemetadata']['schedule_date'] != ''):
                    vpublishdate = datetime.datetime.strptime(item['Moviemetadata']['schedule_date'],
                                                              '%d-%m-%Y').strftime('%Y-%m-%d')
                else:
                    vpublishdate = datetime.datetime.now().strftime('%Y-%m-%d')

                try:
                    mmd = MovieMetadata.objects.get(movie=mv, language=vlanguage)
                except MovieMetadata.DoesNotExist as e:
                    mmd = MovieMetadata()
                mmd.language = vlanguage
                mmd.title = item['Moviemetadata']['title']
                mmd.summary_short = item['Moviemetadata']['summary_short']
                mmd.summary_long = item['Moviemetadata']['summary_long']
                mmd.publish_date = vpublishdate
                mmd.movie = mv
                mmd.save()

            print 'publicar1'
            if nueva_movie == True or publicar == True:
                metadatas = MovieMetadata.objects.filter(movie=mv)
                print 'publicar1'
                for mdi in metadatas:
                    print 'publicar2'
                    if ph.func_publish_queue(request, mdi.movie.asset.asset_id, mdi.language, 'AS', 'Q', mdi.publish_date) == RETURN_ERROR:
                        return HttpResponse("Error al Publicar (" + str(e.message) + ")", None, 500)
                    print 'publicar3'
                    mdi.queue_status = 'Q'
                    mdi.save()

            mydata = [{'code': 200, 'message': 'Guardado Correctamente'}]
            #return HttpResponse("Guardado Correctamente", None, 200)
            return HttpResponse(json.dumps(mydata), None, 200)
        except Asset.DoesNotExist as e:
            return HttpResponse("No existe Asset",None, 500)
        except Channel.DoesNotExist as e:
            return HttpResponse("No existe Canal", None, 500)
        except Girl.DoesNotExist as e:
            return HttpResponse("Error: No existe Chica (" + str(e.message) + ")", None, 500)
        except Category.DoesNotExist as e:
            return HttpResponse("Error: No existe Categoria (" + str(e.message) + ")", None, 500)
        except Country.DoesNotExist as e:
            return HttpResponse("Error: No Existe Pais (" + str(e.message) + ")", None, 500)
        except Language.DoesNotExist as e:
            return HttpResponse("Error: Lenguage No Existe (" + str(e.message) + ")", None, 500)
        except Exception as e:
            return HttpResponse("Hubo un error:(" + str(e.message) + ")", None, 500)
        except KeyError:
            return HttpResponse("Error en decodificacion de datos", None, 500)

















    def add(self, request):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        # ALTA - MOVIE GET debe cargar variables,
        #              POST procesa solo la imagen, los datos se guaran
        # cawas/static/images/landscape/  cawas/static/images/portrait/

        vflag = ''
        message = ''

        ph = PublishHelper()
        pathfilesport= ''
        pathfilesland = ''



        if request.method == 'POST':
            # DECLARACION DE OBJECTOS
            mv = Movie()
            vasset = Asset()
            # VALIDAR IMAGEN
            try:
                img = Image.objects.get(name=vasset.asset_id)
                base_dir = Setting.objects.get(code='dam_base_dir')
            except Setting.DoesNotExist as e:
                request.session['list_movie_message'] = "Error: No existe Setting (" + str(e.message) + ")"
                request.session['list_movie_flag'] = FLAG_ALERT
                self.code_return = -1
            except Image.DoesNotExist as e:
                img = Image()

            img.name = vasset.asset_id
            # TRATAMIENTO DE IMAGEN Landscape
            if (request.FILES.has_key('ThumbHor')):
                if request.FILES['ThumbHor'].name != '':
                    # TRATAMIENTO DE IMAGEN Landscape
                    img.landscape = request.FILES['ThumbHor']
                    extension = os.path.splitext(img.landscape.name)[1]
                    varchivo = pathfilesland.value + img.name + extension
                    img.landscape.name = varchivo
                    varchivo_server = base_dir.value + varchivo
                    if os.path.isfile(varchivo_server):
                        os.remove(varchivo_server)

            # IMAGEN Landscape
            if (request.FILES.has_key('ThumbVer')):
                if request.FILES['ThumbVer'].name != '':
                    # Landscape
                    img.portrait = request.FILES['ThumbVer']
                    extension = os.path.splitext(img.portrait.name)[1]
                    varchivo = pathfilesport.value + img.name + extension
                    img.portrait.name = varchivo
                    # si existe archivo, lo borra
                    varchivo_server = base_dir.value + varchivo
                    if os.path.isfile(varchivo_server):
                        os.remove(varchivo_server)
            img.save()
            mv.image = img
            #La Imagen se publica siempre
            ph = PublishHelper()
            if ph.func_publish_image(request, img) == RETURN_ERROR:
                request.session['list_movie_message'] = 'Error' + request.session['message']
                request.session['list_movie_flag'] = FLAG_ALERT
                return RETURN_ERROR

            request.session['list_movie_message'] = 'Guardado Correctamente'
            request.session['list_movie_flag'] = FLAG_SUCCESS


        # CARGAR VARIABLES USADAS EN FRONT
        assets = Asset.objects.filter(asset_type="unknown")
        vmovies = Movie.objects.all().order_by('original_title')
        channels = Channel.objects.all().order_by('name')
        girls = Girl.objects.all().order_by('name')
        categories = Category.objects.all().order_by('original_name')
        countries = Country.objects.all().order_by('name')

        vlanguages = Language.objects.all()
        title = 'Nueva Movie'
        context = {'title': title, 'assets': assets, 'channels': channels,
                   'girls': girls, 'categories': categories, 'movies': vmovies,
                   'vlanguages': vlanguages, 'flag': vflag, 'message': message,
                   'countries':countries}
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
            base_dir = Setting.objects.get(code='dam_base_dir')
        except Setting.DoesNotExist as e:
            request.session['list_movie_message'] = "Error: No existe Setting (" + str(e.message) + ")"
            request.session['list_movie_flag'] = FLAG_ALERT
            self.code_return = -1

        # Post Movie - Graba datos
        if request.method == 'POST':
            # DECLARACION DE OBJECTOS
            mv = Movie()
            vasset = Asset()

            try:
                vasset = Asset.objects.get(asset_id=asset_id)
                mv = Movie.objects.get(asset=vasset)
                img = Image.objects.get(name=vasset.asset_id)

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

            img.name = vasset.asset_id
            # IMAGEN Portrait
            if (request.FILES.has_key('ThumbHor')):
                print 'debug2'
                if request.FILES['ThumbHor'].name != '':
                    # TRATAMIENTO DE IMAGEN Landscape
                    img.landscape = request.FILES['ThumbHor']
                    extension = os.path.splitext(img.landscape.name)[1]
                    varchivo = pathfilesland.value + img.name + extension
                    img.landscape.name = varchivo
                    varchivo_server = base_dir.value + varchivo
                    if os.path.isfile(varchivo_server):
                        os.remove(varchivo_server)

            # IMAGEN Landscape
            if (request.FILES.has_key('ThumbVer')):
                print 'debug1'
                if request.FILES['ThumbVer'].name != '':
                    # Landscape
                    img.portrait = request.FILES['ThumbVer']
                    extension = os.path.splitext(img.portrait.name)[1]
                    varchivo = pathfilesport.value + img.name + extension
                    img.portrait.name = varchivo
                    # si existe archivo, lo borra
                    varchivo_server = base_dir.value + varchivo
                    if os.path.isfile(varchivo_server):
                        os.remove(varchivo_server)
            img.save()
            mv.image = img
            mv.save()
            request.session['list_movie_message'] = 'Guardado Correctamente'
            request.session['list_movie_flag'] = FLAG_SUCCESS

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

            countries_selected = vmovie.asset.target_country.all().order_by('name')
            countries_notselected = Country.objects.exclude(id__in=countries_selected).order_by('name')


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

        context = {'title': title,
                   'assets': assets,
                   'channels': channels,
                   'girls': girls,
                   'categories': categories,
                   'vmovie': vmovie,
                   'vgirlselected': vgirlselected,
                   'vgirlnotselected': vgirlnotselected,
                   'vcategoryselected': vcategoryselected,
                   'vcategorynotselected': vcategorynotselected,
                   'languages': languages,
                   'vmoviemetadata': vmoviemetadata,
                   'vlangmetadata': vlangmetadata,
                   'asset_id': asset_id,
                   'imgland': imgland,
                   'imgport': imgport,
                   'flag':flag,
                   'message':message,
                   'countries_selected':countries_selected,
                   'countries_notselected':countries_notselected}

        return render(request, 'cawas/movies/edit.html', context)



    def list(self, request):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        usuario = request.user
        titulo = ''
        request.POST.get('page')
        message = ''
        flag = ''
        filter = False

        #Filtro de busqueda
        if request.GET.has_key('search'):
            search = request.GET.get('search')
            if search != '':
                filter = True
                movies = MovieMetadata.objects.filter(Q(title__icontains=search) | Q(movie__asset__asset_id__icontains=search)).order_by('-id')

        if filter==False:
            movies = MovieMetadata.objects.all().order_by('-id')
            paginator = Paginator(movies, 25)
            page = request.GET.get('page')
            try:
                movies = paginator.page(page)
            except PageNotAnInteger:
                movies = paginator.page(1)
            except EmptyPage:
                movies = paginator.page(paginator.num_pages)


        #filtro por
        #if request.GET.has_key('activated'):
        #    activated = request.GET.get('activated')
        #    if activated != 'Todos':
        #        movies.filter(activated=activated)


        if request.session.has_key('list_movie_message'):
            if request.session['list_movie_message'] != '':
                message = request.session['list_movie_message']
                request.session['list_movie_message'] = ''

        if request.session.has_key('list_movie_flag'):
            if request.session['list_movie_flag'] != '':
                flag = request.session['list_movie_flag']
                request.session['list_movie_flag'] = ''

        context = {'message': message, 'flag':flag, 'registros': movies, 'titulo': titulo, 'usuario': usuario,'filter':filter}
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
            publishs = PublishQueue.objects.filter(item_id=vasset_id, status='Q', item_lang=md.language)
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
        md.queue_status = 'Q'
        md.save()

        ph = PublishHelper()
        # SI hay items en estado Queued, se elimina
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

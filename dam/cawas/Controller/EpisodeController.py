import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import Asset, Setting, Girl, Country, Block, Category, Language, Image,PublishZone,PublishQueue, Channel, Device, Serie, Movie, Episode, EpisodeMetadata
from ..Helpers.PublishHelper import PublishHelper
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..Helpers.GlobalValues import *
from ..backend_sdk import ApiBackendServer, ApiBackendResource, ApiBackendException
from django.db.models import Q

class EpisodeController(object):
    code_return = 0
    message_return = ''
    # 0 = ok, -1= error


    def add(self, request):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        # VARIABLES LOCALES
        message = ''
        vflag = ''
        vschedule_date = ''
        vgrabarypublicar = ''
        if request.method == 'POST':
            # VARIABLES
            vepisode = Episode()

            try:
                pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
                pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
                base_dir = Setting.objects.get(code='dam_base_dir')
                # Parsear JSON
                strjson = request.POST['varsToJSON']
                decjson = json.loads(strjson.replace('\r','\\r').replace('\n','\\n'))
                # DATOS OBLIGATORIOS
                vasset = Asset.objects.get(asset_id=decjson['Episode']['asset_id'])
                vasset.asset_type = "episode"
                vasset.save()
                vepisode.asset = vasset
                vepisode.original_title = decjson['Episode']['original_title']
                vepisode.channel = Channel.objects.get(pk=decjson['Episode']['channel_id'])
                vepisode.display_runtime = decjson['Episode']['display_runtime']
                vasset_serie = Asset.objects.get(asset_id=decjson['Episode']['serie_id'])
                vepisode.serie = Serie.objects.get(asset=vasset_serie)
                vepisode.chapter = decjson['Episode']['chapter']
                vepisode.season = decjson['Episode']['season']
                vgrabarypublicar = decjson['Episode']['publicar']

                # Datos OPCIONALES
                if (decjson['Episode']['year'] is not None):
                    vepisode.year = decjson['Episode']['year']

                if (decjson['Episode']['cast'] is not None):
                    vepisode.cast = decjson['Episode']['cast']

                if (decjson['Episode']['directors'] is not None):
                    vepisode.directors = decjson['Episode']['directors']

                try:
                    vimg = Image.objects.get(name=vasset.asset_id)
                except Image.DoesNotExist as e:
                    vimg = Image()

                vimg.name = vasset.asset_id
                # IMAGEN Portrait
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
                vepisode.image = vimg
                vepisode.save()
            except Asset.DoesNotExist as e:
                request.session['list_episode_message'] = 'Error: ' + str(e.message)
                request.session['list_episode_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return
            except Setting.DoesNotExist as e:
                request.session['list_episode_message'] = 'Error: ' + str(e.message)
                request.session['list_episode_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return
            except Serie.DoesNotExist as e:
                request.session['list_episode_message'] = 'Error: ' + str(e.message)
                request.session['list_episode_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return
            except Image.DoesNotExist as e:
                request.session['list_episode_message'] = 'Error: ' + str(e.message)
                request.session['list_episode_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return
            except Language.DoesNotExist as e:
                request.session['list_episode_message'] = 'Error: ' + str(e.message)
                request.session['list_episode_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return
            except Channel.DoesNotExist as e:
                request.session['list_episode_message'] = 'Error: ' + str(e.message)
                request.session['list_episode_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return
            except Device.DoesNotExist as e:
                request.session['list_episode_message'] = 'Error: ' + str(e.message)
                request.session['list_episode_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return

            # CARGAR ASSETS
            if (decjson['Episode']['girls'] is not None):
                vgirls = decjson['Episode']['girls']
                for item in vgirls:
                    try:
                        asset_id = item['girl_id']
                        print "AssetId add episode" + asset_id
                        vgirl = Girl.objects.get(asset_id=item['girl_id'])
                        vepisode.girls.add(vgirl)
                    except Girl.DoesNotExist as e:
                        request.session['list_episode_message'] = 'Error: ' + str(e.message)
                        request.session['list_episode_flag'] = FLAG_ALERT
                        self.code_return = -1
                        return self.code_return
                    except Asset.DoesNotExist as e:
                        request.session['list_episode_message'] = 'Error: ' + str(e.message)
                        request.session['list_episode_flag'] = FLAG_ALERT
                        self.code_return = -1
                        return self.code_return
            # CARGAR CATEGORY
            vcategories = decjson['Episode']['categories']
            for item in vcategories:
                try:
                    category_id = item['category_id']
                    print "category_id add episode" + category_id
                    vcategory = Category.objects.get(pk=category_id)
                    vepisode.category.add(vcategory)
                except Category.DoesNotExist as e:
                    request.session['list_episode_message'] = 'No Existe Categoria ' + str(e.message)
                    request.session['list_episode_flag'] = FLAG_ALERT
                    self.code_return = -1
                    return self.code_return

            #leer target_country de la serie a la que pertence el episodio
            #setear en el asset del episodio los mismos target_countries
            #countries = vepisode.serie.asset
            serie = vepisode.serie
            asset = serie.asset

            vepisode.save()

            vepisode.asset.target_country = []
            vepisode.save()

            for item in vepisode.serie.asset.target_country.all():
                vepisode.asset.target_country.add(item)

            vepisode.save()
            #SI hay items en estado Queued
            ph = PublishHelper()
            vepisodemetadata = decjson['Episode']['Episodemetadatas']
            for item in vepisodemetadata:
                try:
                    vlang = Language.objects.get(code=item['Episodemetadata']['language'])
                    try:
                        emd = EpisodeMetadata.objects.get(episode=vepisode, language=vlang)
                    except EpisodeMetadata.DoesNotExist as e:
                        emd = EpisodeMetadata();

                    # convertDateYMDnowIsNull
                    if (item['Episodemetadata']['schedule_date'] != ''):
                        vschedule_date = datetime.datetime.strptime(item['Episodemetadata']['schedule_date'],
                                                                    '%d-%m-%Y').strftime('%Y-%m-%d')
                    else:
                        vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')

                    emd.language = vlang
                    emd.title = item['Episodemetadata']['title']
                    emd.summary_short = item['Episodemetadata']['summary_short']
                    emd.summary_long = item['Episodemetadata']['summary_long']
                    emd.publish_date = vschedule_date
                    emd.episode = vepisode
                    emd.save()
                except Language.DoesNotExist as e:
                    request.session['list_episode_message'] = 'Error: ' + str(e.message)
                    request.session['list_episode_flag'] = FLAG_ALERT
                    self.code_return = -1
                    return self.code_return
            request.session['list_episode_message'] = 'Guardado Correctamente'
            request.session['list_episode_flag'] = FLAG_SUCCESS
            #PUBLICAR METADATA
            if vgrabarypublicar == '1':
                try:
                    ph = PublishHelper()
                    ph.func_publish_image(request, vimg)
                    metadatas = EpisodeMetadata.objects.filter(episode=vepisode)
                    for mdi in metadatas:
                        # Publicar el Episodio
                        mdi.queue_status = True
                        mdi.save()
                        ph = PublishHelper()
                        ph.func_publish_queue(request, mdi.episode.asset.asset_id, mdi.language, 'AS', 'Q',vschedule_date)
                        ph.func_publish_image(request, vimg)

                        # Se vuelve a publicar la SERIE en el idioma del Episodio publicado
                        if (PublishQueue.objects.filter(item_id=mdi.episode.serie.asset.asset_id,status__in=['Q', 'D']).count() < 1):
                            ph = PublishHelper()
                            ph.func_publish_queue(request, vepisode.serie.asset.asset_id, vlang, 'AS', 'Q', vschedule_date)
                            ph.func_publish_image(request, vepisode.serie.image)
                except EpisodeMetadata.DoesNotExist as e:
                    self.code_return = -1
                    request.session['list_episode_message'] = 'Error al Publicar el Episodio ' + e.message
                    request.session['list_episode_flag'] = FLAG_ALERT
                    return self.code_return
                except Exception as e:
                    self.code_return = -1
                    request.session['list_episode_message'] = 'Error al Republicar la SERIE' + e.message
                    request.session['list_episode_flag'] = FLAG_ALERT
                    return self.code_return

            vflag = "success"
            message ='Guardado Correctamente'

            context = {"flag": vflag, 'message':message }
            return render(request, 'cawas/episodes/add.html', context)
            # Fin datos EPISODE

        # Variables Para GET
        vseries = Serie.objects.all()
        vchannels = Channel.objects.all()
        vcategories = Category.objects.all()
        vgirls = Girl.objects.all()
        vlanguages = Language.objects.all()
        vmovies = Movie.objects.all()
        vcapitulos = Episode.objects.all()
        vassets = Asset.objects.filter(asset_type="unknown")
        countries = Country.objects.all().order_by('name')

        context = {'message': message, 'vcategories': vcategories, 'vchannels': vchannels, 'vgirls': vgirls,
                   'vlanguages': vlanguages, 'vseries': vseries, 'vmovies': vmovies, 'vcapitulos': vcapitulos,
                   'vassets': vassets,'countries':countries}

        return render(request, 'cawas/episodes/add.html', context)




    def edit(self,request, episode_id):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        # VARIABLES LOCALES
        message = ''
        vflag = ''
        vschedule_date = ''
        vasset = Asset()
        vepisode = Episode()
        try:
            vasset = Asset.objects.get(asset_id=episode_id)
            #print "episode: " + episode_id
            vepisode = Episode.objects.get(asset=vasset)
            i = len(vepisode.image.portrait.name)
            imgport = vepisode.image.portrait.name[5:i]
            i = len(vepisode.image.landscape.name)
            imgland = vepisode.image.landscape.name[5:i]
            #imgland = vepisode.image.landscape.name
            #print "episodio " + vepisode.original_title

        except Asset.DoesNotExist as e:
            request.session['list_episode_message'] = 'No Existe Asset' +  str(e.message)
            request.session['list_episode_flag'] = FLAG_ALERT
            self.code_return = -1
            return self.code_return
        except Setting.DoesNotExist as e:
            request.session['list_episode_message'] = 'No Existe Espisodio ' + str(e.message)
            request.session['list_episode_flag'] = FLAG_SUCCESS
            self.code_return = -1
            return self.code_return
        if request.method == 'POST':
            # VARIABLES
            try:
                pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
                pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
                base_dir = Setting.objects.get(code='dam_base_dir')
                # Parsear JSON
                strjson = request.POST['varsToJSON']
                decjson = json.loads(strjson.replace('\r','\\r').replace('\n','\\n'))
                # DATOS OBLIGATORIOS
                vepisode.original_title = decjson['Episode']['original_title']
                vepisode.channel = Channel.objects.get(pk=decjson['Episode']['channel_id'])
                vepisode.display_runtime = decjson['Episode']['display_runtime']
                print "Serie_id" + decjson['Episode']['serie_id']
                vasset_serie = Asset.objects.get(asset_id=decjson['Episode']['serie_id'])
                vepisode.serie = Serie.objects.get(asset=vasset_serie)
                vepisode.chapter = decjson['Episode']['chapter']
                vepisode.season = decjson['Episode']['season']

                # Datos OPCIONALES
                if (decjson['Episode']['year'] is not None):
                    vepisode.year = decjson['Episode']['year']

                if (decjson['Episode']['cast'] is not None):
                    vepisode.cast = decjson['Episode']['cast']

                if (decjson['Episode']['directors'] is not None):
                    vepisode.directors = decjson['Episode']['directors']

                try:
                    vimg = Image.objects.get(name=vasset.asset_id)
                except Image.DoesNotExist as e:
                    vimg = Image()


                vimg.name = vasset.asset_id
                # IMAGEN Portrait
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
                vepisode.image = vimg
                vepisode.save()
            except Asset.DoesNotExist as e:
                request.session['list_episode_message'] = 'No Existe Asset' + str(e.message)
                request.session['list_episode_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return
            except Exception as e:
                request.session['list_episode_message'] = 'Error al Guardar Episodio: ' + str(e.message)
                request.session['list_episode_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return

            # CARGAR ASSETS
            vepisode.girls = []
            vepisode.save()

            if (decjson['Episode']['girls'] is not None):
                vgirls = decjson['Episode']['girls']
                for item in vgirls:
                    try:
                        # print item['asset_id']
                        asset_id = item['girl_id']
                        print "AssetId add episode" + asset_id
                        vgirl = Girl.objects.get(asset_id=item['girl_id'])
                        vepisode.girls.add(vgirl)
                    except Exception as e:
                        request.session['list_episode_message'] = 'Error al Guardar Episodio: ' + str(e.message)
                        request.session['list_episode_flag'] = FLAG_ALERT
                        self.code_return = -1
                        return self.code_return

            vepisode.category = []
            vepisode.save()
            # CARGAR CATEGORY
            vcategories = decjson['Episode']['categories']
            for item in vcategories:
                try:
                    category_id = item['category_id']
                    print "category_id add episode" + category_id
                    vcategory = Category.objects.get(pk=category_id)
                    vepisode.category.add(vcategory)
                except Exception as e:
                    request.session['list_episode_message'] = 'Error al Guardar Episodio: ' + str(e.message)
                    request.session['list_episode_flag'] = FLAG_ALERT
                    self.code_return = -1
                    return self.code_return


            vepisode.save()




            #Eliminar cola de publicacion para el item en estado Queued
            ph = PublishHelper()
            vepisodemetadata = decjson['Episode']['Episodemetadatas']
            for item in vepisodemetadata:
                try:
                    vlang = Language.objects.get(code=item['Episodemetadata']['language'])
                    try:
                        emd = EpisodeMetadata.objects.get(episode=vepisode, language=vlang)
                    except EpisodeMetadata.DoesNotExist as e:
                        emd = EpisodeMetadata();

                    # convertDateYMDnowIsNull
                    if (item['Episodemetadata']['schedule_date'] != ''):
                        vschedule_date = datetime.datetime.strptime(item['Episodemetadata']['schedule_date'],
                                                                    '%d-%m-%Y').strftime('%Y-%m-%d')
                    else:
                        vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                    emd.language = vlang
                    emd.title = item['Episodemetadata']['title']
                    emd.summary_short = item['Episodemetadata']['summary_short']
                    emd.summary_long = item['Episodemetadata']['summary_long']
                    emd.publish_date = vschedule_date
                    emd.episode = vepisode
                    emd.queue_status = 'Q'
                    emd.save()
                    #
                    #Publicar el Episodio
                    ph = PublishHelper()
                    ph.func_publish_queue(request, vepisode.asset.asset_id, vlang, 'AS', 'Q', vschedule_date)
                    ph.func_publish_image(request, vimg)

                    # Se vuelve a publicar la SERIE en el idioma del Episodio publicado
                    if (PublishQueue.objects.filter(item_id=vepisode.serie.asset.asset_id,status__in=['Q', 'D']).count() < 1):
                        ph = PublishHelper()
                        ph.func_publish_queue(request, vepisode.serie.asset.asset_id, vlang, 'AS', 'Q', vschedule_date)
                        ph.func_publish_image(request, vepisode.serie.image)

                    request.session['list_episode_message'] = 'Guardado Correctamente '
                    request.session['list_episode_flag'] = FLAG_SUCCESS


                except Language.DoesNotExist as e:
                    self.code_return = -1
                    request.session['list_episode_message'] = 'Lenguaje no Existe ' + e.message
                    request.session['list_episode_flag'] = FLAG_ALERT
                    return self.code_return
                except Exception as e:
                    self.code_return = -1
                    request.session['list_episode_message'] = 'Error al Guardar Episode Metadata ' + e.message
                    request.session['list_episode_flag'] = FLAG_ALERT
                    return self.code_return

        try:
            vchannels = Channel.objects.all()
            vcategories = Category.objects.all()
            vgirls = Girl.objects.all()
            vlanguages = Language.objects.all()
            vmovies = Movie.objects.all()
            vcapitulos = Episode.objects.all()
            vassets = Asset.objects.filter(asset_type="unknown")

            vgirlselected = vepisode.girls.all()
            vgirlnotselected = Girl.objects.exclude(id__in=vgirlselected)
            vcategoryselected = vepisode.category.all()
            vcategorynotselected = Category.objects.exclude(id__in=vcategoryselected)
            vseries = Serie.objects.all()

            countries_selected = vepisode.asset.target_country.all().order_by('name')
            countries_notselected = Country.objects.exclude(id__in=countries_selected).order_by('name')

            # nuevo diccionario para completar lenguages y metadata
            vlangmetadata = []
            for itemlang in vlanguages:
                try:
                    vepisodemetadata = EpisodeMetadata.objects.get(episode=vepisode, language=itemlang)
                    vlangmetadata.append({
                        'checked': True, 'code': itemlang.code, 'name': itemlang.name,
                        'title': vepisodemetadata.title, 'summary_short': vepisodemetadata.summary_short,
                        'summary_long': vepisodemetadata.summary_long, 'publish_date': vepisodemetadata.publish_date
                    })
                except EpisodeMetadata.DoesNotExist as a:
                    vlangmetadata.append({'checked': False, 'code': itemlang.code, 'name': itemlang.name, 'titulo': '',
                                          'descripcion': '', 'fechapub': ''})

        except Girl.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Chica. (" + e.message + ")"})
        except Category.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Categoria. (" + e.message + ")"})

        context = {'message': message, 'vgirlnotselected': vgirlnotselected,
                   'vgirlselected': vgirlselected,
                   'imgland': imgland, 'imgport': imgport, 'vepisode': vepisode,
                   'vcategorynotselected': vcategorynotselected, 'vcategoryselected': vcategoryselected,
                   'vchannels': vchannels, 'vlangmetadata': vlangmetadata, 'vseries': vseries,
                   'countries_selected':countries_selected, 'countries_notselected':countries_notselected
                   }

        return render(request, 'cawas/episodes/edit.html', context)



    def list(self, request):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        usuario = request.user
        #Cuando hay una Des-publicacion se completa esta variable
        message =''
        flag = ''
        if request.session.has_key('list_episode_message'):
            if request.session['list_episode_message'] != '':
                message = request.session['list_episode_message']
                request.session['list_episode_message'] = ''

        if request.session.has_key('list_episode_flag'):
            if request.session['list_episode_flag'] != '':
                flag = request.session['list_episode_flag']
                request.session['list_episode_flag'] = ''

        page = request.GET.get('page')
        request.POST.get('page')
        episodes_list = None

        if request.POST:
            titulo = request.POST['inputTitulo']
            selectestado = request.POST['selectestado']
            # FILTROS
            #Q(name__icontains=titulo) | Q(block_id__icontains=titulo)
            if titulo != '':
                assets = Asset.objects.filter(asset_id__icontains=titulo)
                episodes_sel = Episode.objects.filter(Q(original_title__icontains=titulo)|Q(asset__in=assets))
            else:
                episodes_sel = Episode.objects.all()

            if selectestado != '':
                episodes_list = EpisodeMetadata.objects.filter(episode__in=episodes_sel, queue_status=selectestado).order_by('-id')
            else:
                episodes_list = EpisodeMetadata.objects.filter(episode__in=episodes_sel).order_by('-id')



        if episodes_list is None:
            episodes_list = EpisodeMetadata.objects.all().order_by('-id')

        paginator = Paginator(episodes_list, 20)  # Show 25 contacts per page
        try:
            episodes = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            episodes = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            episodes = paginator.page(paginator.num_pages)

        context = {'message': message,'flag':flag, 'registros': episodes, 'usuario': usuario}
        return render(request, 'cawas/episodes/list.html', context)


    #despublicar
    def unpublish(self, request, id):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        try:
            episodemetadata = EpisodeMetadata.objects.get(id=id)
            vasset_id = episodemetadata.episode.asset.asset_id


            # 1 - VERIFICAR, si estado de publicacion esta en Q, se debe eliminar
            publishs = PublishQueue.objects.filter(item_id=vasset_id, status='Q')
            if publishs.count > 0:
                publishs.delete()



            # 2 - Realizar delete al backend
            setting = Setting.objects.get(code='backend_asset_url')
            api_key = Setting.objects.get(code='backend_api_key')
            vzones = PublishZone.objects.filter(enabled=True)
            for zone in vzones:
                abr = ApiBackendResource(zone.backend_url, setting.value, api_key.value)
                param = {"asset_id": episodemetadata.episode.asset.asset_id,
                         "asset_type": "show",
                         "lang": episodemetadata.language.code}
                abr.delete(param)
            # Se deberia hacer algo con las Series?

            # mostrar cartel de informaion
            # eliminar episodiometada en los idiomas
            # eliminar episodio
            # actulizar asset a unkwon
            # republicar la serie


            # 3 - Actualizar Activated a False
            episodemetadata.activated=False
            episodemetadata.save()

            self.code_return = 0
            self.message_return= 'Episode ' + episodemetadata.episode.asset.asset_id + ' despublicada Correctamente'
            request.session['list_episode_message'] = 'Metadata en ' + episodemetadata.language.name +' de Capitulo ' + episodemetadata.episode.asset.asset_id + ' Despublicado Correctamente'
            request.session['list_episode_flag'] = FLAG_SUCCESS
        except PublishZone.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "PublishZone no Existe. (" + str(e.message) + ")"})
        except EpisodeMetadata.DoesNotExist as e:
            return render(request, 'cawas/error.html',
                          {"message": "Metadata de Capitulo no Existe. (" + str(e.message) + ")"})
        except ApiBackendException as e:
            request.session['list_episode_message'] = "Error al despublicar (" + str(e.value) + ")"
            request.session['list_episode_flag'] = FLAG_ALERT

        return self.code_return


    def publish(self, request, id):

        try:
            md = EpisodeMetadata.objects.get(id=id)
            md.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
            md.queue_status = 'Q'
            md.save()

            #Publica el Episodio
            ph = PublishHelper()
            ph.func_publish_queue(request, md.episode.asset.asset_id, md.language, 'AS', 'Q', datetime.datetime.now().strftime('%Y-%m-%d'))
            ph.func_publish_image(request, md.episode.image)

            # Se vuelve a publicar la SERIE en el idioma del Episodio publicado
            #Si no existe serie en estado publicado, se pub
            if (PublishQueue.objects.filter(item_id=md.episode.serie.asset.asset_id, status__in=['Q','D']).count() < 1):
                ph = PublishHelper()
                ph.func_publish_queue(request, md.episode.serie.asset.asset_id, md.language, 'AS', 'Q', datetime.datetime.now().strftime('%Y-%m-%d'))
                ph.func_publish_image(request, md.vepisode.serie.image)

            request.session['list_episode_message'] = 'Episodio en ' + md.language.name
            request.session['list_episode_flag'] = FLAG_SUCCESS
            self.code_return = 0

        except Exception as e:
            self.code_return = -1
            request.session['list_episode_message'] = 'Error al Guardar Episode Metadata ' + e.message
            request.session['list_episode_flag'] = FLAG_ALERT
            return self.code_return

        request.session['list_episode_message'] = 'Metadata en ' + md.language.name + ' de Capitulo ' + md.episode.asset.asset_id + ' Guardado en Cola de Publicacion'
        request.session['list_episode_flag'] = FLAG_SUCCESS
        self.code_return = 0
        return self.code_return


    def publish_all(self, request,param_episode, param_lang ):
        #Publica nuevamente la Girl para todos los idiomas

        mditems = EpisodeMetadata.objects.filter(episode=param_episode, language=param_lang)
        #Actualizar la fecha de publicacion
        for md in mditems:
            md.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
            md.save()
            #Dejar en cola de publicacion para cada idioma
            ph = PublishHelper()
            ph.func_publish_queue(request, md.episode.asset.asset_id, md.language, 'AS', 'Q', md.publish_date)
            ph.func_publish_image(request, md.episode.image)
            self.code_return = 0

        return self.code_return
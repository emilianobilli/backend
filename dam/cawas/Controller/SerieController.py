import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import Asset, Setting, Serie, Country, SerieMetadata, Category, Episode, EpisodeMetadata,  Language,PublishQueue, PublishZone, Image, Girl,  GirlMetadata, Channel
from ..Helpers.PublishHelper import PublishHelper
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..Helpers.GlobalValues import *
from ..backend_sdk import ApiBackendServer, ApiBackendResource, ApiBackendException
from django.db.models import Q


class SerieController(object):
    code_return = 0

    def add(self, request):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        # VARIABLES LOCALES
        message = ''
        flag = ''
        vgrabarypublicar = ''
        if request.method == 'POST':
            # VARIABLES
            vserie = Serie()
            vimg = Image()

            vasset = Asset()
            vasset.asset_type = "serie"
            vasset.save()

            # Parsear JSON
            strjson = request.POST['varsToJSON']


            decjson = json.loads(strjson.replace('\r','\\r').replace('\n','\\n'))

            try:
                pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
                pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
                base_dir = Setting.objects.get(code='dam_base_dir')
            except Setting.DoesNotExist as e:
                self.code_return = -1
                request.session['list_serie_message'] = 'Error: ' + e.message
                request.session['list_serie_flag'] = FLAG_ALERT
                return self.code_return

            vimg.name = vasset.asset_id
            # IMAGEN Landscape
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
            # FIN IMAGEN

            # Datos de Serie
            vserie.asset = vasset
            vserie.original_title = decjson['Serie']['original_title']
            vserie.year = decjson['Serie']['year']
            if (decjson['Serie']['cast'] is not None):
                vserie.cast = decjson['Serie']['cast']
            if (decjson['Serie']['directors'] is not None):
                vserie.directors = decjson['Serie']['directors']

            vserie.image = vimg
            vserie.save()

            # CARGAR GIRLS
            if (decjson['Serie']['girls'] is not None):
                vgirls = decjson['Serie']['girls']
                for item in vgirls:
                    try:
                        g = Girl.objects.get(pk=item['girl_id'])
                        vserie.girls.add(g)
                    except Girl.DoesNotExist as e:
                        self.code_return = -1
                        request.session['list_serie_message'] = 'Error: ' + e.message
                        request.session['list_serie_flag'] = FLAG_ALERT
                        return self.code_return

            # CARGAR CATEGORIES
            vcategories = decjson['Serie']['categories']
            for item in vcategories:
                try:
                    vserie.category.add(Category.objects.get(pk=item['category_id']))
                except Category.DoesNotExist as e:
                    self.code_return = -1
                    request.session['list_serie_message'] = 'Error: ' + e.message
                    request.session['list_serie_flag'] = FLAG_ALERT
                    return self.code_return


            # CARGAR Countries al Asset
            if (decjson['Serie']['countries'] is not None):
                countries = decjson['Serie']['countries']
                for item in countries:
                    try:
                        country = Country.objects.get(id=item['country_id'])
                        vserie.asset.target_country.add(country)
                    except Country.DoesNotExist as e:
                        request.session['list_serie_message'] = "Error: No Existe Pais (" + str(e.message) + ")"
                        request.session['list_serie_flag'] = FLAG_ALERT
                        self.code_return = -1

            # Channel
            try:
                vserie.channel = Channel.objects.get(pk=decjson['Serie']['channel_id'])
            except Channel.DoesNotExist as e:
                self.code_return = -1
                request.session['list_serie_message'] = 'Error: ' + e.message
                request.session['list_serie_flag'] = FLAG_ALERT
                return self.code_return

            vserie.save()
            message = 'Registrado Correctamente'
            # Fin datos serie

            # BORRAR Y CREAR METADATA
            vseriemetadatas = decjson['Serie']['Seriemetadatas']
            for item in vseriemetadatas:
                smd = SerieMetadata()
                try:
                    smd.language = Language.objects.get(code=item['Seriemetadata']['language'])
                    vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                    smd.title = item['Seriemetadata']['title']
                    smd.summary_short = item['Seriemetadata']['summary_short']
                    smd.summary_long = item['Seriemetadata']['summary_long']
                    smd.serie = vserie
                    smd.publish_date = vschedule_date
                    smd.queue_status = 'Q'
                    smd.save()
                except Language.DoesNotExist as e:
                    self.code_return = -1
                    request.session['list_serie_message'] = 'Error No existe Lenguaje ' + e.message
                    request.session['list_serie_flag'] = FLAG_ALERT
                    return self.code_return



            flag = 'success'
            self.code_return = 0
            request.session['list_serie_message'] = 'Guardado Correctamente'
            request.session['list_serie_flag'] = FLAG_SUCCESS

        # VARIABLES PARA GET - CARGAR GIRL
        try:
            message = ''
            vlanguages = Language.objects.all()
            vgirls = Girl.objects.all()
            vcategories = Category.objects.all()
            vchannels = Channel.objects.all()
            vseries = Serie.objects.all()
            countries = Country.objects.all().order_by('name')
        except Exception as e:
            self.code_return = -1
            request.session['list_serie_message'] = 'Error: ' + e.message
            request.session['list_episode_flag'] = FLAG_ALERT
            return self.code_return

        context = {'message': message, 'flag':flag, 'vgirls': vgirls, 'vlanguages': vlanguages, 'vcategories': vcategories,
                   'vchannels': vchannels, 'vseries': vseries, 'flag':flag, 'countries':countries}
        return render(request, 'cawas/series/add.html', context)




    def edit(self,request, asset_id):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        # VARIABLES LOCALES
        message  = ''
        flag = ''
        vgrabarypublicar=''
        if request.method == 'POST':
            # VARIABLES
            vserie = Serie()
            vimg = Image()
            vasset = Asset()
            # Parsear JSON
            try:
                strjson = request.POST['varsToJSON']
                decjson = json.loads(strjson.replace('\r','\\r').replace('\n','\\n'))
                vasset = Asset.objects.get(asset_id=asset_id)
                vserie = Serie.objects.get(asset=vasset)
                vimg = Image.objects.get(name=vasset.asset_id)
                pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
                pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
                base_dir = Setting.objects.get(code='dam_base_dir')
                print 'flag1'


            except Exception as e:
                self.code_return = -1
                print 'fallo json'
                request.session['list_serie_message'] = 'Error: ' + e.message
                request.session['list_serie_flag'] = FLAG_ALERT
                return self.code_return

            vimg.name = vasset.asset_id
            # IMAGEN Landscape
            print 'debug1'
            if (request.FILES.has_key('ThumbHor')):
                if request.FILES['ThumbHor'].name != '':
                    # TRATAMIENTO DE IMAGEN Landscape
                    print 'debug2'
                    vimg.landscape = request.FILES['ThumbHor']
                    extension = os.path.splitext(vimg.landscape.name)[1]
                    varchivo = pathfilesland.value + vimg.name + extension
                    vimg.landscape.name = varchivo
                    varchivo_server = base_dir.value + varchivo
                    if os.path.isfile(varchivo_server):
                        os.remove(varchivo_server)

            # IMAGEN Landscape
            print 'debug3'
            if (request.FILES.has_key('ThumbVer')):
                if request.FILES['ThumbVer'].name != '':
                    # Landscape
                    print 'debug4'
                    vimg.portrait = request.FILES['ThumbVer']
                    extension = os.path.splitext(vimg.portrait.name)[1]
                    varchivo = pathfilesport.value + vimg.name + extension
                    vimg.portrait.name = varchivo
                    # si existe archivo, lo borra
                    varchivo_server = base_dir.value + varchivo
                    if os.path.isfile(varchivo_server):
                        os.remove(varchivo_server)

            vimg.save()
            print 'flag2'
            # FIN IMAGEN
            vgrabarypublicar = decjson['Serie']['publicar']
            # Datos de Serie
            vserie.asset = vasset
            vserie.original_title = decjson['Serie']['original_title']
            vserie.year = decjson['Serie']['year']

            if (decjson['Serie']['cast'] is not None):
                vserie.cast = decjson['Serie']['cast']

            if (decjson['Serie']['directors'] is not None):
                vserie.directors = decjson['Serie']['directors']

            vserie.image = vimg
            vserie.save()

            # CARGAR GIRLS
            vserie.girls = []
            vserie.save()
            if (decjson['Serie']['girls'] is not None):
                vgirls = decjson['Serie']['girls']
                for item in vgirls:
                    try:
                        g = Girl.objects.get(pk=item['girl_id'])
                        vserie.girls.add(g)
                    except Girl.DoesNotExist as e:
                        self.code_return = -1
                        request.session['list_serie_message'] = 'Error: ' + e.message
                        request.session['list_serie_flag'] = FLAG_ALERT
                        return self.code_return
                vserie.save()
            print 'flag3'
            # CARGAR CATEGORIES
            vserie.category = []
            vserie.save()
            vcategories = decjson['Serie']['categories']
            for item in vcategories:
                try:
                    vserie.category.add(Category.objects.get(pk=item['category_id']))
                except Category.DoesNotExist as e:
                    self.code_return = -1
                    request.session['list_serie_message'] = 'Error: ' + e.message
                    request.session['list_serie_flag'] = FLAG_ALERT
                    return self.code_return

            vserie.asset.target_country = []
            vserie.save()


            #!!!cuando se cambie countries, se debe actualizar los paises en los episodios que pertenecen a la serie!!!
            # CARGAR Countries al Asset
            if (decjson['Serie']['countries'] is not None):
                countries = decjson['Serie']['countries']
                for item in countries:
                    try:
                        country = Country.objects.get(id=item['country_id'])
                        vserie.asset.target_country.add(country)
                    except Country.DoesNotExist as e:
                        request.session['list_serie_message'] = "Error: No Existe Pais (" + str(e.message) + ")"
                        request.session['list_serie_flag'] = FLAG_ALERT
                        self.code_return = -1

            print 'flag4'
            # Channel
            try:
                vserie.channel = Channel.objects.get(pk=decjson['Serie']['channel_id'])
            except Channel.DoesNotExist as e:
                self.code_return = -1
                request.session['list_serie_message'] = 'Error: ' + e.message
                request.session['list_serie_flag'] = FLAG_ALERT
                return self.code_return

            vserie.save()
            message = 'Categoria - Registrado Correctamente'
            print 'flag5'
            # BORRAR Y CREAR METADATA
            vseriemetadatas = decjson['Serie']['Seriemetadatas']

            for item in vseriemetadatas:
                try:
                    vlanguage = Language.objects.get(code=item['Seriemetadata']['language'])
                    smd = SerieMetadata.objects.get(serie=vserie, language=vlanguage)
                except SerieMetadata.DoesNotExist as e:
                    smd = SerieMetadata()
                except Language.DoesNotExist as e:
                    self.code_return = -1
                    request.session['list_serie_message'] = 'Error: ' + e.message
                    request.session['list_serie_flag'] = FLAG_ALERT
                    return self.code_return

                vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                smd.language = vlanguage
                smd.title = item['Seriemetadata']['title']
                smd.summary_short = item['Seriemetadata']['summary_short']
                smd.summary_long = item['Seriemetadata']['summary_long']
                smd.serie = vserie
                smd.publish_date = vschedule_date
                smd.queue_status = 'Q'
                smd.save()


                if (Episode.objects.filter(serie=vserie).count() > 0):
                    print 'ingreso'
                    ph = PublishHelper()
                    ph.func_publish_queue(request, vserie.asset.asset_id, smd.language, 'AS', 'Q',vschedule_date)
                    ph.func_publish_image(request, vimg)
                else:
                    self.code_return = -1
                    request.session['list_serie_message'] = 'No se puede Publicar Serie sin Episodios asignados '
                    request.session['list_serie_flag'] = FLAG_ALERT
                    return self.code_return
                # Fin de POST

            flag = "success"
            self.code_return = 0
            request.session['list_serie_message'] = 'Guardado Correctamente'
            request.session['list_serie_flag'] = FLAG_SUCCESS

        # VARIABLES PARA GET - CARGAR GIRL
        try:
            message = ''
            vlanguages = Language.objects.all()
            vgirls = Girl.objects.all()
            vcategories = Category.objects.all()
            vchannels = Channel.objects.all()
            vseries = Serie.objects.all()
            vasset = Asset.objects.get(asset_id=asset_id)
            vserie = Serie.objects.get(asset=vasset)
            vepisodes = Episode.objects.filter(serie=vserie)

            countries_selected = vserie.asset.target_country.all().order_by('name')
            countries_notselected = Country.objects.exclude(id__in=countries_selected).order_by('name')

            # carga imagenes
            i = len(vserie.image.portrait.name)
            imgport = vserie.image.portrait.name[5:i]
            i = len(vserie.image.landscape.name)
            imgland = vserie.image.landscape.name[5:i]

            vgirlselected = vserie.girls.all()
            vgirlnotselected = Girl.objects.exclude(id__in=vgirlselected)

            vcategoryselected = vserie.category.all()
            vcategorynotselected = Category.objects.exclude(id__in=vcategoryselected)

            # Nuevo diccionario para completar lenguages y metadata
            vlangmetadata = []
            for itemlang in vlanguages:
                vseriemetadata = None
                try:
                    vseriemetadata = SerieMetadata.objects.get(serie=vserie, language=itemlang)
                    vlangmetadata.append(
                        {'checked': True,
                         'code': itemlang.code,
                         'name': itemlang.name,
                         'title': vseriemetadata.title,
                         'summary_short': vseriemetadata.summary_short,
                         'summary_long': vseriemetadata.summary_long,
                         })
                except SerieMetadata.DoesNotExist as a:
                    vlangmetadata.append({'checked': False,
                                          'code': itemlang.code,
                                          'name': itemlang.name,
                                          'title': '',
                                          'summary_short': '',
                                          'summary_long': ''})

        except Exception as e:
            self.code_return = -1
            request.session['list_serie_message'] = 'Error: ' + e.message
            request.session['list_serie_flag'] = FLAG_ALERT
            return self.code_return


        context = {'message': message, 'vgirls': vgirls,
                   'vlanguages': vlanguages,
                   'vcategories': vcategories,
                   'vchannels': vchannels,
                   'vseries': vseries,
                   'vlangmetadata': vlangmetadata,
                   'vserie': vserie,
                   'imgport': imgport, 'imgland': imgland,
                   'vgirlnotselected': vgirlnotselected,
                   'vgirlselected': vgirlselected,
                   'vcategoryselected': vcategoryselected,
                   'vcategorynotselected': vcategorynotselected,
                   'vepisodes':vepisodes,
                   'countries_selected':countries_selected,
                   'countries_notselected':countries_notselected,
                   'message':message
                   }

        return render(request, 'cawas/series/edit.html', context)



    def list(self, request):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        usuario = request.user
        titulo = ''
        page = request.GET.get('page')
        request.POST.get('page')
        filter = False
        message = ''
        flag = ''

        # Filtro de busqueda
        if request.GET.has_key('search'):
            search = request.GET.get('search')
            if search != '':
                filter = True
                registros = SerieMetadata.objects.filter(Q(title__icontains=search) | Q(serie__asset__asset_id__icontains=search)).order_by('-id')

        if filter == False:
            registros = SerieMetadata.objects.all().order_by('-id')
            paginator = Paginator(registros, 25)
            page = request.GET.get('page')
            try:
                registros = paginator.page(page)
            except PageNotAnInteger:
                registros = paginator.page(1)
            except EmptyPage:
                registros = paginator.page(paginator.num_pages)

        if request.session.has_key('list_serie_message'):
            if request.session['list_serie_message'] != '':
                message = request.session['list_serie_message']
                request.session['list_serie_message'] = ''

        if request.session.has_key('list_serie_flag'):
            if request.session['list_serie_flag'] != '':
                flag = request.session['list_serie_flag']
                request.session['list_serie_flag'] = ''


        series = SerieMetadata.objects.all().order_by('-id')

        context = {'message':message, 'flag':flag, 'registros': registros, 'titulo': titulo, 'usuario': usuario}
        return render(request, 'cawas/series/list.html', context)



    def publish(self, request, id):
        #Publicar la Serie
        try:
            md = SerieMetadata.objects.get(id=id)
            #md.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
            md.queue_status = 'Q'
            md.save()

            ph = PublishHelper()
            ph.func_publish_queue(request, md.serie.asset.asset_id, md.language, 'AS', 'Q',datetime.datetime.now().strftime('%Y-%m-%d'))
            #Publicar los episodios de la serie
            episodes = Episode.objects.filter(serie=md.serie)
            for e in episodes:
                #recorrer la metadata en el idioma que se selecciono la serie
                episodemetadatas = EpisodeMetadata.objects.filter(episode=e, language=md.language)
                for em in episodemetadatas:
                    ph = PublishHelper()
                    ph.func_publish_queue(request, em.episode.asset.asset_id, em.language, 'AS', 'Q', datetime.datetime.now().strftime('%Y-%m-%d'))
                    ph.func_publish_image(request, em.episode.image)

            ph = PublishHelper()
            ph.func_publish_queue(request, md.serie.asset.asset_id, md.language, 'AS', 'Q',datetime.datetime.now().strftime('%Y-%m-%d'))
            request.session['list_serie_message'] = 'Serie en ' + md.language.name + ' Guardado en Cola de Publicacion'
            request.session['list_serie_flag'] = FLAG_SUCCESS
            self.code_return = 0
        except Exception as e:
            self.code_return = -1
            request.session['list_serie_message'] = "Error al despublicar (" + str(e.message) + ")"
            request.session['list_serie_flag'] = FLAG_ALERT
            return self.code_return

        return self.code_return


    # despublicar
    def unpublish(self, request, id):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        try:
            seriemetadata = SerieMetadata.objects.get(id=id)
            vasset_id = seriemetadata.serie.asset.asset_id

            # 1 - VERIFICAR, si estado de publicacion DE SERIE esta en Q, se debe eliminar

            if PublishQueue.objects.filter(item_id=vasset_id, status='Q').count() > 0:
                PublishQueue.objects.filter(item_id=vasset_id, status='Q').delete()


            # 2 - Realizar delete al backend de la Serie
            setting = Setting.objects.get(code='backend_asset_url')
            api_key = Setting.objects.get(code='backend_api_key')
            vzones = PublishZone.objects.filter(enabled=True)
            #despublica la serie
            for zone in vzones:
                abr = ApiBackendResource(zone.backend_url, setting.value, api_key.value)
                param = {"asset_id": seriemetadata.serie.asset.asset_id,
                         "asset_type":"show",
                         "lang": seriemetadata.language.code}
                abr.delete(param)


            #Obtener los episodios que pertenecen a esta serie
            #publicar nuevamente los episodes

            episodes = Episode.objects.filter(serie=seriemetadata.serie)
            for item in episodes:

                try:
                    # Despublicar los episodios que tengan el mismo idioma que la serie.
                    mde = EpisodeMetadata.objects.filter(episode=item, language=seriemetadata.language)
                    for episodemetadata in mde:

                        # VERIFICAR SI estado de publicacion de EPISODE esta en Q, se debe eliminar

                        if PublishQueue.objects.filter(item_id=episodemetadata.episode.asset.asset_id, status='Q').count() > 0:
                            PublishQueue.objects.filter(item_id=episodemetadata.episode.asset.asset_id, status='Q').delete()


                        for zone in vzones:
                            abr = ApiBackendResource(zone.backend_url, setting.value, api_key.value)
                            param = {"asset_id": episodemetadata.episode.asset.asset_id,
                                     "asset_type": "show",
                                     "lang": episodemetadata.language.code}
                            abr.delete(param)
                        episodemetadata.activated = False
                        episodemetadata.save()

                except ApiBackendException as e:
                    request.session['list_serie_message'] = "Error al Despublicar Episodios en Backend(" + str(e.value) + ")"
                    request.session['list_serie_flag'] = FLAG_ALERT
                    self.code_return = -1
                    return self.code_return

                except PublishQueue.DoesNotExist as e:
                    request.session['list_serie_message'] = "No existen PublishQueue para eliminar (" + str(e.value) + ")"
                    request.session['list_serie_flag'] = FLAG_ALERT
                    self.code_return = -1
                    return self.code_return

                except Exception as e:
                    request.session['list_serie_message'] = "Error General al Despublicar Episodios(" + str(e.value) + ")"
                    request.session['list_serie_flag'] = FLAG_ALERT
                    self.code_return = -1
                    return self.code_return

            # 3 - Actualizar Activated a False
            seriemetadata.activated = False
            seriemetadata.save()

            # esto es para que se actualice el campo "episodes" en el backend
            serie = seriemetadata.serie
            serie.save()


            self.code_return = 0
            request.session['list_serie_message'] = 'Metadata '+ str(seriemetadata.id) + ' de Serie '+ str(seriemetadata.serie.asset.asset_id)+ ' Despublicado Correctamente'
            request.session['list_serie_flag'] = FLAG_SUCCESS

        except PublishZone.DoesNotExist as e:
            request.session['list_serie_message'] = "No existe Publish Zone (" + str(e.value) + ")"
            request.session['list_serie_flag'] = FLAG_ALERT
            self.code_return = -1
            return self.code_return

        except SerieMetadata.DoesNotExist as e:
            request.session['list_serie_message'] = "No Existe Metadata para Serie (" + str(e.value) + ")"
            request.session['list_serie_flag'] = FLAG_ALERT
            self.code_return = -1
            return self.code_return

        except ApiBackendException as e:
            request.session['list_serie_message'] = "Error al despublicar Backend(" + str(e.value) + ")"
            request.session['list_serie_flag'] = FLAG_ALERT
            self.code_return = -1
            return self.code_return



    def publish_all(self, request, param_serie, param_lang ):


        mditems = SerieMetadata.objects.filter(serie=param_serie, language=param_lang)
        #Actualizar la fecha de publicacion
        for md in mditems:
            #md.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
            md.activated = True
            md.save()
            #Dejar en cola de publicacion para cada idioma
            ph = PublishHelper()
            ph.func_publish_queue(request, md.serie.asset.asset_id, md.language, 'AS', 'Q',datetime.datetime.now().strftime('%Y-%m-%d'))
            ph.func_publish_image(request, md.serie.image)
            self.code_return = 0


        return self.code_return
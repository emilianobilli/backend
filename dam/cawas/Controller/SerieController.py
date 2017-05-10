import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import Asset, Setting, Serie, SerieMetadata, Category, Episode, EpisodeMetadata,  Language,PublishQueue, PublishZone, Image, Girl,  GirlMetadata, Channel
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
            decjson = json.loads(strjson)
            try:
                pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
                pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            except Setting.DoesNotExist as e:
                self.code_return = -1
                request.session['list_serie_message'] = 'Error: ' + e.message
                request.session['list_serie_flag'] = FLAG_ALERT
                return self.code_return

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
            # FIN IMAGEN

            # Datos de Serie
            vserie.asset = vasset
            vserie.original_title = decjson['Serie']['original_title']
            vserie.year = decjson['Serie']['year']
            vserie.cast = decjson['Serie']['cast']
            vserie.directors = decjson['Serie']['directors']
            vserie.image = vimg
            vserie.save()

            # CARGAR GIRLS
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
                except Language.DoesNotExist as e:
                    self.code_return = -1
                    request.session['list_serie_message'] = 'Error No existe Lenguaje ' + e.message
                    request.session['list_serie_flag'] = FLAG_ALERT
                    return self.code_return

                vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                smd.title = item['Seriemetadata']['title']
                smd.summary_short = item['Seriemetadata']['summary_short']
                smd.summary_long = item['Seriemetadata']['summary_long']
                smd.serie = vserie
                smd.publish_date = vschedule_date
                smd.save()


            flag = 'success'


        # VARIABLES PARA GET - CARGAR GIRL
        try:
            message = ''
            vlanguages = Language.objects.all()
            vgirls = Girl.objects.all()
            vcategories = Category.objects.all()
            vchannels = Channel.objects.all()
            vseries = Serie.objects.all()

        except Exception as e:
            self.code_return = -1
            request.session['list_serie_message'] = 'Error: ' + e.message
            request.session['list_episode_flag'] = FLAG_ALERT
            return self.code_return

        self.code_return = 0
        request.session['list_serie_message'] = 'Guardado Correctamente'
        request.session['list_serie_flag'] = FLAG_SUCCESS

        context = {'message': message, 'flag':flag, 'vgirls': vgirls, 'vlanguages': vlanguages, 'vcategories': vcategories,
                   'vchannels': vchannels, 'vseries': vseries, 'flag':flag}
        return render(request, 'cawas/series/add.html', context)




    def edit(self,request, asset_id):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        # VARIABLES LOCALES
        message = ''
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
                decjson = json.loads(strjson)
                vasset = Asset.objects.get(asset_id=asset_id)
                vserie = Serie.objects.get(asset=vasset)
                vimg = Image.objects.get(name=vasset.asset_id)
                pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
                pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            except Exception as e:
                self.code_return = -1
                request.session['list_serie_message'] = 'Error: ' + e.message
                request.session['list_serie_flag'] = FLAG_ALERT
                return self.code_return
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
            # FIN IMAGEN
            vgrabarypublicar = decjson['Serie']['publicar']
            # Datos de Serie
            vserie.asset = vasset
            vserie.original_title = decjson['Serie']['original_title']
            vserie.year = decjson['Serie']['year']
            vserie.cast = decjson['Serie']['cast']
            vserie.directors = decjson['Serie']['directors']
            vserie.image = vimg
            vserie.save()

            # CARGAR GIRLS
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
                smd.save()
                metadatas = SerieMetadata.objects.filter(serie=vserie, language=smd.language)
                # Si no existe METADATA, se genera
                if metadatas.count() < 1:
                    # Publica en PublishQueue
                    if vgrabarypublicar == '1':
                        if (Episode.objects.filter(serie=vserie).count() > 0):
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

        self.code_return = 0
        request.session['list_serie_message'] = 'Guardado Correctamente'
        request.session['list_serie_flag'] = FLAG_SUCCESS

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
                   'flag':flag
                   }
        # return render(request, 'cawas/pruebas/subir_img.html', context)

        # Serie - OK
        # SerieMetadata -
        # Publishqueue -
        # Imagequeue - s

        return render(request, 'cawas/series/edit.html', context)



    def list(self, request):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        usuario = request.user
        titulo = ''
        page = request.GET.get('page')
        request.POST.get('page')
        series_list = None

        message = ''
        flag = ''

        if request.session.has_key('list_serie_message'):
            if request.session['list_serie_message'] != '':
                message = request.session['list_serie_message']
                request.session['list_serie_message'] = ''

        if request.session.has_key('list_serie_flag'):
            if request.session['list_serie_flag'] != '':
                flag = request.session['list_serie_flag']
                request.session['list_serie_flag'] = ''

        if request.POST:
            titulo = request.POST['inputTitulo']
            selectestado = request.POST['selectestado']
            # FILTROS
            if titulo != '':
                assets = Asset.objects.filter(asset_id__icontains=titulo)
                series_sel = Serie.objects.filter(Q(original_title__icontains=titulo) | Q(asset__in=assets))
            else:
                series_sel = Serie.objects.all()

            if selectestado != '':
                series_list = SerieMetadata.objects.filter(serie__in=series_sel, publish_status=selectestado).order_by('serie_id')
            else:
                series_list = SerieMetadata.objects.filter(serie__in=series_sel).order_by('serie_id')


        if series_list is None:
            series_list = SerieMetadata.objects.all().order_by('serie_id')

        paginator = Paginator(series_list, 20)  # Show 25 contacts per page
        try:
            series = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            series = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            series = paginator.page(paginator.num_pages)

        context = {'message':message, 'flag':flag, 'registros': series, 'titulo': titulo, 'usuario': usuario}
        return render(request, 'cawas/series/list.html', context)



    def publish(self, request, id):
        #Publicar la Serie
        try:

            md = SerieMetadata.objects.get(id=id)
            md.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
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
            request.session['list_serie_message'] = 'Serie en ' + md.language.name + ' de Publicada Correctamente'
            request.session['list_serie_flag'] = FLAG_SUCCESS
            self.code_return = 0
        except Exception as e:
            self.code_return = -1
            request.session['list_serie_message'] = "Error al despublicar (" + str(e.message) + ")"
            request.session['list_serie_flag'] = FLAG_ALERT
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
            publishs = PublishQueue.objects.filter(item_id=vasset_id, status='Q')
            if publishs.count > 0:
                publishs.delete()


            # 2 - Realizar delete al backend de la Serie
            setting = Setting.objects.get(code='backend_asset_url')
            api_key = Setting.objects.get(code='backend_api_key')
            vzones = PublishZone.objects.filter(enabled=True)

            for zone in vzones:
                abr = ApiBackendResource(zone.backend_url, setting.value, api_key.value)
                param = {"asset_id": seriemetadata.serie.asset.asset_id,
                         "asset_type":"show",
                         "lang": seriemetadata.language.code}
                abr.delete(param)


            #Obtener los episodios que pertenecen a esta serie
            #publicar nuevamente los episodes
            print 'despublicacion de episodes'
            episodes = Episode.objects.filter(serie=seriemetadata.serie)
            for item in episodes:
                print 'episode: ' + item.asset.asset_id
                try:
                    # Despublicar los episodios que tengan el mismo idioma que la serie.
                    mde = EpisodeMetadata.objects.filter(episode=item, language=seriemetadata.language)
                    for episodemetadata in mde:
                        print 'episodemetadata: ' + episodemetadata.episode.asset.asset_id
                        # VERIFICAR SI estado de publicacion de EPISODE esta en Q, se debe eliminar
                        publishs = PublishQueue.objects.filter(item_id=episodemetadata.episode.asset.asset_id, status='Q')
                        if publishs.count > 0:
                            publishs.delete()

                        for zone in vzones:
                            abr = ApiBackendResource(zone.backend_url, setting.value, api_key.value)
                            param = {"asset_id": episodemetadata.episode.asset.asset_id,
                                     "asset_type": "show",
                                     "lang": episodemetadata.language.code}
                            abr.delete(param)
                        episodemetadata.activated = False
                        episodemetadata.save()
                except Exception as e:
                    request.session['list_serie_message'] = "Error al Despublicar (" + str(e.value) + ")"
                    request.session['list_serie_flag'] = FLAG_ALERT
                    self.code_return = -1
                    return self.code_return

            # 3 - Actualizar Activated a False
            seriemetadata.activated = False
            seriemetadata.save()

            self.code_return = 0
            request.session['list_serie_message'] = 'Metadata '+ str(seriemetadata.id) + ' de Serie '+ str(seriemetadata.serie.asset.asset_id)+ ' Despublicado Correctamente'
            request.session['list_serie_flag'] = FLAG_SUCCESS

        except PublishZone.DoesNotExist as e:
            request.session['list_serie_message'] = "Error al Publicar (" + str(e.value) + ")"
            request.session['list_serie_flag'] = FLAG_ALERT
            self.code_return = -1
            return self.code_return

        except SerieMetadata.DoesNotExist as e:
            request.session['list_serie_message'] = "Error al Publicar (" + str(e.value) + ")"
            request.session['list_serie_flag'] = FLAG_ALERT
            self.code_return = -1
            return self.code_return
        except ApiBackendException as e:
            request.session['list_serie_message'] = "Error al despublicar (" + str(e.value) + ")"
            request.session['list_serie_flag'] = FLAG_ALERT

        return self.code_return



    def publish_all(self, request, param_serie, param_lang ):


        mditems = SerieMetadata.objects.filter(serie=param_serie, language=param_lang)
        #Actualizar la fecha de publicacion
        for md in mditems:
            md.publish_date = datetime.datetime.now().strftime('%Y-%m-%d')
            md.activated = True
            md.save()
            #Dejar en cola de publicacion para cada idioma
            ph = PublishHelper()
            ph.func_publish_queue(request, md.serie.asset.asset_id, md.language, 'AS', 'Q', md.publish_date)
            ph.func_publish_image(request, md.serie.image)
            self.code_return = 0


        return self.code_return
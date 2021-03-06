import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import Asset, Setting, Girl, Block,Country, PublishQueue,  Category, GirlMetadata, EpisodeMetadata, SerieMetadata, MovieMetadata, PublishZone,  Language, Image, Channel, Device, Serie, Movie, Episode
from ..Helpers.PublishHelper import PublishHelper
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from MovieController import MovieController
from SerieController import SerieController
from GirlController import GirlController
from EpisodeController import EpisodeController
from ..Helpers.GlobalValues import *
from ..backend_sdk import ApiBackendServer, ApiBackendResource, ApiBackendException
from django.db.models import Q

class BlockController(object):

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
            vblock = Block()

            # Parsear JSON
            try:
                strjson = request.POST['varsToJSON']
                decjson = json.loads(strjson.replace('\r','\\r').replace('\n','\\n'))
                vblock.name = decjson['Block']['name']
                vblock.order = decjson['Block']['order']

                if (decjson['Block']['tipo'] is not None):
                    vblock.type = decjson['Block']['tipo']

                if (decjson['Block']['query'] is not None):
                    vblock.query = decjson['Block']['query']

                vgrabarypublicar = decjson['Block']['publicar']
                vschedule_date = datetime.datetime.strptime(decjson['Block']['publish_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
                if vschedule_date is None:
                    vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                vblock.publish_date = vschedule_date

                vblock.language = Language.objects.get(code=decjson['Block']['language'])
                vblock.queue_status = 'Q'
                if decjson['Block']['channel_id'] is not None:
                    vblock.channel = Channel.objects.get(pk=decjson['Block']['channel_id'])

                vblock.target_device = Device.objects.get(pk=int(decjson['Block']['target_device_id']))
                vblock.save()


                # CARGAR Countries al Asset
                if (decjson['Block']['countries'] is not None):
                    countries = decjson['Block']['countries']
                    for item in countries:
                        try:
                            country = Country.objects.get(id=item['country_id'])
                            vblock.target_country.add(country)
                        except Country.DoesNotExist as e:
                            request.session['list_block_message'] = "Error: No Existe Pais (" + str(e.message) + ")"
                            request.session['list_block_flag'] = FLAG_ALERT
                            self.code_return = -1


                vassets = decjson['Block']['assets']
                for item in vassets:
                    try:
                        asset_id = item['asset_id']
                        vasset = Asset.objects.get(asset_id=asset_id)
                        vblock.assets.add(vasset)
                    except Asset.DoesNotExist as e:
                        return render(request, 'cawas/error.html',
                                      {"message": "No existe Asset. " + asset_id + "  (" + e.message + ")"})

                vblock.save()
            except Setting.DoesNotExist as e:
                self.code_return = -1
                request.session['list_block_message'] = 'Error: No existe Configuracion. ' + e.message
                request.session['list_block_flag'] = FLAG_ALERT
                return self.code_return
            except Image.DoesNotExist as e:
                self.code_return = -1
                request.session['list_block_message'] = 'Error: No Existe imagen asociada a la serie. ' + e.message
                request.session['list_block_flag'] = FLAG_ALERT
                return self.code_return
            except Exception as e:
                self.code_return = -1
                request.session['list_block_message'] = 'Error: ' + str(e)
                request.session['list_block_flag'] = FLAG_ALERT
                return self.code_return

            # CARGAR ASSETS
            if vgrabarypublicar == '1':
                vassets = decjson['Block']['assets']
                for item in vassets:
                    try:
                        asset_id = item['asset_id']
                        vasset = Asset.objects.get(asset_id=asset_id)
                        ph = PublishHelper()

                        # Publica en PublishQueue
                        # Eliminar cola de publicacion para el item en estado Queued
                        ph.func_publish_queue(request, asset_id, vblock.language, 'AS', 'Q', vschedule_date)

                    except Asset.DoesNotExist as e:
                        self.code_return = -1
                        request.session['list_block_message'] = 'Error: No existe Asset. ' + e.message
                        request.session['list_block_flag'] = FLAG_ALERT
                        return self.code_return

                vblock.queue_status = 'Q'
                vblock.save()
                ph = PublishHelper()
                ph.func_publish_queue(request, vblock.block_id, vblock.language, 'BL', 'Q', vblock.publish_date)
                self.code_return = 0

            request.session['list_block_message'] = 'Guardado Correctamente.'
            request.session['list_block_flag'] = FLAG_SUCCESS

            return render(request, 'cawas/blocks/add.html')
            # Fin datos Bloque

        # Variables Para GET
        vblocks = Block.objects.all().order_by('name')
        vchannels = Channel.objects.all().order_by('name')
        vdevices = Device.objects.all().order_by('name')
        vgirls = Girl.objects.all().order_by('name')
        vlanguages = Language.objects.all()
        vmovies = Movie.objects.all().order_by('original_title')
        vcapitulos = Episode.objects.all().order_by('original_title')
        vseries = Serie.objects.all().order_by('original_title')
        countries = Country.objects.all().order_by('name')

        context = {'message': message,
                   'vblocks': vblocks,
                   'vchannels': vchannels,
                   'vdevices': vdevices,
                   'vgirls': vgirls,
                   'vlanguages': vlanguages,
                   'vseries': vseries,
                   'vmovies': vmovies,
                   'vcapitulos': vcapitulos,
                   'countries':countries,
                   'block_type':BLOCK_TYPE}
        return render(request, 'cawas/blocks/add.html', context)




    def edit(self, request, block_id):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))
        vblock = Block()
        # VARIABLES LOCALES
        message = ''
        vflag = ''
        vschedule_date = ''
        if request.method == 'POST':

            # Parsear JSON
            try:
                strjson = request.POST['varsToJSON']
                decjson = json.loads(strjson.replace('\r','\\r').replace('\n','\\n'))
                vblock = Block.objects.get(block_id=decjson['Block']['block_id'])
                vblock.name = decjson['Block']['name']
                vblock.order = decjson['Block']['order']
                vschedule_date = datetime.datetime.strptime(decjson['Block']['publish_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
                vblock.publish_date = vschedule_date
                vblock.language = Language.objects.get(code=decjson['Block']['language'])
                if decjson['Block']['channel_id'] is not None:
                    vblock.channel = Channel.objects.get(pk=decjson['Block']['channel_id'])

                if (decjson['Block']['tipo'] is not None):
                    vblock.type = decjson['Block']['tipo']

                if (decjson['Block']['query'] is not None):
                    vblock.query = decjson['Block']['query']

                vdevice = Device.objects.get(pk=int(decjson['Block']['target_device_id']))

                vblock.target_device_id = int(decjson['Block']['target_device_id'])
                vblock.queue_status = 'Q'
                vblock.save()
            except Exception as e:
                self.code_return = -1
                request.session['list_block_message'] = 'Error: ' + str(e)
                request.session['list_block_flag'] = FLAG_ALERT
                return self.code_return

            vblock.target_country= []
            # CARGAR Countries al Asset
            if (decjson['Block']['countries'] is not None):
                countries = decjson['Block']['countries']
                for item in countries:
                    try:
                        country = Country.objects.get(id=item['country_id'])
                        vblock.target_country.add(country)
                    except Country.DoesNotExist as e:
                        request.session['list_block_message'] = "Error: No Existe Pais (" + str(e.message) + ")"
                        request.session['list_block_flag'] = FLAG_ALERT
                        self.code_return = -1

            # CARGAR NUEVOS ASSETS SELECCIONADOS
            assetall = []

            vassets = decjson['Block']['assets']
            for itemactual in vassets:
                if itemactual['asset_id'] not in assetall:
                    assetall.append(itemactual['asset_id'])

            for itemactual in vblock.assets.all():
                if itemactual.asset_id not in assetall:
                    assetall.append(itemactual.asset_id)

            # Bloque en Cawas
            vblock.assets.clear()
            for item in vassets:
                try:
                    asset_id = item['asset_id']
                    vasset = Asset.objects.get(asset_id=asset_id)
                    vblock.assets.add(vasset)
                except Asset.DoesNotExist as e:
                    return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})
            vblock.save()

            # Publicacion
            for item in assetall:
                try:
                    ph = PublishHelper()
                    print item
                    ph.func_publish_queue(request, item, vblock.language, 'AS', 'Q', vblock.publish_date)
                except Asset.DoesNotExist as e:
                    request.session['list_block_message'] = 'Error: '+ e.message
                    request.session['list_block_flag'] = FLAG_ALERT
                    return  -1

            ph = PublishHelper()
            ph.func_publish_queue(request, vblock.block_id, vblock.language, 'BL', 'Q', vblock.publish_date)
            context = {"flag": "success"}
            self.code_return = 0
            request.session['list_block_message'] = 'Guardado Correctamente.'
            request.session['list_block_flag'] = FLAG_SUCCESS
            return render(request, 'cawas/blocks/edit.html', context)
            # Fin datos Bloque

        try:
            print "block_id" + block_id
            vblock = Block.objects.get(block_id=block_id)
            vassetselect = vblock.assets.all()
            #
            vmovienotselect = Movie.objects.exclude(asset__in=vassetselect).order_by('original_title')
            vserienotselect = Serie.objects.exclude(asset__in=vassetselect).order_by('original_title')
            vgirlnotselect = Girl.objects.exclude(asset__in=vassetselect)
            vepisodenotselect = Episode.objects.exclude(asset__in=vassetselect)

            vmovieselect = Movie.objects.filter(asset__in=vassetselect)
            vserieselect = Serie.objects.filter(asset__in=vassetselect)
            vgirlselect = Girl.objects.filter(asset__in=vassetselect)
            vepisodeselect = Episode.objects.filter(asset__in=vassetselect)

            countries_selected = vblock.target_country.all().order_by('name')
            countries_notselected = Country.objects.exclude(id__in=countries_selected).order_by('name')

        except Block.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Bloque2. (" + e.message + ")"})

        # Variables Para GET
        vchannels = Channel.objects.all()
        vseries = Serie.objects.all()
        vgirls = Girl.objects.all()
        vlanguages = Language.objects.all()
        vdevices = Device.objects.all()
        context = {'message': message,
                   'vchannels': vchannels,
                   'vgirls': vgirls,
                   'vlanguages': vlanguages,
                   'vseries': vseries,
                   'vblock': vblock,
                   'vdevices':vdevices,
                   'vmovienotselect': vmovienotselect,
                   'vgirlnotselect': vgirlnotselect,
                   'vepisodenotselect': vepisodenotselect,
                   'vmovieselect': vmovieselect,
                   'vgirlselect': vgirlselect,
                   'vepisodeselect': vepisodeselect,
                   'vserienotselect': vserienotselect,
                   'vserieselect': vserieselect,
                   'countries_selected':countries_selected,
                   'countries_notselected':countries_notselected,
                   'block_type': BLOCK_TYPE
                   }
        return render(request, 'cawas/blocks/edit.html', context)




    def list(self,request):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        usuario = request.user
        message = ''
        titulo = ''
        flag =''
        page = request.GET.get('page')
        request.POST.get('page')
        filter = False

        # Filtro de busqueda
        if request.GET.has_key('search1'):
            search = request.GET.get('search1')
            if search != '':
                filter = True
                registros = Block.objects.filter(
                    Q(block_id__icontains=search) | Q(name__icontains=search)).order_by('-id')

        if filter == False:
            registros = Block.objects.all().order_by('-id')
            paginator = Paginator(registros, 25)
            page = request.GET.get('page')
            try:
                registros = paginator.page(page)
            except PageNotAnInteger:
                registros = paginator.page(1)
            except EmptyPage:
                registros = paginator.page(paginator.num_pages)

        if request.session.has_key('list_block_message'):
            if request.session['list_block_message'] != '':
                message = request.session['list_block_message']
                request.session['list_block_message'] = ''

        if request.session.has_key('list_block_flag'):
            if request.session['list_block_flag'] != '':
                flag = request.session['list_block_flag']
                request.session['list_block_flag'] = ''

        blocks = Block.objects.all().order_by('-id')
        context = {'message': message, 'flag':flag,  'registros': registros, 'titulo': titulo, 'usuario': usuario}
        return render(request, 'cawas/blocks/list.html', context)




    # despublicar
    def unpublish(self, request, id):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        try:
            block = Block.objects.get(id=id)
            #1 - quitar la asociacion

            #Si el Bloque no fue publicado, se elimina de cawas y sus relaciones
            if not block.activated:
                block.delete()
                self.code_return=0
                request.session['list_block_message'] = 'Bloque Eliminado Correctamente '
                request.session['list_block_flag'] = FLAG_SUCCESS
                return self.code_return

            assetsblock = block.assets.all()

            #print 'assetblock: ' + str(assetsblock)
            # 2 - VERIFICAR, Si bloque esta encolado, se elimina de cola de publicacion
            publishs = PublishQueue.objects.filter(item_id=block.block_id, status='Q')
            if publishs.count > 0:
                publishs.delete()
                print 'publish.delete(): '

            # 3 - Publicar los assets que pertenecen al Bloque
            #vschedule_date = datetime.datetime.strptime(decjson['Block']['publish_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
            for item in assetsblock:
                # enconlar los assets
                if item.asset_type =="movie":
                    movie = Movie.objects.get(asset=item)
                    ctr = MovieController()
                    ctr.publish_all(request, param_movie=movie, param_lang=block.language)
                    print 'publica movie: '

                if item.asset_type == "serie":
                    serie = Serie.objects.get(asset=item)
                    ctr = SerieController()
                    ctr.publish_all(request, param_serie=serie, param_lang=block.language)
                    print 'publica serie: '
                if item.asset_type == "episode":
                    episode = Episode.objects.get(asset=item)
                    ctr = EpisodeController()
                    ctr.publish_all(request, param_episode=episode, param_lang=block.language)
                    print 'publica episode: '
                if item.asset_type == "girl":
                    girl = Girl.objects.get(asset=item)
                    ctr = GirlController()
                    ctr.publish_all(request, param_girl=girl, param_lang=block.language)
                    print 'publica girl: '

            # 4 - Realizar delete al backend
            setting = Setting.objects.get(code='backend_block_url')
            api_key = Setting.objects.get(code='backend_api_key')
            vzones = PublishZone.objects.filter(enabled=True)
            for zone in vzones:
                abr = ApiBackendResource(zone.backend_url, setting.value, api_key.value)
                param = {"block_id": block.block_id,
                         "lang": block.language.code}
                abr.delete(param)

            # 3 - Actualizar Activated a False
            #block.assets = []
            #block.activated = False
            #block.save()

            # se elimina el bloque de cawas
            block.delete()
            self.code_return = 0
            request.session['list_block_message'] = 'Bloque Eliminado y Despublicado Correctamente '
            request.session['list_block_flag'] = FLAG_SUCCESS

        except PublishZone.DoesNotExist as e:
            request.session['list_block_message'] = "Error al despublicar (" + str(e.message) + ")"
            request.session['list_block_flag'] = FLAG_ALERT
            self.code_return = -1

        except Block.DoesNotExist as e:
            request.session['list_block_message'] = "Error al despublicar (" + str(e.message) + ")"
            request.session['list_block_flag'] = FLAG_ALERT
            self.code_return = -1
        except Setting.DoesNotExist as e:
            request.session['list_block_message'] = "Error al despublicar (" + str(e.message) + ")"
            request.session['list_block_flag'] = FLAG_ALERT
            self.code_return = -1

        except ApiBackendException as e:
            request.session['list_block_message'] = "Error al despublicar (" + str(e.value) + ")"
            request.session['list_block_flag'] = FLAG_ALERT
        except Exception as e:
            request.session['list_block_message'] = "Error al despublicar (" + str(e) + ")"
            request.session['list_block_flag'] = FLAG_ALERT

        return self.code_return



    def publish(self, request, id):
        #Publicar la Serie
        block = Block.objects.get(id = id)
        vpublish_date           = datetime.datetime.now().strftime('%Y-%m-%d')
        block.queue_status = 'Q'
        block.save()
       # ENCOLA LOS ASSETS QUE CORRESPONDEN AL BLOQUE, SOLO en el IDIOMA QUE SE SELECCIONO
        vassets = block.assets.all()
        for item in vassets:
            try:
                asset_id = item.asset_id
                ph = PublishHelper()
                if (PublishQueue.objects.filter(item_id=item.asset_id, status='Q').count() < 1 ):
                    if (item.asset_type=='movie'):
                        registro = Movie.objects.get(asset = item)
                        ph.func_publish_image(request, registro.image)

                    if (item.asset_type=='girl'):
                        print 'isgirl' + item.asset_id
                        registro = Girl.objects.get(asset = item)
                        ph.func_publish_image(request, registro.image)

                    if (item.asset_type=='episode'):
                        registro = Episode.objects.get(asset = item)
                        ph.func_publish_image(request, registro.image)

                    if (item.asset_type=='serie'):
                        registro = Serie.objects.get(asset = item)
                        ph.func_publish_image(request, registro.image)

                ph.func_publish_queue(request, asset_id, block.language, 'AS', 'Q', vpublish_date)

            except Asset.DoesNotExist as e:
                request.session['list_block_message'] = "Error: (" + str(e.message) + ")"
                request.session['list_block_flag'] = FLAG_ALERT
                self.code_return = -1

            except Girl.DoesNotExist as e:
                request.session['list_block_message'] = "Error: (" + str(e.message) + ")"
                request.session['list_block_flag'] = FLAG_ALERT
                self.code_return = -1

        ph = PublishHelper()
        ph.func_publish_queue(request, block.block_id, block.language, 'BL', 'Q', block.publish_date)

        request.session['list_block_message'] = 'Bloque en ' + block.language.name + ' Guardado en Cola de Publicacion'
        request.session['list_block_flag'] = FLAG_SUCCESS
        self.code_return = 0

        return self.code_return


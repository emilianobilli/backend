import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import Asset, Setting, Girl, Block, PublishQueue,  Category, GirlMetadata, EpisodeMetadata, SerieMetadata, MovieMetadata, PublishZone,  Language, Image, Channel, Device, Serie, Movie, Episode
from ..Helpers.PublishHelper import PublishHelper
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from MovieController import MovieController
from SerieController import SerieController
from GirlController import GirlController
from EpisodeController import EpisodeController
from ..Helpers.GlobalValues import *
from backend_sdk import ApiBackendServer, ApiBackendResource
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
        if request.method == 'POST':
            # VARIABLES
            vblock = Block()
            # Parsear JSON
            try:
                strjson = request.POST['varsToJSON']
                decjson = json.loads(strjson)
                # pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
                # pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
                vblock.name = decjson['Block']['name']
                vschedule_date = datetime.datetime.strptime(decjson['Block']['publish_date'], '%d-%m-%Y').strftime(
                    '%Y-%m-%d')
                vblock.publish_date = vschedule_date
                vblock.language = Language.objects.get(code=decjson['Block']['language'])
                vblock.channel = Channel.objects.get(pk=decjson['Block']['channel_id'])

                print "Device:" + str(decjson['Block']['target_device_id'])
                vblock.target_device = Device.objects.get(pk=int(decjson['Block']['target_device_id']))
                vblock.save()
                # vblock.target_device = Device.objects.get(pk=decjson['Block']['target_device_id'])

            except Setting.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No Existe Setting. (" + e.message + ")"})
            except Serie.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No Existe Serie. (" + e.message + ")"})
            except Image.DoesNotExist as e:
                return render(request, 'cawas/error.html',
                              {"message": "No Existe Imagen Asociada a la Serie. (" + e.message + ")"})
            except Language.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe LENGUAJE. (" + e.message + ")"})
            except Channel.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Channel. (" + e.message + ")"})
            except Device.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Device. (" + e.message + ")"})

            # CARGAR ASSETS
            vassets = decjson['Block']['assets']
            for item in vassets:
                try:
                    asset_id = item['asset_id']
                    vasset = Asset.objects.get(asset_id=asset_id)
                    vblock.assets.add(vasset)
                    # Publica en PublishQueue
                    ph = PublishHelper()
                    ph.func_publish_queue(request, asset_id, vblock.language, 'AS', 'Q', vblock.publish_date)

                except Asset.DoesNotExist as e:
                    return render(request, 'cawas/error.html',
                                  {"message": "No existe Asset. " + asset_id + "  (" + e.message + ")"})

            vblock.save()
            ph = PublishHelper()
            ph.func_publish_queue(request, vblock.block_id, vblock.language, 'BL', 'Q', vblock.publish_date)
            #func_publish_queue(vblock.block_id, vblock.language, 'BL', 'Q', vblock.publish_date)
            context = {"flag": "success"}
            return render(request, 'cawas/blocks/add.html', context)
            # Fin datos Bloque

        # Variables Para GET
        vblocks = Block.objects.all()
        vchannels = Channel.objects.all()
        vdevices = Device.objects.all()
        vgirls = Girl.objects.all()
        vlanguages = Language.objects.all()
        vmovies = Movie.objects.all()
        vcapitulos = Episode.objects.all()
        vseries = Serie.objects.all()

        context = {'message': message, 'vblocks': vblocks, 'vchannels': vchannels, 'vdevices': vdevices,
                   'vgirls': vgirls,
                   'vlanguages': vlanguages, 'vseries': vseries,
                   'vmovies': vmovies, 'vcapitulos': vcapitulos}
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
                decjson = json.loads(strjson)
                vblock = Block.objects.get(block_id=decjson['Block']['block_id'])
                vblock.name = decjson['Block']['name']
                vschedule_date = datetime.datetime.strptime(decjson['Block']['publish_date'], '%d-%m-%Y').strftime(
                    '%Y-%m-%d')
                vblock.publish_date = vschedule_date
                vblock.language = Language.objects.get(code=decjson['Block']['language'])
                vblock.channel = Channel.objects.get(pk=decjson['Block']['channel_id'])
                vdevice = Device.objects.get(pk=int(decjson['Block']['target_device_id']))

                vblock.target_device_id = int(decjson['Block']['target_device_id'])
                vblock.save()
            except Setting.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No Existe Setting. (" + e.message + ")"})
            except Serie.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No Existe Serie. (" + e.message + ")"})
            except Image.DoesNotExist as e:
                return render(request, 'cawas/error.html',
                              {"message": "No Existe Imagen Asociada a la Serie. (" + e.message + ")"})
            except Language.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe LENGUAJE. (" + e.message + ")"})
            except Channel.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Channel. (" + e.message + ")"})
            except Device.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Device. (" + e.message + ")"})
            except Block.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Bloque1. (" + e.message + ")"})

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
                    # asset_id = item['asset_id']
                    # vasset = Asset.objects.get(asset_id=item)
                    # vblock.assets.add(vasset)
                    ph = PublishHelper()
                    ph.func_publish_queue(request, asset_id, vblock.language, 'AS', 'Q', vblock.publish_date)
                    #func_publish_queue(item, vblock.language, 'AS', 'Q', vblock.publish_date)
                except Asset.DoesNotExist as e:
                    return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})

            # Publica en PublishQueue

            #func_publish_queue(vblock.block_id, vblock.language, 'BL', 'Q', vblock.publish_date)
            ph = PublishHelper()
            ph.func_publish_queue(request, vblock.block_id, vblock.language, 'BL', 'Q', vblock.publish_date)
            context = {"flag": "success"}
            return render(request, 'cawas/blocks/edit.html', context)
            # Fin datos Bloque

        try:
            print "block_id" + block_id
            vblock = Block.objects.get(block_id=block_id)
            vassetselect = vblock.assets.all()
            #
            vmovienotselect = Movie.objects.exclude(asset__in=vassetselect)
            vserienotselect = Serie.objects.exclude(asset__in=vassetselect)
            vgirlnotselect = Girl.objects.exclude(asset__in=vassetselect)
            vepisodenotselect = Episode.objects.exclude(asset__in=vassetselect)

            vmovieselect = Movie.objects.filter(asset__in=vassetselect)
            vserieselect = Serie.objects.filter(asset__in=vassetselect)
            vgirlselect = Girl.objects.filter(asset__in=vassetselect)
            vepisodeselect = Episode.objects.filter(asset__in=vassetselect)

        except Block.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Bloque2. (" + e.message + ")"})

        # Variables Para GET

        vchannels = Channel.objects.all()
        vseries = Serie.objects.all()
        vgirls = Girl.objects.all()
        vlanguages = Language.objects.all()
        vdevices = Device.objects.all()



        context = {'message': message, 'vchannels': vchannels,
                   'vgirls': vgirls, 'vlanguages': vlanguages,
                   'vseries': vseries, 'vblock': vblock,
                   'vdevices':vdevices,
                   'vmovienotselect': vmovienotselect, 'vgirlnotselect': vgirlnotselect,
                   'vepisodenotselect': vepisodenotselect, 'vmovieselect': vmovieselect,
                   'vgirlselect': vgirlselect, 'vepisodeselect': vepisodeselect,
                   'vserienotselect': vserienotselect, 'vserieselect': vserieselect
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
        blocks_list = None

        if request.session.has_key('list_block_message'):
            if request.session['list_block_message'] != '':
                message = request.session['list_block_message']
                request.session['list_block_message'] = ''

        if request.session.has_key('list_block_flag'):
            if request.session['list_block_flag'] != '':
                flag = request.session['list_block_flag']
                request.session['list_block_flag'] = ''


        if request.POST:
            titulo = request.POST['inputTitulo']
            selectestado = request.POST['selectestado']

            # FILTROS
            if titulo != '':
                if selectestado != '':
                    blocks_list = Block.objects.filter(Q(name__icontains=titulo)|Q(block_id__icontains=titulo), publish_status=selectestado).order_by('block_id')
                else:
                    blocks_list = Block.objects.filter(Q(name__icontains=titulo)|Q(block_id__icontains=titulo)).order_by('block_id')
            elif selectestado != '':
                blocks_list = Block.objects.filter(publish_status=selectestado).order_by('block_id')
            else:
                blocks_list = Block.objects.all().order_by('block_id')

        if blocks_list is None:
            blocks_list = Block.objects.all().order_by('block_id')

        paginator = Paginator(blocks_list, 20)  # Show 25 contacts per page
        try:
            blocks = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            blocks = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            blocks = paginator.page(paginator.num_pages)

        context = {'message': message, 'flag':flag,  'registros': blocks, 'titulo': titulo, 'usuario': usuario}
        return render(request, 'cawas/blocks/list.html', context)




    # despublicar
    def unpublish(self, request, id):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        try:
            block = Block.objects.get(id=id)
            #1 - quitar la asociacion
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
            vzones = PublishZone.objects.filter(enabled=True)
            for zone in vzones:
                abr = ApiBackendResource(zone.backend_url, setting.value)
                param = {"block_id": block.block_id,
                         "lang": block.language.code}
                abr.delete(param)

            # 3 - Actualizar Activated a False
            block.assets = []
            block.activated = False
            block.save()

            # se elimina el bloque de cawas
            block.delete()

            self.code_return = 0
            request.session['list_block_message'] = 'Bloque Despublicado Correctamente '
            request.session['list_block_flag'] = FLAG_SUCCESS

        except PublishZone.DoesNotExist as e:
            return render(request, 'cawas/error.html',
                          {"message": "PublishZone no Existe. (" + str(e.message) + ")"})
        except Block.DoesNotExist as e:
            return render(request, 'cawas/error.html',
                          {"message": "Metadata de Slider no Existe. (" + str(e.message) + ")"})

        return self.code_return



    def publish(self, request, id):
        #Publicar la Serie
        block = Block.objects.get(id = id)
        vpublish_date = datetime.datetime.now().strftime('%Y-%m-%d')
        block.publish_date = vpublish_date
        block.save()
       # ENCOLA LOS ASSETS QUE CORRESPONDEN AL BLOQUE
        vassets = block.assets.all()
        for item in vassets:
            try:
                asset_id = item.asset_id
                ph = PublishHelper()
                ph.func_publish_queue(request, asset_id, block.language, 'AS', 'Q', block.publish_date)

            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html',
                              {"message": "No existe Asset. " + asset_id + "  (" + e.message + ")"})

        ph = PublishHelper()
        ph.func_publish_queue(request, block.block_id, block.language, 'BL', 'Q', block.publish_date)

        request.session['list_block_message'] = 'Bloque en ' + block.language.name + ' de Publicada Correctamente'
        request.session['list_block_flag'] = FLAG_SUCCESS
        self.code_return = 0

        return self.code_return


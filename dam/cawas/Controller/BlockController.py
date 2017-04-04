import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import Asset, Setting, Girl, Block, Category, Language, Image, Channel, Device, Serie, Movie, Episode
from ..Helpers.PublishHelper import PublishHelper
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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

        context = {'message': message, 'vchannels': vchannels,
                   'vgirls': vgirls, 'vlanguages': vlanguages,
                   'vseries': vseries, 'vblock': vblock,
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
        message = "Error"
        titulo = ''
        page = request.GET.get('page')
        request.POST.get('page')
        blocks_list = None

        if request.POST:
            titulo = request.POST['inputTitulo']
            selectestado = request.POST['selectestado']

            # FILTROS
            if titulo != '':
                if selectestado != '':
                    blocks_list = Block.objects.filter(name__icontains=titulo, publish_status=selectestado).order_by('block_id')
                else:
                    blocks_list = Block.objects.filter(name__icontains=titulo).order_by('block_id')
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

        context = {'message': message, 'registros': blocks, 'titulo': titulo, 'usuario': usuario}
        return render(request, 'cawas/blocks/list.html', context)
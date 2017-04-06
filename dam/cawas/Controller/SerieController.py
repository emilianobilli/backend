import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import Asset, Setting, Serie, SerieMetadata, Category, Language,PublishQueue, PublishZone, Image, Girl,  GirlMetadata, Channel
from ..Helpers.PublishHelper import PublishHelper
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..Helpers.GlobalValues import *

class SerieController(object):


    def add(self, request):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        # VARIABLES LOCALES
        message = ''
        flag = ''
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
                return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})

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
                    return render(request, 'cawas/error.html', {"message": "No existe Girl. (" + e.message + ")"})

            # CARGAR CATEGORIES
            vcategories = decjson['Serie']['categories']
            for item in vcategories:
                try:
                    vserie.category.add(Category.objects.get(pk=item['category_id']))
                except Category.DoesNotExist as e:
                    return render(request, 'cawas/error.html', {"message": "No existe Category. (" + e.message + ")"})

            # Channel
            try:
                vserie.channel = Channel.objects.get(pk=decjson['Serie']['channel_id'])
            except Channel.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Channel. (" + e.message + ")"})

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
                    return render(request, 'cawas/error.html', {"message": "No existe LANGUAGE. (" + e.message + ")"})

                vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                smd.title = item['Seriemetadata']['title']
                smd.summary_short = item['Seriemetadata']['summary_short']
                smd.summary_long = item['Seriemetadata']['summary_long']
                smd.serie = vserie
                smd.publish_date = vschedule_date

                smd.save()
                # Publica en PublishQueue
                ph = PublishHelper()
                ph.func_publish_queue(request, vasset.asset_id, smd.language, 'AS', 'Q', vschedule_date)
                ph.func_publish_image(request, vimg)

            flag = 'success'


        # VARIABLES PARA GET - CARGAR GIRL
        try:
            message = ''
            vlanguages = Language.objects.all()
            vgirls = Girl.objects.all()
            vcategories = Category.objects.all()
            vchannels = Channel.objects.all()
            vseries = Serie.objects.all()


        except Serie.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Serie No Existe . (" + e.message + ")"})
        except Girl.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Girl No Existe . (" + e.message + ")"})
        except Category.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Categoria no Existe. (" + e.message + ")"})
        except Channel.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Canal no Existe. (" + e.message + ")"})
        except GirlMetadata.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "GirlMetaData No Existe . (" + e.message + ")"})

        context = {'message': message, 'flag':flag,'vgirls': vgirls, 'vlanguages': vlanguages, 'vcategories': vcategories,
                   'vchannels': vchannels, 'vseries': vseries,'flag':flag}
        return render(request, 'cawas/series/add.html', context)




    def edit(self,request, asset_id):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        # VARIABLES LOCALES
        message = ''
        flag = ''
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
            except Setting.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No Existe Setting. (" + e.message + ")"})
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No Existe Asset. (" + e.message + ")"})
            except Serie.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No Existe Serie. (" + e.message + ")"})
            except Image.DoesNotExist as e:
                return render(request, 'cawas/error.html',
                              {"message": "No Existe Imagen Asociada a la Serie. (" + e.message + ")"})

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
                    return render(request, 'cawas/error.html', {"message": "No existe Girl. (" + e.message + ")"})

            # CARGAR CATEGORIES
            vcategories = decjson['Serie']['categories']
            for item in vcategories:
                try:
                    vserie.category.add(Category.objects.get(pk=item['category_id']))
                except Category.DoesNotExist as e:
                    return render(request, 'cawas/error.html', {"message": "No existe Category. (" + e.message + ")"})

            # Channel
            try:
                vserie.channel = Channel.objects.get(pk=decjson['Serie']['channel_id'])
            except Channel.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Channel. (" + e.message + ")"})

            vserie.save()
            message = 'Categoria - Registrado Correctamente'

            # Fin datos serie

            # BORRAR Y CREAR METADATA

            vseriemetadatas = decjson['Serie']['Seriemetadatas']
            #SerieMetadata.objects.filter(serie=vserie).delete()
            for item in vseriemetadatas:
                try:
                    vlanguage = Language.objects.get(code=item['Seriemetadata']['language'])
                    smd = SerieMetadata.objects.get(serie=vserie, language=vlanguage)
                except SerieMetadata.DoesNotExist as e:
                    smd = SerieMetadata()
                except Language.DoesNotExist as e:
                    return render(request, 'cawas/error.html', {"message": "No existe LANGUAGE. (" + e.message + ")"})

                vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                smd.language = vlanguage
                smd.title = item['Seriemetadata']['title']
                smd.summary_short = item['Seriemetadata']['summary_short']
                smd.summary_long = item['Seriemetadata']['summary_long']
                smd.serie = vserie
                smd.publish_date = vschedule_date

                metadatas = SerieMetadata.objects.filter(serie=vserie, language=smd.language)
                # Si no existe METADATA, se genera
                if metadatas.count() < 1:
                    smd.save()
                    # Publica en PublishQueue
                    ph = PublishHelper()
                    ph.func_publish_queue(request, vasset.asset_id, smd.language, 'AS', 'Q', vschedule_date)
                    ph.func_publish_image(request, vimg)

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


        except Asset.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Asset No Existe . (" + e.message + ")"})
        except Serie.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Serie No Existe . (" + e.message + ")"})
        except Girl.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Girl No Existe . (" + e.message + ")"})
        except Category.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Categoria no Existe. (" + e.message + ")"})
        except Channel.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Canal no Existe. (" + e.message + ")"})
        except GirlMetadata.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "GirlMetaData No Existe . (" + e.message + ")"})

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
        # Imagequeue -

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
                if selectestado != '':
                    series_list = SerieMetadata.objects.filter(title__icontains=titulo,
                                                               publish_status=selectestado).order_by('serie_id')
                else:
                    series_list = SerieMetadata.objects.filter(title__icontains=titulo).order_by('serie_id')
            elif selectestado != '':
                series_list = SerieMetadata.objects.filter(publish_status=selectestado).order_by('serie_id')
            else:
                series_list = SerieMetadata.objects.all().order_by('serie_id')

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

        context = {'message': message, 'flag':flag, 'registros': series, 'titulo': titulo, 'usuario': usuario}
        return render(request, 'cawas/series/list.html', context)



    # despublicar
    def unpublish(self, request, id):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        try:
            seriemetadata = SerieMetadata.objects.get(id=id)
            vasset_id = seriemetadata.serie.asset.asset_id

            # 1 - VERIFICAR, si estado de publicacion esta en Q, se debe eliminar
            print "itemid " + vasset_id
            publishs = PublishQueue.objects.filter(item_id=vasset_id, status='Q')
            if publishs.count > 0:
                publishs.delete()

            # 2 - Realizar delete al backend
            backend_asset_url = Setting.objects.get(code='backend_asset_url')
            # vzones = PublishZone.objects.filter(enabled=True)
            # SE COMENTA PARA
            # for zone in vzones:
            #    abr = ApiBackendResource(zone.backend_url, backend_asset_url)
            #    param = ({"asset_id": girlmetadata.girl.asset.asset_id, "asset_type": "show",
            #              "lang": girlmetadata.language.code})
            #    abr.delete(param)


            # 3 - Actualizar Activated a False
            seriemetadata.activated = False
            seriemetadata.save()

            self.code_return = 0
            request.session['list_serie_message'] = 'Metadata '+ str(seriemetadata.id) + ' de Serie '+str(seriemetadata.serie.asset.asset_id)+ ' Despublicado Correctamente'
            request.session['list_serie_flag'] = FLAG_SUCCESS
        except PublishZone.DoesNotExist as e:
            return render(request, 'cawas/error.html',
                          {"message": "PublishZone no Existe. (" + str(e.message) + ")"})
        except SerieMetadata.DoesNotExist as e:
            return render(request, 'cawas/error.html',
                          {"message": "Metadata de Serie no Existe. (" + str(e.message) + ")"})

        return self.code_return
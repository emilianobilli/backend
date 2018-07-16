import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import Asset, Setting, Slider,Country, Movie, Episode, Serie, Girl, Category, Language, Device, Image, Girl, PublishZone, Channel, PublishQueue, ImageQueue
from ..Helpers.PublishHelper import PublishHelper
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..Helpers.GlobalValues import *
from ..backend_sdk import ApiBackendServer, ApiBackendResource, ApiBackendException
from django.db.models import Q


class SliderController(object):

    def add(self, request):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        # VARIABLES LOCALES
        message = ''
        vflag = ""
        vasset = Asset()
        vslider = Slider()
        try:
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            pathfileslogo = Setting.objects.get(code='image_repository_path_logo')
            base_dir      = Setting.objects.get(code='dam_base_dir')
        except Setting.DoesNotExist as e:
            message ='No existe Setting '
            return render(request, 'cawas/error.html', {'code': 500, 'message': message}, status=500)



        #PROCESAMIENTO POST
        if request.method == 'POST':
            # VARIABLES
            try:
                vimg = Image()
                # Parsear JSON
                strjson = request.POST['varsToJSON']
                decjson = json.loads(strjson.replace('\r','\\r').replace('\n','\\n'))
                vgrabarypublicar = decjson['Slider']['publicar']
                if decjson['Slider']['asset_id'] is not None:
                    if Asset.objects.filter(asset_id=decjson['Slider']['asset_id']).exists():
                        vasset = Asset.objects.get(asset_id=decjson['Slider']['asset_id'])
                        vslider.asset = vasset
                    else:
                        vslider.asset = None
                vslider.media_type = decjson['Slider']['media_type']
                vdevice = Device.objects.get(id=decjson['Slider']['target_device_id'])
                vslider.target_device = vdevice
                vslider.text = decjson['Slider']['text']

                if decjson['Slider']['videoname'] is not None:
                    vslider.video_name = decjson['Slider']['videoname']


                if decjson['Slider']['linked_url'] is None:
                    vslider.linked_url = ''
                else:
                    vslider.linked_url = decjson['Slider']['linked_url']

                vslider.language = Language.objects.get(code=decjson['Slider']['language'])
                vslider.save()

                vimg.name = vslider.slider_id
                if (request.FILES.has_key('ThumbHor')):
                    if request.FILES['ThumbHor'].name != '':
                        # TRATAMIENTO DE IMAGEN Landscape
                        vimg.landscape      = request.FILES['ThumbHor']
                        extension           = os.path.splitext(vimg.landscape.name)[1]
                        varchivo            =  pathfilesland.value + vimg.name + extension
                        vimg.landscape.name = varchivo
                        varchivo_server     = base_dir.value + varchivo
                        if os.path.isfile(varchivo_server):
                            os.remove(varchivo_server)

                #LOGO
                if (request.FILES.has_key('logo')):
                    if request.FILES['logo'].name != '':
                        # TRATAMIENTO DE IMAGEN LOGO
                        vimg.logo       = request.FILES['logo']
                        extension       = os.path.splitext(vimg.logo.name)[1]
                        varchivo        = pathfileslogo.value + vimg.name + extension
                        vimg.logo.name  = varchivo
                        varchivo_server = base_dir.value + varchivo
                        if os.path.isfile(varchivo_server):
                            os.remove(varchivo_server)
                #/LOGO

                vimg.save()
                vslider.image = vimg
                vslider.save()


                # CARGAR Countries al Asset
                if (decjson['Slider']['countries'] is not None):
                    countries = decjson['Slider']['countries']
                    for item in countries:
                        try:
                            country = Country.objects.get(id=item['country_id'])
                            vslider.target_country.add(country)
                        except Country.DoesNotExist as e:
                            message = "Error: No Existe Pais (" + str(e.message) + ")"
                            return render(request, 'cawas/error.html', {'code': 500, 'message': message}, status=500)


                if decjson['Slider']['text'] is None:
                    vslider.text = ''
                else:
                    vslider.text = decjson['Slider']['text']

                if (decjson['Slider']['publish_date'] != ''):
                    vschedule_date = datetime.datetime.strptime(decjson['Slider']['publish_date'],'%d-%m-%Y').strftime('%Y-%m-%d')
                else:
                    vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')

                vslider.publish_date = vschedule_date
                vslider.queue_status = 'Q'
                vslider.save()
                vflag = "success"
                request.session['list_slider_message'] = 'Guardado Correctamente'
                request.session['list_slider_flag'] = FLAG_SUCCESS

                # PUBLICAR METADATA
                if vgrabarypublicar == '1':
                    # preguntar si asset asociado NO esta activado, no publicar el Slider y mostrar mensaje,
                    # se debe publicar asset asociado antes de publicar el slider

                    ph = PublishHelper()
                    ph.func_publish_queue(request, vslider.slider_id, vslider.language, 'SL', 'Q', vschedule_date)
                    ph.func_publish_image(request, vslider.image)


                    vflag = "success"
                    request.session['list_slider_message'] = 'Guardado Correctamente en Cola de Publicacion'
                    request.session['list_slider_flag'] = FLAG_SUCCESS

            except Exception as e:
                message =  "Error al Guardar Slider. (" + str(e) + " )"
                return render(request, 'cawas/error.html', {'code':500, 'message':message}, status=500)

        vassets = Asset.objects.all()
        vsliders = Slider.objects.all()
        vlanguages = Language.objects.all()
        vdevices = Device.objects.all()
        vtypes = {"image": "Image", "video": "Video"}
        countries = Country.objects.all().order_by('name')

        context = {'message': message, 'flag': vflag, 'vtypes': vtypes, 'vassets': vassets, 'vsliders': vsliders,
                   'vlanguages': vlanguages, 'vdevices': vdevices, 'countries':countries}


        return render(request, 'cawas/sliders/add.html', context)




    def edit(self, request, slider_id):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))
        # VARIABLES LOCALES
        vflag = ''
        message=''
        imgland = ''
        imglogo = ''

        try:
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            pathfileslogo = Setting.objects.get(code='image_repository_path_logo')
            base_dir = Setting.objects.get(code='dam_base_dir')
        except Setting.DoesNotExist as e:
            message= 'No existe Setting '
            return render(request, 'cawas/error.html', {'code': 500, 'message': message}, status=500)

        try:
            vslider               = Slider.objects.get(slider_id=slider_id)
            vassets               = Asset.objects.all()
            vsliders              = Slider.objects.all()
            vlanguages            = Language.objects.all()
            vdevices              = Device.objects.all()
            countries_selected    = vslider.target_country.all().order_by('name')
            countries_notselected = Country.objects.exclude(id__in=countries_selected).order_by('name')
            vtypes = {"image": "Image", "video": "Video"}

            if vslider.image is not None:
                i = len(vslider.image.landscape.name)
                imgland = vslider.image.landscape.name[5:i]

            if vslider.image.logo is not None:
                if vslider.image.logo.name is not None:
                    i = len(vslider.image.logo.name)
                    imglogo = vslider.image.logo.name[5:i]

        except Slider.DoesNotExist as e:
            message =  'Error: ' + e.message
            return render(request, 'cawas/error.html', {'code': 500, 'message': message}, status=500)


        if request.method == 'POST':
            # VARIABLES
            try:
                # Parsear JSON
                strjson = request.POST['varsToJSON']
                decjson = json.loads(strjson.replace('\r','\\r').replace('\n','\\n'))
                vslider = Slider.objects.get(slider_id=slider_id)


                if decjson['Slider']['asset_id'] is not None:
                    if Asset.objects.filter(asset_id=decjson['Slider']['asset_id']).exists():
                        vasset = Asset.objects.get(asset_id=decjson['Slider']['asset_id'])
                        vslider.asset = vasset
                    else:
                        vslider.asset = None

                vslider.media_type      = decjson['Slider']['media_type']
                vdevice = Device.objects.get(id=decjson['Slider']['target_device_id'])
                vslider.target_device   = vdevice
                if decjson['Slider']['text'] is None:
                    vslider.text = ''
                else:
                    vslider.text = decjson['Slider']['text']


                if decjson['Slider']['videoname'] is not None:
                    vslider.video_name = decjson['Slider']['videoname']
                if decjson['Slider']['linked_url'] is None:
                    vslider.linked_url = ''
                else:
                    vslider.linked_url = decjson['Slider']['linked_url']
                print 'videoname '
                vslider.save()

                vslider.language = Language.objects.get(code=decjson['Slider']['language'])
                if (decjson['Slider']['publish_date'] != ''):
                    vschedule_date = datetime.datetime.strptime(decjson['Slider']['publish_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
                else:
                    vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                vslider.publish_date = vschedule_date

                if Image.objects.filter(name=vslider.slider_id).exists():
                    vimg = Image.objects.get(name=vslider.slider_id)
                else:
                    vimg = Image()


            except Device.DoesNotExist as e:
                message = "Error: (" + str(e.message) + ")"
                return render(request, 'cawas/error.html', {'code': 500, 'message': message}, status=500)
            except Asset.DoesNotExist as e:
                message = "Error: (" + str(e.message) + ")"
                return render(request, 'cawas/error.html', {'code': 500, 'message': message}, status=500)


            vimg.name = vslider.slider_id

            # IMAGEN Portrait
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

            # LOGO
            if (request.FILES.has_key('logo')):
                if request.FILES['logo'].name != '':
                    # TRATAMIENTO DE IMAGEN LOGO
                    vimg.logo = request.FILES['logo']
                    extension = os.path.splitext(vimg.logo.name)[1]
                    varchivo = pathfileslogo.value + vimg.name + extension
                    vimg.logo.name = varchivo
                    varchivo_server = base_dir.value + varchivo
                    if os.path.isfile(varchivo_server):
                        os.remove(varchivo_server)
                        # /LOGO


            vimg.save()
            vslider.image = vimg
            vslider.queue_status = 'Q'
            vslider.target_country = []

            # CARGAR Countries al Asset del Episode
            if (decjson['Slider']['countries'] is not None):
                countries = decjson['Slider']['countries']
                for item in countries:
                    try:
                        country = Country.objects.get(id=item['country_id'])
                        vslider.target_country.add(country)
                    except Country.DoesNotExist as e:
                        message = "Error: No Existe Pais (" + str(e.message) + ")"
                        return render(request, 'cawas/error.html', {'code': 500, 'message': message}, status=500)
            vslider.save()

            # publicar
            ph = PublishHelper()
            ph.func_publish_queue(request, vslider.slider_id, vslider.language, 'SL', 'Q', vslider.publish_date)
            ph.func_publish_image(request, vslider.image)

            vflag = "success"
            request.session['list_slider_message'] = 'Guardado Correctamente en Cola de Publicacion'
            request.session['list_slider_flag'] = FLAG_SUCCESS

        if request.method == 'GET':
            context = {
                'vtypes': vtypes,
                'vassets': vassets,
                'vsliders': vsliders,
                'imgland':imgland,
                'imglogo': imglogo,
                'vlanguages': vlanguages,
                'vdevices': vdevices,
                'flag': vflag,
                'vslider':vslider,
                'message':message,
                'countries_selected':countries_selected,
                'countries_notselected':countries_notselected}
            return render(request, 'cawas/sliders/edit.html', context)




    def list(self, request):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        usuario = request.user
        message = ''
        flag=''
        titulo = ''
        page = request.GET.get('page')
        request.POST.get('page')
        registros =''
        filter = False

        # Filtro de busqueda
        if request.GET.has_key('search'):
            search = request.GET.get('search')
            if search != '':
                filter = True
                registros = Slider.objects.filter(Q(slider_id__icontains=search) | Q(text__icontains=search)).order_by('-id')

        if filter ==False:
            registros = Slider.objects.all().order_by('-id')
            paginator = Paginator(registros, 25)
            page = request.GET.get('page')
            try:
                registros = paginator.page(page)
            except PageNotAnInteger:
                registros = paginator.page(1)
            except EmptyPage:
                registros = paginator.page(paginator.num_pages)


        #Mensajes
        if request.session.has_key('list_slider_message'):
            if request.session['list_slider_message'] != '':
                message = request.session['list_slider_message']
                request.session['list_slider_message'] = ''

        if request.session.has_key('list_slider_flag'):
            if request.session['list_slider_flag'] != '':
                flag = request.session['list_slider_flag']
                request.session['list_slider_flag'] = ''

        context = {'message': message, 'flag':flag, 'registros': registros, 'titulo': titulo, 'usuario': usuario}
        return render(request, 'cawas/sliders/list.html', context)


    def publish(self, request, id):
        try:
            vslider = Slider.objects.get(slider_id=id)
            vslider.queue_status = 'Q'
            vslider.save()
            # publicar
            ph = PublishHelper()
            ph.func_publish_queue(request, vslider.slider_id, vslider.language, 'SL', 'Q', vslider.publish_date)
            ph.func_publish_image(request, vslider.image)


        except Slider.DoesNotExist as e:
            self.code_return = -1
            request.session['list_slider_message'] = 'Error: ' + e.message
            request.session['list_slider_flag'] = FLAG_ALERT
            return self.code_return

        request.session['list_slider_message'] = 'Slider ' + vslider.slider_id + ' Guardado en Cola de Publicacion'
        request.session['list_slider_flag'] = FLAG_SUCCESS
        self.code_return = 0



    #Despublicar
    def unpublish(self, request, id):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        try:
            if (Slider.objects.filter(slider_id=id).count() > 0 ):
                slider = Slider.objects.get(slider_id=id)

            # 1 - VERIFICAR, si estado de publicacion esta en Q, se debe eliminar
            publishs = PublishQueue.objects.filter(item_id=slider.slider_id, status='Q')
            if publishs.count > 0:
                publishs.delete()

            # 2 - Realizar delete al backend
            setting = Setting.objects.get(code='backend_slider_url')
            api_key = Setting.objects.get(code='backend_api_key')
            vzones = PublishZone.objects.filter(enabled=True)

            #SE COMENTA PARA
            hasErrorBackend = False
            for zone in vzones:
                abr = ApiBackendResource(zone.backend_url, setting.value, api_key.value)
                param = {"slider_id": slider.slider_id, "lang": slider.language.code}
                respuesta = abr.delete(param)

                if 'status' in respuesta:
                    if respuesta['status'] != 200:
                        hasErrorBackend = True


            if not hasErrorBackend:
                slider.delete()
                self.code_return = 0
                request.session['list_slider_message'] = 'Slider Eliminado Correctamente '
                request.session['list_slider_flag'] = FLAG_SUCCESS
                return self.code_return

        except PublishZone.DoesNotExist as e:
            self.code_return = -1
            request.session['list_slider_message'] = 'Error: ' + e.message
            request.session['list_slider_flag'] = FLAG_ALERT
            return self.code_return
        except ApiBackendException as e:
            self.code_return = -1
            request.session['list_slider_message'] = 'Error: ' + e.message
            request.session['list_slider_flag'] = FLAG_ALERT
            return self.code_return

        return self.code_return
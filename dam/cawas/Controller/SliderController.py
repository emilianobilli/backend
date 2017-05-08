import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import Asset, Setting, Slider,  Category, Language, Device, Image, Girl, PublishZone, Channel, PublishQueue, ImageQueue
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
        vschedule_date = ''
        vasset = Asset()
        vslider = Slider()

        try:
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
        except Setting.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})

        if request.method == 'POST':
            # VARIABLES
            try:
                vimg = Image()
                # Parsear JSON
                strjson = request.POST['varsToJSON']
                decjson = json.loads(strjson)
                if (decjson['Slider']['asset_id']!='0'):
                    vasset = Asset.objects.get(asset_id=decjson['Slider']['asset_id'])
                    vslider.asset = vasset
                vslider.media_type = decjson['Slider']['media_type']
                vdevice = Device.objects.get(id=decjson['Slider']['target_device_id'])
                vslider.target_device = vdevice
                vslider.text = decjson['Slider']['text']
                vslider.language = Language.objects.get(code=decjson['Slider']['language'])
                #vslider.image = vimg
                vslider.save()

                if (request.FILES.has_key('ThumbHor')):
                    if request.FILES['ThumbHor'].name != '':
                        vimg.name = vslider.slider_id
                        vimg.landscape = request.FILES['ThumbHor']
                        extension = os.path.splitext(vimg.landscape.name)[1]
                        varchivo = pathfilesland.value + vimg.name + extension
                        vimg.landscape.name = varchivo
                        if os.path.isfile(varchivo):
                            os.remove(varchivo)
                        vimg.save()
                        vslider.image = vimg
                        vslider.save()
                        print 'debug5'



                if (decjson['Slider']['publish_date'] != ''):
                    vschedule_date = datetime.datetime.strptime(decjson['Slider']['publish_date'],'%d-%m-%Y').strftime('%Y-%m-%d')
                else:
                    vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')

                vslider.publish_date = vschedule_date
                vslider.save()




            except Device.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Device. (" + e.message + ")"})
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})
            except Language.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Lenguaje. (" + e.message + ")"})


            vflag = "success"
            request.session['list_slider_message'] = 'Guardado Correctamente'
            request.session['list_slider_flag'] = FLAG_SUCCESS


        vassets = Asset.objects.all()
        vsliders = Slider.objects.all()
        vlanguages = Language.objects.all()
        vdevices = Device.objects.all()
        vtypes = {"image": "Image", "video": "Video"}

        context = {'message': message, 'flag': vflag, 'vtypes': vtypes, 'vassets': vassets, 'vsliders': vsliders,
                   'vlanguages': vlanguages, 'vdevices': vdevices}
        return render(request, 'cawas/sliders/add.html', context)




    def edit(self, request, slider_id):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

            # VARIABLES LOCALES
        vflag = ''
        message=''
        vschedule_date = ''
        vasset = Asset()
        vslider = Slider()
        vimg = Image()
        imgland = ''
        try:
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
        except Setting.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})

        try:
            vslider = Slider.objects.get(slider_id=slider_id)
            vassets = Asset.objects.all()
            vsliders = Slider.objects.all()
            vlanguages = Language.objects.all()
            vdevices = Device.objects.all()
            vtypes = {"image": "Image", "video": "Video"}

            if vslider.image is not None:
                i = len(vslider.image.landscape.name)
                imgland = vslider.image.landscape.name[5:i]

        except Slider.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Slider. (" + str(e.message) + ")"})
        except Image.DoesNotExist as e:
            imgland = ''

        if request.method == 'POST':
            # VARIABLES
            try:
                # Parsear JSON
                strjson = request.POST['varsToJSON']
                decjson = json.loads(strjson)

                vslider = Slider.objects.get(slider_id=slider_id)

                if decjson['Slider']['asset_id'] is not None:
                    if Asset.objects.filter(asset_id=decjson['Slider']['asset_id']).exists():
                        vasset = Asset.objects.get(asset_id=decjson['Slider']['asset_id'])
                        vslider.asset = vasset

                vslider.media_type = decjson['Slider']['media_type']
                vdevice = Device.objects.get(id=decjson['Slider']['target_device_id'])
                vslider.target_device = vdevice
                vslider.text = decjson['Slider']['text']
                vslider.language = Language.objects.get(code=decjson['Slider']['language'])
                if (decjson['Slider']['publish_date'] != ''):
                    vschedule_date = datetime.datetime.strptime(decjson['Slider']['publish_date'], '%d-%m-%Y').strftime(
                        '%Y-%m-%d')
                else:
                    vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                vslider.publish_date = vschedule_date

                if Image.objects.filter(name=vslider.slider_id).exists():
                    vimg = Image.objects.get(name=vslider.slider_id)
                else:
                    vimg = Image()

            except Device.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Device. (" + e.message + ")"})
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})

            # IMAGEN Portrait
            if (request.FILES.has_key('ThumbHor')):
                if request.FILES['ThumbHor'].name != '':
                    vimg.landscape = request.FILES['ThumbHor']
                    extension = os.path.splitext(vimg.landscape.name)[1]
                    vimg.name = vslider.slider_id
                    varchivo = pathfilesland.value + vimg.name + extension
                    vimg.landscape.name = varchivo
                    if os.path.isfile(varchivo):
                        os.remove(varchivo)

            vimg.save()
            vslider.image = vimg
            vslider.save()

            # publicar
            ph = PublishHelper()
            ph.func_publish_queue(request, vslider.slider_id, vslider.language, 'AS', 'Q', vslider.publish_date)
            ph.func_publish_image(request, vslider.image)

            request.session['list_slider_message'] = 'Guardado Correctamente'
            request.session['list_slider_flag'] = FLAG_SUCCESS



        if request.method == 'GET':
            context = {'vtypes': vtypes, 'vassets': vassets, 'vsliders': vsliders, 'imgland':imgland,
                       'vlanguages': vlanguages, 'vdevices': vdevices, 'flag': vflag, 'vslider': vslider,
                        'message':message}
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
        sliders_list = None

        if request.session.has_key('list_slider_message'):
            if request.session['list_slider_message'] != '':
                message = request.session['list_slider_message']
                request.session['list_slider_message'] = ''

        if request.session.has_key('list_slider_flag'):
            if request.session['list_slider_flag'] != '':
                flag = request.session['list_slider_flag']
                request.session['list_slider_flag'] = ''


        if request.POST:
            titulo = request.POST['inputTitulo']
            selectestado = request.POST['selectestado']
            # FILTROS
            if titulo != '':
                if selectestado != '':
                    sliders_list = Slider.objects.filter(slider_id__icontains=titulo, publish_status=selectestado).order_by('slider_id')
                else:
                    sliders_list = Slider.objects.filter(slider_id__icontains=titulo).order_by('slider_id')
            elif selectestado != '':
                sliders_list = Slider.objects.filter(publish_status=selectestado).order_by('slider_id')
            else:
                sliders_list = Slider.objects.all().order_by('slider_id')

        if sliders_list is None:
            sliders_list = Slider.objects.all().order_by('slider_id')

        paginator = Paginator(sliders_list, 20)  # Show 25 contacts per page
        try:
            sliders = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            sliders = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            sliders = paginator.page(paginator.num_pages)

        context = {'message': message, 'flag':flag, 'registros': sliders, 'titulo': titulo, 'usuario': usuario}
        return render(request, 'cawas/sliders/list.html', context)


    def publish(self, request, id):
        try:
            vslider = Slider.objects.get(slider_id=id)
            # publicar
            ph = PublishHelper()
            ph.func_publish_queue(request, vslider.slider_id, vslider.language, 'AS', 'Q', vslider.publish_date)
            ph.func_publish_image(request, vslider.image)

        except Slider.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Slider. (" + str(e.message) + ")"})

        request.session['list_slider_message'] = 'Slider ' + vslider.slider_id + ' Publicada Correctamente'
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

            if not slider.activated:
                slider.delete()
                self.code_return = 0
                request.session['list_slider_message'] = 'Slider Eliminado Correctamente '
                request.session['list_slider_flag'] = FLAG_SUCCESS
                return self.code_return

            # 1 - VERIFICAR, si estado de publicacion esta en Q, se debe eliminar
            publishs = PublishQueue.objects.filter(item_id=slider.slider_id, status='Q')
            if publishs.count > 0:
                publishs.delete()

            # 2 - Realizar delete al backend
            setting = Setting.objects.get(code='backend_slider_url')
            api_key = Setting.objects.get(code='backend_api_key')
            vzones = PublishZone.objects.filter(enabled=True)
            #SE COMENTA PARA
            for zone in vzones:
                abr = ApiBackendResource(zone.backend_url, setting.value, api_key.value)
                param = {"slider_id": slider.slider_id,
                         "lang": slider.language.code}
                abr.delete(api_key.value, param)

            # 3 - Actualizar Activated a False
            slider.activated=False
            slider.save()
            slider.delete()
            self.code_return = 0
            request.session['list_slider_message'] = 'Slider en ' + slider.language.name +' de Slider ' + slider.slider_id + ' Despublicado Correctamente'
            request.session['list_slider_flag'] = FLAG_SUCCESS
        except PublishZone.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "PublishZone no Existe. (" + str(e.message) + ")"})
        except ApiBackendException as e:
            request.session['list_slider_message'] = "Error al despublicar (" + str(e.value) + ")"
            request.session['list_slider_flag'] = FLAG_ALERT

        return self.code_return
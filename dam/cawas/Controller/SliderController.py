import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import Asset, Setting, Slider, SliderMetadata, Category, Language, Device, Image, Girl, PublishZone, Channel, PublishQueue, ImageQueue
from ..Helpers.PublishHelper import PublishHelper
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..Helpers.GlobalValues import *
from backend_sdk import ApiBackendServer, ApiBackendResource


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

        if request.method == 'POST':
            # VARIABLES
            try:
                # Parsear JSON
                strjson = request.POST['varsToJSON']
                decjson = json.loads(strjson)
                print "DEBUG: " + decjson['Slider']['media_type']

                vasset = Asset.objects.get(asset_id=decjson['Slider']['asset_id'])
                print "ASSET_ID: " + decjson['Slider']['asset_id']
                vslider.asset = vasset
                vslider.media_url = decjson['Slider']['media_url']
                vslider.media_type = decjson['Slider']['media_type']

                print "ASSET_ID: " + decjson['Slider']['media_type']

                vdevice = Device.objects.get(id=decjson['Slider']['target_device_id'])
                vslider.target_device = vdevice
                vslider.media_type = decjson['Slider']['target_device_id']
                vslider.save()
            except Device.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Device. (" + e.message + ")"})
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})


            # METADATA
            vslidermetadata = decjson['Slider']['Slidermetadatas']
            print decjson['Slider']['Slidermetadatas']


            # SliderMetadata.objects.filter(slider=vslider).delete()
            for item in vslidermetadata:
                try:
                    smd = SliderMetadata()

                    if (item['Slidermetadata']['schedule_date'] != ''):
                        vschedule_date = datetime.datetime.strptime(item['Slidermetadata']['schedule_date'],
                                                                    '%d-%m-%Y').strftime('%Y-%m-%d')
                    else:
                        vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')

                    vlang = Language.objects.get(code=item['Slidermetadata']['language'])
                    smd.language = vlang
                    smd.text = item['Slidermetadata']['text']
                    smd.slider = vslider
                    smd.publish_date = vschedule_date
                    smd.save()

                    # Publica en PublishQueue
                    ph = PublishHelper()
                    ph.func_publish_queue(request, vslider.slider_id, vlang, 'AS', 'Q', vschedule_date)

                except Language.DoesNotExist as e:
                    return render(request, 'cawas/error.html',
                                  {"message": "Lenguaje no Existe. (" + str(e.message) + ")"})
                except Exception as e:
                    return render(request, 'cawas/error.html',
                                  {"message": "Error al Guardar Metadata. (" + str(e.message) + ")"})
            vflag = "success"

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

        try:
            vslider = Slider.objects.get(slider_id=slider_id)

            vassets = Asset.objects.all()
            vsliders = Slider.objects.all()
            vlanguages = Language.objects.all()
            vdevices = Device.objects.all()
            vtypes = {"image": "Image", "video": "Video"}

            # nuevo diccionario para completar lenguages y metadata
            vlangmetadata = []
            for itemlang in vlanguages:
                try:
                    vslidermetadata = SliderMetadata.objects.get(slider=vslider, language=itemlang)
                    vlangmetadata.append({
                        'checked': True, 'code': itemlang.code, 'name': itemlang.name,
                        'text': vslidermetadata.text, 'publish_date': vslidermetadata.publish_date
                    })
                except SliderMetadata.DoesNotExist as a:
                    vlangmetadata.append(
                        {'checked': False, 'code': itemlang.code, 'name': itemlang.name, 'text': '', 'text': '',
                         'publish_date': ''})

        except Slider.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Slider. (" + str(e.message) + ")"})

        if request.method == 'POST':
            # VARIABLES
            try:
                # Parsear JSON
                strjson = request.POST['varsToJSON']
                decjson = json.loads(strjson)
                vasset = Asset.objects.get(asset_id=decjson['Slider']['asset_id'])
                vslider.asset = vasset
                vslider.media_url = decjson['Slider']['media_url']
                vslider.media_type = decjson['Slider']['media_type']
                vdevice = Device.objects.get(id=decjson['Slider']['target_device_id'])
                vslider.target_device = vdevice
                vslider.media_type = decjson['Slider']['target_device_id']
                vslider.save()
            except Device.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Device. (" + e.message + ")"})
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})

            # METADATA
            vslidermetadata = decjson['Slider']['Slidermetadatas']
            print decjson['Slider']['Slidermetadatas']
            vflag = "success"

            # SliderMetadata.objects.filter(slider=vslider).delete()
            for item in vslidermetadata:
                try:
                    smd = SliderMetadata()

                    print "DEBUG1: " + item['Slidermetadata']['schedule_date']
                    if (item['Slidermetadata']['schedule_date'] != ''):
                        vschedule_date = datetime.datetime.strptime(item['Slidermetadata']['schedule_date'],
                                                                    '%d-%m-%Y').strftime('%Y-%m-%d')
                    else:
                        vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')

                    vlang = Language.objects.get(code=item['Slidermetadata']['language'])
                    smd.language = vlang
                    smd.text = item['Slidermetadata']['text']
                    smd.slider = vslider
                    smd.publish_date = vschedule_date
                    metadatas = SliderMetadata.objects.filter(slider=vslider, language=vlang)
                    if metadatas.count() < 1:
                        smd.save()
                        # Publica en PublishQueue
                        ph = PublishHelper()
                        ph.func_publish_queue(request, vslider.slider_id, vlang, 'AS', 'Q', vschedule_date)
                    vflag = "success"
                except Language.DoesNotExist as e:
                    return render(request, 'cawas/error.html',
                                  {"message": "Lenguaje no Existe. (" + str(e.message) + ")"})
                except Exception as e:
                    return render(request, 'cawas/error.html',
                                  {"message": "Error al Guardar Metadata. (" + str(e.message) + ")"})
                vflag = "success"

        context = {'vtypes': vtypes, 'vassets': vassets, 'vsliders': vsliders,
                   'vlanguages': vlanguages, 'vdevices': vdevices, 'flag': vflag, 'vslider': vslider,
                   'vlangmetadata': vlangmetadata, 'message':message, 'flag':vflag}
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
                sliders = Slider.objects.filter(media_url__icontains=titulo).order_by('slider_id')
                if selectestado != '':
                    sliders_list = SliderMetadata.objects.filter(slider__in=sliders,
                                                                 publish_status=selectestado).order_by('slider_id')
                else:
                    sliders_list = SliderMetadata.objects.filter(slider__in=sliders).order_by('slider_id')
            elif selectestado != '':
                sliders_list = SliderMetadata.objects.filter(publish_status=selectestado).order_by('slider_id')
            else:
                sliders_list = SliderMetadata.objects.all().order_by('slider_id')

        if sliders_list is None:
            sliders_list = SliderMetadata.objects.all().order_by('slider_id')

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


#despublicar
    def unpublish(self, request, id):
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        try:
            slidermetadata = SliderMetadata.objects.get(id=id)
            vasset_id = slidermetadata.slider.slider_id

            # 1 - VERIFICAR, si estado de publicacion esta en Q, se debe eliminar
            publishs = PublishQueue.objects.filter(item_id=vasset_id, status='Q')
            if publishs.count > 0:
                publishs.delete()

            # 2 - Realizar delete al backend
            backend_asset_url = Setting.objects.get(code='backend_asset_url')
            vzones = PublishZone.objects.filter(enabled=True)
            #SE COMENTA PARA
            for zone in vzones:
                abr = ApiBackendResource(zone.backend_url, backend_asset_url)
                param = ({"asset_id": slidermetadata.slider.asset.asset_id, "asset_type": "show",
                          "lang": slidermetadata.language.code})
                abr.delete(param)


            # 3 - Actualizar Activated a False
            slidermetadata.activated=False
            slidermetadata.save()

            self.code_return = 0
            request.session['list_slider_message'] = 'Metadata en ' + slidermetadata.language.name +' de Slider ' + slidermetadata.slider.slider_id + ' Despublicado Correctamente'
            request.session['list_slider_flag'] = FLAG_SUCCESS
        except PublishZone.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "PublishZone no Existe. (" + str(e.message) + ")"})
        except SliderMetadata.DoesNotExist as e:
            return render(request, 'cawas/error.html',
                          {"message": "Metadata de Slider no Existe. (" + str(e.message) + ")"})

        return self.code_return
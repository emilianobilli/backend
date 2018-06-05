from django.http import HttpResponse
from ..models import Asset, Channel, Image,Setting
import os, datetime, json, logging
from django.shortcuts import render,redirect
from LogController import LogController
from ..Helpers.GlobalValues import *
from ..Helpers.PublishHelper import PublishHelper

TYPE_LANDSCAPE = 1
TYPE_PORTRAIT  = 2

class ChannelController(object):





    def add(self, request):
        if request.method == 'POST':
            try:
                #img_logo        = File()
                #img_logo_hover  = Image()
                channel         = Channel()

                pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
                base_dir      = Setting.objects.get(code='dam_base_dir')
                nombre     = request.POST['nombre']

                channel.name = nombre
                channel.save()

                #if (request.FILES.has_key('image_logo')):
                #    if request.FILES['image_logo'].name != '':
                #        img_logo = self.processImage(self, request.FILES['image_logo'], pathfilesland, base_dir, 'logo_channel_'+ channel.id,TYPE_LANDSCAPE )

                #if (request.FILES.has_key('image_logo_hover')):
                #    if request.FILES['image_logo_hover'].name != '':
                #        img_logo_hover = self.processImage(self, request.FILES['image_logo_hover'], pathfilesland, base_dir, 'logo_hover_channel_'+channel.id, TYPE_LANDSCAPE)

                #img_logo.save()
                #img_logo_hover.save()

                channel.name = nombre

                #channel.logo       = img_logo
                #channel.logo_hover = img_logo_hover
                channel.save()

            except Setting.DoesNotExist as e:
                request.session['list_channel_message'] = "Error al Guardar Channel. (" + e.message + ")"
                request.session['list_channel_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return

            except Exception as e:
                request.session['list_channel_message'] = "Error al Guardar Channel. (" + str(e.message) + ")"
                request.session['list_channel_flag'] = FLAG_ALERT
                self.code_return = -1
                return self.code_return

        return render(request, 'cawas/channels/add.html')



    def list(self, request):
        try:
            registros = Channel.objects.all().order_by('-id')
            context = {'registros':registros}
            return render(request, 'cawas/channels/list.html', context)
        except Asset.DoesNotExist as e:
            return HttpResponse("No existe Asset", None, 500)
        except KeyError:
            return HttpResponse("Error en decodificacion de datos", None, 500)










    def processImage(self, image_param, path, base_dir, image_name, image_type):
        image_process = Image()
        image_process.name = image_name
        if image_type == TYPE_LANDSCAPE:
            image_process.landscape = image_param
            extension = os.path.splitext(image_process.landscape.name)[1]
            varchivo = path.value + image_process.name + extension
            image_process.landscape.name = varchivo
        if image_type == TYPE_PORTRAIT:
            image_process.portrait = image_param
            extension = os.path.splitext(image_process.portrait.name)[1]
            varchivo = path.value + image_process.name + extension
            image_process.portrait.name = varchivo

        varchivo_server = base_dir.value + varchivo
        if os.path.isfile(varchivo_server):
            os.remove(varchivo_server)

        return image_process
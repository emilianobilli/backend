import datetime,os
from ..models import PublishQueue, ImageQueue,PublishZone, Setting
from django.shortcuts import render

class PublishHelper(object):

    #Atributos
    def func_publish_queue(self, request, pid, planguage, pitem_type, pstatus,  pschedule_date):
        #fecha pschedule_date: ya tiene que estar parceada como strftime('%Y-%m-%d')

        publicaciones_anteriores = PublishQueue.objects.filter(item_id=pid, status='Q',item_lang=planguage)
        if publicaciones_anteriores.count() > 0:
            publicaciones_anteriores.delete()

        #Crear nueva publicacion
        vzones = PublishZone.objects.filter(enabled=True)
        for zone in vzones:
            try:
                # CREAR COLA DE PUBLICACION
                vpublish = PublishQueue()
                vpublish.item_id = pid
                vpublish.item_lang = planguage
                vpublish.item_type = pitem_type
                vpublish.status = pstatus
                vpublish.publish_zone = zone
                vpublish.schedule_date = pschedule_date
                vpublish.save()
            except Exception as e:
                request.session['message'] = 'Error ' + e.message
                return -1

    def func_publish_image(self, request, pimg):
        # COLA DE PUBLICACION PARA IMAGENES
            vzones = PublishZone.objects.filter(enabled=True)
            for zone in vzones:
                try:
                    imgQueue = ImageQueue()
                    imgQueue.image = pimg
                    imgQueue.publish_zone = zone
                    imgQueue.schedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                    imgQueue.save()
                except Exception as e:
                    request.session['message'] = 'Error ' + e.message
                    return -1


'''
    def subir_imagen(self, request, p_img ):
        try:
            vimg = p_img
            pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            base_dir = Setting.objects.get(code='dam_base_dir')

            if (request.FILES.has_key('ThumbHor')):
                if request.FILES['ThumbHor'].name != '':
                    # TRATAMIENTO DE IMAGEN Landscape
                    vimg.landscape = request.FILES['ThumbHor']
                    extension = os.path.splitext(vimg.landscape.name)[1]
                    varchivo = base_dir + pathfilesland.value + vimg.name + extension
                    print varchivo
                    vimg.landscape.name = varchivo
                    if os.path.isfile(varchivo):
                        os.remove(varchivo)

            # IMAGEN Portrait
            if (request.FILES.has_key('ThumbVer')):
                if request.FILES['ThumbVer'].name != '':
                    vimg.portrait = request.FILES['ThumbVer']
                    extension = os.path.splitext(vimg.portrait.name)[1]
                    varchivo = base_dir + pathfilesport.value + vimg.name + extension
                    vimg.portrait.name = varchivo
                    # si existe archivo, lo borra
                    print varchivo

                    if os.path.isfile(varchivo):
                        os.remove(varchivo)
            vimg.save()
        except Exception as e:
            request.session['message'] = 'Error ' + e.message
            return -1

        return vimg
'''


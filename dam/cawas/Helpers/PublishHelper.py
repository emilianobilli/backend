import datetime
from ..models import PublishQueue, ImageQueue,PublishZone
from django.shortcuts import render

class PublishHelper(object):

    #Atributos
    def func_publish_queue(self, request, pid, planguage, pitem_type, pstatus,  pschedule_date):
        #fecha pschedule_date: ya tiene que estar parceada como strftime('%Y-%m-%d')

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
                return render(request, 'cawas/error.html', {"message": "No existe Lenguaje. (" + e.message + ")"})


    def func_publish_image(self, request, pimg):
        # COLA DE PUBLICACION PARA IMAGENES
            vzones = PublishZone.objects.filter(enabled=True)
            for zone in vzones:
                try:
                    imgQueue = ImageQueue()
                    imgQueue.image = pimg
                    imgQueue.publish_zone = zone
                    imgQueue.schedule_date = datetime.datetime.now()
                    imgQueue.save()
                except Exception as e:
                    return render(request , 'cawas/error.html',{"message": "Error al Generar Cola de Imagen. (" + e.message + ")"})

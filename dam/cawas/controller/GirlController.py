
import datetime, os, json
from django.db import models
from .cawas.models import Channel, Girl, Image, GirlMetadata
from django.shortcuts import get_object_or_404, render


class GirlController:
    decjson=""
    vimg=Image()
    vgirl=Girl()
    pass

    def setJsonStr(strjson):
        decjson = json.loads(strjson)

    def setImagen(imagen):
        vimg = imagen


    def add(self):
        a = 1
        # VARIABLES
        vgirl = Girl()
        vasset = Asset()
        vasset.asset_type = "girl"
        vasset.save()

        try:
            # CREAR GIRL
            vgirl.asset = vasset
            vgirl.name = decjson['Girl']['name']
            vgirl.type = decjson['Girl']['type_girl']

            if (decjson['Girl']['birth_date'] is not None):
                vgirl.birth_date = datetime.datetime.strptime(decjson['Girl']['birth_date'], '%d-%m-%Y').strftime(
                    '%Y-%m-%d')
            else:
                vgirl.birth_date = datetime.datetime.now().strftime('%Y-%m-%d')

            vgirl.height = decjson['Girl']['height']
            vgirl.weight = decjson['Girl']['weight']
            vgirl.image = vimg
            vgirl.save()
        except Exception as e:
            return render(request, 'cawas/error.html', {"message": "Error al Guardar Girl. (" + e.message + ")."})

        # CREAR METADATA
        vgirlmetadatas = decjson['Girl']['Girlmetadatas']
        for item in vgirlmetadatas:
            vlanguage = Language.objects.get(code=item['Girlmetadata']['language'])
            try:
                gmd = GirlMetadata.objects.get(girl=vgirl, language=vlanguage)
            except GirlMetadata.DoesNotExist as e:
                gmd = GirlMetadata()

            vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
            gmd.language = vlanguage
            gmd.description = item['Girlmetadata']['description']
            gmd.nationality = item['Girlmetadata']['nationality']
            gmd.publish_date = vschedule_date
            gmd.girl = vgirl
            gmd.save()

            # Publica en PublishQueue
            func_publish_queue(vasset, vlanguage, 'AS', 'Q', vschedule_date)
            # Publica en PublishImage
            func_publish_image(vimg)
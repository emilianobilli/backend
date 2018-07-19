import os, datetime, json
from django.http import HttpResponse
from ..models import Asset, Tag, VideoLog, TagMetadata, Setting, PublishZone
from django.shortcuts import render, redirect
from django.http import JsonResponse
from ..backend_sdk import ApiBackendResource

class VideoLogController(object):


    def add(self, request, asset_id):

        if request.is_ajax():
            if request.method == 'POST':
                try:
                    json_data = json.loads(request.body)

                    tag_id   = json_data['tag_id']
                    asset_id = json_data['asset_id']
                    timein   = int(json_data['timein'])
                    timeout  = int(json_data['timeout'])

                    tag = Tag.objects.get(tag_id=tag_id)
                    asset = Asset.objects.get(asset_id=asset_id)

                    videolog = VideoLog()
                    videolog.asset = asset
                    videolog.tag = tag
                    videolog.tc_in = timein
                    videolog.tc_out = timeout
                    videolog.save()

                    #Publicar Tag
                    tagmetadatas = TagMetadata.objects.filter(tag=tag)
                    for m in tagmetadatas:
                        setting = Setting.objects.get(code='backend_tags_url')
                        api_key = Setting.objects.get(code='backend_api_key')
                        vzones = PublishZone.objects.filter(enabled=True)
                        for zone in vzones:
                            abr = ApiBackendResource(zone.backend_url, setting.value, api_key.value)
                            json_body = videolog.toDict(m.language)
                            respuesta = abr.add(json_body)
                            if 'status' in respuesta:
                                if respuesta['status'] != 201:
                                    response = {'message': respuesta['message'], 'status':respuesta['status'], 'data': json_body}
                                    return HttpResponse(json.dumps(response), None, 500)


                    return HttpResponse(json.dumps({'message': 'Guardado Correctamente',  'data':json_body}), None, 200)
                except Asset.DoesNotExist as e:
                    return HttpResponse(json.dumps({'message': 'No Existe Asset' }), None, 500)
                except TagMetadata.DoesNotExist as e:
                    return HttpResponse(json.dumps({'message': 'No Existe TagMetadata'}), None, 500)
                except Tag.DoesNotExist as e:
                    return HttpResponse(json.dumps({'message': 'No Existe Tag'}), None, 500)
                except Exception as e:
                    return HttpResponse(json.dumps({'message': 'Error:'+ e.message}), None, 500)



        #Variables para Get
        try:
            tags = Tag.objects.all()
            asset = Asset.objects.get(asset_id=asset_id)
            videologs = VideoLog.objects.filter(asset=asset).order_by('id')
        except Asset.DoesNotExist as e:
            return JsonResponse({'code': 500, 'message': 'No Existe Asset'})
        except Tag.DoesNotExist as e:
            return JsonResponse({'code': 500, 'message': 'No Existe Asset'})
        except VideoLog.DoesNotExist as e:
            videologs=[]

        context = {'asset_id':asset_id, 'tags':tags, 'registros':videologs }
        return render(request, 'cawas/videotag/index.html', context)





    def findByAssetId(self, request):
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    json_data = json.loads(request.body)
                    asset_id = json_data['asset_id']
                    asset = Asset.objects.get(asset_id=asset_id)
                    videologs = VideoLog.objects.filter(asset=asset)
                    return JsonResponse({'code': 200, 'message': 'Ok','data':json.dumps(videologs)})
                except Asset.DoesNotExist as e:
                    return JsonResponse({'code': 500, 'message': 'No Existe Asset'})
                except VideoLog.DoesNotExist as e:
                    videologs = []
            else:
                return JsonResponse({'code': 500, 'message': 'Metodo no permitido'})
        return JsonResponse({'code': 500, 'message': 'Metodo no permitido'})






    def delete(self, request):
        if request.is_ajax():
            if request.method == 'POST':
                try:

                    json_data = json.loads(request.body)
                    id = json_data['id']
                    response = { 'message': 'Eliminado Correctamente', 'data': id}

                    # Despublicar desde el Backend
                    setting = Setting.objects.get(code='backend_tags_url')
                    api_key = Setting.objects.get(code='backend_api_key')
                    vzones  = PublishZone.objects.filter(enabled=True)
                    video   = VideoLog.objects.get(id=id)

                    # Buscar el videolog y su tag, por cada metadata
                    tagmetadatas = TagMetadata.objects.filter(tag=video.tag)
                    for m in tagmetadatas:
                        for zone in vzones:
                            abr = ApiBackendResource(zone.backend_url, setting.value, api_key.value)
                            json_body  = video.toDict(m.language)
                            respuesta = abr.delete(json_body)
                            if 'status' in respuesta:
                                if respuesta['status'] != 200:
                                    response = {'message': respuesta['message'], 'data': json_body}
                                    return HttpResponse(json.dumps(response), None, 500)

                    VideoLog.objects.filter(id=id).delete()
                    return HttpResponse(json.dumps(response), None, 200)

                except Tag.DoesNotExist as e:
                    return HttpResponse(json.dumps({ 'message': 'No Existe Tag'}), None, 500)
                except VideoLog.DoesNotExist as e:
                    return HttpResponse(json.dumps({ 'message': 'No Existe VideoLog'}), None, 500)
                except TagMetadata.DoesNotExist as e:
                    return HttpResponse(json.dumps({'message': 'No Existe TagMetadata'}), None, 500)
                except Exception as e:
                    return HttpResponse(json.dumps({'message': 'Error en Despublicacion de tag'}), None, 500)


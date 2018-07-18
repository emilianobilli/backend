import os, datetime, json
from django.http import HttpResponse
from ..models import Asset, Tag, VideoLog
from django.shortcuts import render, redirect
from django.http import JsonResponse

class VideoLogController(object):


    def add(self, request, asset_id):

        if request.is_ajax():
            if request.method == 'POST':
                try:
                    json_data = json.loads(request.body)

                    tag_id = json_data['tag_id']
                    asset_id = json_data['asset_id']
                    print 'debug1'
                    timein = int(json_data['timein'])
                    timeout = int(json_data['timeout'])

                    tag = Tag.objects.get(tag_id=tag_id)
                    asset = Asset.objects.get(asset_id=asset_id)
                    videolog = VideoLog()
                    videolog.asset = asset
                    videolog.tag = tag
                    videolog.tc_in = timein
                    videolog.tc_out = timeout
                    videolog.save()

                    return JsonResponse({'code': 200, 'message': 'Guardado Correctamente', 'data':videolog.id })
                except Asset.DoesNotExist as e:
                    return JsonResponse({'code': 500, 'message': 'No Existe Asset'})
                except Tag.DoesNotExist as e:
                    return JsonResponse({'code': 500, 'message': 'No Existe Tag'})
                except Exception as e:
                    return JsonResponse({'code': 500, 'message': 'Error:'+ e.message})



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
                    VideoLog.objects.filter(id=id).delete()
                    return JsonResponse({'code': 200, 'message': 'Eliminado Correctamente', 'data': id})
                except VideoLog.DoesNotExist as e:
                    return JsonResponse({'code': 500, 'message': 'No Existe VideoLog'})
                except Exception as e:
                    return JsonResponse({'code': 500, 'message': 'Error:' + e.message})


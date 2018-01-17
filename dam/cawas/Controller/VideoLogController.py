import os, datetime, json
from django.http import HttpResponse
from ..models import Asset, Tag, VideoLog
from django.shortcuts import render,redirect
from django.http import JsonResponse

class VideoLogController(object):


    def add(self, request, asset_id):

        if request.is_ajax():

            if request.method == 'POST':
                try:

                    json_data = json.loads(request.body)

                    tag_id = json_data['tag_id']
                    asset_id = json_data['asset_id']
                    timein = json_data['timein'][0:5]
                    timeout = json_data['timeout'][0:5]


                    tag = Tag.objects.get(tag_id=tag_id)

                    asset = Asset.objects.get(asset_id=asset_id)


                    videolog = VideoLog()
                    videolog.asset = asset
                    videolog.tag = tag
                    print 'debug1'
                    videolog.tc_in = timein
                    print 'debug2' + str(timein)
                    videolog.tc_out = timeout
                    print 'debug3'
                    videolog.save()

                    return JsonResponse({'code': 200, 'message': 'Guardado Correctamente'})
                except Asset.DoesNotExist as e:
                    return JsonResponse({'code': 500, 'message': 'No Existe Asset'})
                except Tag.DoesNotExist as e:
                    return JsonResponse({'code': 500, 'message': 'No Existe Tag'})
                except Exception as e:
                    return JsonResponse({'code': 500, 'message': 'Error:'+ e.message})


        print 'debug5'
        #Variables para Get
        tags = Tag.objects.all()
        print 'tags' +str(tags)
        context = {'asset_id':asset_id, 'tags':tags}
        return render(request, 'cawas/videotag/index.html', context)



    def delete(self, request):
        data = {'code': 200, 'message': 'Guardado Correctamente'}
        return HttpResponse(json.dumps(data), None, 200)



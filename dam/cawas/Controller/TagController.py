import os, datetime, json
from LogController import LogController
from django.http import HttpResponse
from ..models import Asset,Tag, TagMetadata, Language
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



class TagController(object):

    def index(self, request):
        try:
            if not request.user.is_authenticated:
                lc = LogController()
                return redirect(lc.login_view(request))

            registros = Tag.objects.all().order_by('-id')
            paginator = Paginator(registros, 25)
            page = request.GET.get('page')
            try:
                registros = paginator.page(page)
            except PageNotAnInteger:
                registros = paginator.page(1)
            except EmptyPage:
                registros = paginator.page(paginator.num_pages)

            context ={
                'registros': registros
            }
            return render(request, 'cawas/tags/index.html', context=context)

        except Exception as e:
            request.session['index_tags_message'] = e.message

        return render(request, 'cawas/tags/index.html', context=context)





    def add(self, request):
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    #Leer el Json
                    json_data = json.loads(request.body)
                    print (str(json_data))
                    #La validacion se hace en el Front End con Jquery

                    nombre = json_data['nombre']
                    nombre_pt = ''
                    nombre_es = ''
                    if 'nombre_es' in json_data:
                        nombre_es = json_data['nombre_es']

                    if 'nombre_pt' in json_data:
                        nombre_pt = json_data['nombre_pt']

                    print (str(nombre))
                    print (str(nombre_es))
                    #Crear Tag
                    newtag = Tag()
                    newtag.name = nombre
                    newtag.save()


                    if nombre_es !="":
                        lang = Language.objects.get(code='es')
                        newtagmetadata = TagMetadata()
                        newtagmetadata.tag = newtag
                        newtagmetadata.language =lang
                        newtagmetadata.name = nombre_es
                        newtagmetadata.save()

                    if nombre_pt !="":
                        lang = Language.objects.get(code='pt')
                        newtagmetadata = TagMetadata()
                        newtagmetadata.tag = newtag
                        newtagmetadata.language = lang
                        newtagmetadata.name = nombre_pt
                        newtagmetadata.save()

                    return JsonResponse({'code': 200, 'message': 'Guardado Correctamente'})
                except Asset.DoesNotExist as e:
                    return JsonResponse({'code': 500, 'message': e.message})


        return render(request, 'cawas/tags/add.html', None)




    def edit(self, request, tag_id):
        if request.is_ajax():
            if request.method == 'POST':
                try:
                    # Leer el Json
                    json_data = json.loads(request.body)

                    # La validacion se hace en el Front End con Jquery
                    tag_id = json_data['tag_id']
                    tag = Tag.objects.get(tag_id=tag_id)
                    nombre = json_data['nombre']
                    nombre_pt = ''
                    nombre_es = ''
                    if 'nombre_es' in json_data:
                        nombre_es = json_data['nombre_es']

                    if 'nombre_pt' in json_data:
                        nombre_pt = json_data['nombre_pt']

                    tag.name = nombre
                    tag.save()

                    if nombre_es != '':
                        lang = Language.objects.get(code='es')
                        tagmetadata = TagMetadata.objects.get(language=lang, tag=tag)
                        tagmetadata.name = nombre_es
                        tagmetadata.save()

                    if nombre_pt != '':
                        lang = Language.objects.get(code='pt')
                        tagmetadata = TagMetadata.objects.get(language=lang, tag=tag)
                        print 'tag:' + str(tag)
                        tagmetadata.name = nombre_pt
                        tagmetadata.save()

                    return JsonResponse({'code': 200, 'message': 'Guardado Correctamente'})

                except Tag.DoesNotExist as e:
                    return JsonResponse({'code': 500, 'message': e.message})
                except TagMetadata.DoesNotExist as e:
                    return JsonResponse({'code': 500, 'message': e.message})
                except Exception as e:
                    return JsonResponse({'code': 500, 'message': e.message})

        #GET

        tag = Tag.objects.get(tag_id=tag_id)
        lang_es = Language.objects.get(code='es')
        lang_pt = Language.objects.get(code='pt')
        item_metadata_es=''
        item_metadata_pt=''



        if TagMetadata.objects.filter(tag=tag, language=lang_es).count() > 0:

            item_metadata_es = TagMetadata.objects.get(tag=tag, language=lang_es)
        if TagMetadata.objects.filter(tag=tag, language=lang_pt)>0:

            item_metadata_pt = TagMetadata.objects.get(tag=tag, language=lang_pt)


        context = {'item': tag, 'item_metadata_es': item_metadata_es, 'item_metadata_pt': item_metadata_pt}
        return render(request, 'cawas/tags/edit.html', context)








    def delete(self, request):
        data = {'code': 200, 'message': 'Eliminado Correctamente'}
        return HttpResponse(json.dumps(data), None, 200)



    def findAll(self):
        data =[
                {'id': 1, 'description': 'Tag 1'},
                {'id': 2, 'description': 'Tag 2'},
               ]
        return HttpResponse(json.dumps(data), None, 200)



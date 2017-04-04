import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import Asset, Setting, Girl, GirlMetadata, Category, Language, Image
from ..Helpers.PublishHelper import PublishHelper

class GirlController(object):
    #Atributos
    decjson=""
    vimg=Image()
    vgirl=Girl()


    #respuestas, 0 = ok, 2= login
    def add(self, request):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))

        message = ''
        vflag = ""
        vimg = Image()

        try:
            pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
        except Setting.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})

        # POST - Obtener datos del formulario y guardar la metadata
        if request.method == 'POST':
            # parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)

            # VARIABLES - (esta logica pasa al controlador)
            vgirl = Girl()
            vasset = Asset()
            vasset.asset_type = "girl"
            vasset.save()

            try:
                vimg.name = vasset.asset_id
                # IMAGEN Portrait
                if (request.FILES.has_key('ThumbHor')):
                    if request.FILES['ThumbHor'].name != '':
                        vimg.portrait = request.FILES['ThumbHor']
                        extension = os.path.splitext(vimg.portrait.name)[1]
                        varchivo = pathfilesport.value + vimg.name + extension
                        vimg.portrait.name = varchivo
                        if os.path.isfile(varchivo):
                            os.remove(varchivo)

                # IMAGEN Landscape
                if (request.FILES.has_key('ThumbVer')):
                    if request.FILES['ThumbVer'].name != '':
                        vimg.landscape = request.FILES['ThumbVer']
                        extension = os.path.splitext(vimg.landscape.name)[1]
                        varchivo = pathfilesland.value + vimg.name + extension
                        vimg.landscape.name = varchivo
                        if os.path.isfile(varchivo):
                            os.remove(varchivo)
                vimg.save()

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
                # Publica en PublishQueue

                # Luego del POST redirige a pagina principal
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

                ph = PublishHelper()
                ph.func_publish_queue(request, vasset.asset_id, vlanguage, 'AS', 'Q', vschedule_date)
                ph.func_publish_image(request, vimg)

            #return True


        # Cargar variables para presentar en templates
        vgirls = Girl.objects.all()
        vcategories = Category.objects.all()
        vlanguages = Language.objects.all()

        vtypegirl = {"pornstar": "Pornstar", "playmate": "Playmate"}
        context = {'message': message, 'vgirls': vgirls, 'vcategories': vcategories, 'vlanguages': vlanguages,
                   'vtypegirl': vtypegirl,
                   'flag': vflag}
        # checks:
        # Imagenes - OK
        # Girl - OK
        # Girl metadata - OK
        # Publishqueue - NO
        # Publishimage - NO
        return render(request, 'cawas/girls/add.html', context)




    #EDICION DE GIRL
    def edit(self, request, asset_id):
     #AUTENTICACION DE USUARIO

        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))


        #VARIABLES PARA GET - CARGAR GIRL
        try:
            message = ''
            vlangmetadata = []
            pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            vasset = Asset.objects.get(asset_id=asset_id)
            vgirl = Girl.objects.get(asset=vasset)
            vtypegirl = {"pornstar": "Pornstar", "playmate": "Playmate"}
            vlanguages = Language.objects.all()
        # carga imagenes
            i = len(vgirl.image.portrait.name)
            imgport = vgirl.image.portrait.name[5:i]
            i = len(vgirl.image.landscape.name)
            imgland = vgirl.image.landscape.name[5:i]
        #Nuevo diccionario para completar lenguages y metadata
            for itemlang in vlanguages:
                vgirlmetadata = None
                try:
                    vgirlmetadata = GirlMetadata.objects.get(girl=vgirl, language=itemlang)
                    vlangmetadata.append(
                        {'checked': True, 'code': itemlang.code, 'name': itemlang.name,
                         'description': vgirlmetadata.description,
                         'nationality': vgirlmetadata.nationality})
                except GirlMetadata.DoesNotExist as a:
                    vlangmetadata.append({'checked': False, 'code': itemlang.code, 'name': itemlang.name, 'description': '', 'nationality': ''})
        except Setting.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})
        except Girl.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Asset no se encuentra Vinculado a Girl. (" + e.message + ")"})
        except Asset.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Asset no Existe. (" + e.message + ")"})
        except Category.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Categoria no Existe. (" + e.message + ")"})
        except GirlMetadata.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "GirlMetaData No Existe . (" + e.message + ")"})


        if request.method == 'POST':
            #VARIABLES
            vasset = Asset()
            vgirl = Girl()
            # Parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)

            # Leer GIRL desde AssetID
            try:
                vasset = Asset.objects.get(asset_id=decjson['Girl']['asset_id'])
                vgirl = Girl.objects.get(asset=vasset)
                #verificar imagen
                vimg = Image.objects.get(name=vasset.asset_id)

            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "Asset no Existe. (" + e.message + ")"})
            except GirlMetadata.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "GirlMetaData No Existe . (" + e.message + ")"})
            except Image.DoesNotExist as e:
                vimg = Image()

            # IMAGEN Portrait
            if (request.FILES.has_key('ThumbHor')):
                if request.FILES['ThumbHor'].name != '':
                    vimg.portrait = request.FILES['ThumbHor']
                    extension = os.path.splitext(vimg.portrait.name)[1]
                    vimg.name = vasset.asset_id
                    varchivo = pathfilesport.value + vimg.name + extension
                    vimg.portrait.name = varchivo
                    if os.path.isfile(varchivo):
                        os.remove(varchivo)

            # IMAGEN Landscape
            if (request.FILES.has_key('ThumbVer')):
                if request.FILES['ThumbVer'].name != '':
                    vimg.landscape = request.FILES['ThumbVer']
                    extension = os.path.splitext(vimg.landscape.name)[1]
                    varchivo = pathfilesland.value + vimg.name + extension
                    vimg.landscape.name = varchivo
                    if os.path.isfile(varchivo):
                        os.remove(varchivo)

            vimg.save()

            #Actualiza Girl
            try:
                vgirl.name = decjson['Girl']['name']
                vgirl.type = decjson['Girl']['type_girl']
                vgirl.birth_date = datetime.datetime.strptime(decjson['Girl']['birth_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
                vgirl.height = decjson['Girl']['height']
                vgirl.weight = decjson['Girl']['weight']
                vgirl.image = vimg
                vgirl.save()
            except Exception as e:
                return render(request, 'cawas/error.html', {"message": "Error al Guardar Girl. (" + str(e.message) + ")."})


            #BORRAR Y CREAR METADATA
            vgirlmetadatas = decjson['Girl']['Girlmetadatas']
            gmds = GirlMetadata.objects.filter(girl=vgirl).delete()

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
                ph = PublishHelper()
                ph.func_publish_queue(request, vasset.asset_id, vlanguage, 'AS', 'Q', vschedule_date)
                # Publica en PublishImage
                ph.func_publish_image(request, vimg)
            context = {'vflag': 'success'}
            return render(request, 'cawas/girls/add.html', context)
            #return True
            #Luego del POST redirige a pagina principal
            #



        context = {'message': message,  'vlanguages': vlanguages, 'vgirl':vgirl, 'vtypegirl':vtypegirl,'vlangmetadata':vlangmetadata,
                   'imgport':imgport, 'imgland':imgland}
        # checks:
        return render(request, 'cawas/girls/edit.html', context)
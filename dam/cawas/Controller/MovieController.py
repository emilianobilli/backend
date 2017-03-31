import os, datetime, json
from LogController import LogController
from django.shortcuts import render,redirect
from ..models import Asset, Setting, Movie, MovieMetadata, Category, Language, Image, Girl, PublishZone, Channel, PublishQueue, ImageQueue
from ..Helpers.PublishHelper import PublishHelper

class MovieController(object):

    def add(self, request):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))
        # return redirect(login_view)
        # ALTA - MOVIE: en el GET debe cargar variables, y en POST debe leer JSON
        # cawas/static/images/landscape/  cawas/static/images/portrait/

        vflag = ""
        if request.method == 'POST':

            # parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)

            # DECLARACION DE OBJECTOS
            mv = Movie()
            vasset = Asset()

            # CARGAR MOVIE
            try:
                vasset = Asset.objects.get(asset_id=decjson['Movie']['asset_id'])
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})

            # VALIDAR IMAGEN
            try:
                img = Image.objects.get(name=vasset.asset_id)
            except Image.DoesNotExist as e:
                vflag = "error"
                img = Image()

            try:
                pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
                pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            except Setting.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})

            # TRATAMIENTO DE IMAGEN Portrait
            img.portrait = request.FILES['ThumbHor']
            extension = os.path.splitext(img.portrait.name)[1]
            img.name = vasset.asset_id
            varchivo = pathfilesport.value + img.name + extension
            img.portrait.name = varchivo

            if os.path.isfile(varchivo):
                os.remove(varchivo)

            # Landscape
            img.landscape = request.FILES['ThumbVer']
            extension = os.path.splitext(img.landscape.name)[1]
            varchivo = pathfilesland.value + img.name + extension
            img.landscape.name = varchivo
            # si existe archivo, lo borra
            if os.path.isfile(varchivo):
                os.remove(varchivo)

            img.save()
            mv.image = img

            # Channel
            try:
                vchannel = Channel.objects.get(pk=decjson['Movie']['channel_id'])
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})

            mv.asset = vasset
            mv.channel = vchannel
            mv.original_title = decjson['Movie']['original_title']

            if (decjson['Movie']['year'] is not None):
                mv.year = decjson['Movie']['year']
            if (decjson['Movie']['cast'] is not None):
                mv.cast = decjson['Movie']['cast']
            if (decjson['Movie']['directors'] is not None):
                mv.cast = decjson['Movie']['directors']

            mv.display_runtime = decjson['Movie']['display_runtime']
            # calcular runtime
            # mv.runtime
            mv.save()

            # CARGAR GIRLS
            if (decjson['Movie']['girls'] is not None):
                vgirls = decjson['Movie']['girls']
                for item in vgirls:
                    try:
                        vgirl = Girl.objects.get(pk=item['girl_id'])
                        mv.girls.add(vgirl)
                    except Girl.DoesNotExist as e:
                        return render(request, 'cawas/error.html', {"message": "No existe Girl. (" + e.message + ")"})

            # CARGAR CATEGORIES
            vcategories = decjson['Movie']['categories']
            for item in vcategories:
                try:
                    vcategory = Category.objects.get(pk=item['category_id'])
                    mv.category.add(vcategory)
                except Category.DoesNotExist as e:
                    vflag = "error"
                    return render(request, 'cawas/error.html', {"message": "No existe Categoria. (" + e.message + ")"})

            # ACTUALIZAR EL ASSET A MOVIE
            vasset.asset_type = "movie"
            vasset.save()

            # CARGAR METADATA
            vmoviesmetadata = decjson['Movie']['Moviesmetadata']

            for item in vmoviesmetadata:
                try:
                    # CREAR METADATA POR IDIOMA
                    vlanguage = Language.objects.get(code=item['Moviemetadata']['language'])
                    if (item['Moviemetadata']['schedule_date'] != ''):
                        vpublishdate = datetime.datetime.strptime(item['Moviemetadata']['schedule_date'],
                                                                  '%d-%m-%Y').strftime('%Y-%m-%d')
                    else:
                        vpublishdate = datetime.datetime.now().strftime('%Y-%m-%d')

                    try:
                        mmd = MovieMetadata.objects.get(movie=mv, language=vlanguage)
                    except MovieMetadata.DoesNotExist as e:
                        mmd = MovieMetadata();
                    mmd.language = vlanguage
                    mmd.title = item['Moviemetadata']['title']
                    mmd.summary_short = item['Moviemetadata']['summary_short']
                    mmd.summary_long = item['Moviemetadata']['summary_long']
                    mmd.publish_date = vpublishdate
                    mmd.movie = mv
                    mmd.save()

                    # Recorrer el publicZone y genera un PublicQueue por cada idioma

                    vzones = PublishZone.objects.filter(enabled=True)
                    for zone in vzones:
                        # CREAR COLA DE PUBLICACION
                        vpublish = PublishQueue()
                        vpublish.item_id = vasset.asset_id
                        vpublish.item_lang = vlanguage
                        vpublish.item_type = 'AS'
                        vpublish.status = 'Q'
                        vpublish.publish_zone = zone
                        vpublish.schedule_date = vpublishdate
                        vpublish.save()

                except Language.DoesNotExist as e:
                    return render(request, 'cawas/error.html', {"message": "No existe Lenguaje. (" + e.message + ")"})
                except Exception as e:
                    return render(request, 'cawas/error.html',
                                  {"message": "Error al Guardar metadata. (" + e.message + ")"})

            # COLA DE PUBLICACION PARA IMAGENES
            try:
                vzones = PublishZone.objects.filter(enabled=True)
                for zone in vzones:
                    imgQueue = ImageQueue()
                    imgQueue.image = img
                    imgQueue.publish_zone = zone
                    imgQueue.schedule_date = datetime.datetime.now()
                    imgQueue.save()
            except Exception as e:
                return render(request, 'cawas/error.html',
                              {"message": "Error al Generar Cola de Imagen. (" + e.message + ")"})
            vflag = "success"
            message = 'Registrado correctamente'
            # FIN DE POST

        # VARIABLES PARA GET
        # CARGAR VARIABLES USADAS EN FRONT
        assets = Asset.objects.filter(asset_type="unknown")
        vmovies = Movie.objects.all()
        channels = Channel.objects.all()
        girls = Girl.objects.all()
        categories = Category.objects.all()
        vlanguages = Language.objects.all()
        title = 'Nueva Movie'
        context = {'title': title, 'assets': assets, 'channels': channels, 'girls': girls, 'categories': categories,
                   'movies': vmovies, 'vlanguages': vlanguages, 'flag': vflag}
        return render(request, 'cawas/movies/add.html', context)



    def edit(self, request, asset_id):
        # AUTENTICACION DE USUARIO
        if not request.user.is_authenticated:
            lc = LogController()
            return redirect(lc.login_view(request))
        # EDIT - MOVIE: en el GET debe cargar variables, y en POST debe leer JSON
        vlangmetadata = []

        try:
            pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
        except Setting.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})

        # Post Movie - Graba datos
        if request.method == 'POST':
            # parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)

            # DECLARACION DE OBJECTOS
            mv = Movie()
            vasset = Asset()

            # Leer Movie desde AssetID
            # CARGAR MOVIE
            try:
                vasset = Asset.objects.get(asset_id=asset_id)
                mv = Movie.objects.get(asset=vasset)
                img = Image.objects.get(name=vasset.asset_id)

                vchannel = Channel.objects.get(pk=decjson['Movie']['channel_id'])
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})
            except Movie.DoesNotExist as e:
                return render(request, 'cawas/error.html',
                              {"message": "No existe Movie asociado al Asset. (" + e.message + ")"})
            except Image.DoesNotExist as e:
                img = Image()
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})

            # IMAGEN Portrait
            if (request.FILES.has_key('ThumbHor')):
                if request.FILES['ThumbHor'].name != '':
                    img.portrait = request.FILES['ThumbHor']
                    extension = os.path.splitext(img.portrait.name)[1]
                    img.name = vasset.asset_id
                    varchivo = pathfilesport.value + img.name + extension
                    img.portrait.name = varchivo
                    if os.path.isfile(varchivo):
                        os.remove(varchivo)

            # IMAGEN Landscape
            if (request.FILES.has_key('ThumbVer')):
                if request.FILES['ThumbVer'].name != '':
                    img.landscape = request.FILES['ThumbVer']
                    extension = os.path.splitext(img.landscape.name)[1]
                    varchivo = pathfilesland.value + img.name + extension
                    img.landscape.name = varchivo
                    if os.path.isfile(varchivo):
                        os.remove(varchivo)

            img.save()
            mv.image = img
            mv.asset = vasset
            mv.channel = vchannel
            mv.original_title = decjson['Movie']['original_title']

            if (decjson['Movie']['year'] is not None):
                mv.year = decjson['Movie']['year']
            if (decjson['Movie']['cast'] is not None):
                mv.cast = decjson['Movie']['cast']
            if (decjson['Movie']['directors'] is not None):
                mv.cast = decjson['Movie']['directors']

            mv.display_runtime = decjson['Movie']['display_runtime']
            # calcular runtime
            # mv.runtime
            mv.save()

            # CARGAR GIRLS
            if (decjson['Movie']['girls'] is not None):
                vgirls = decjson['Movie']['girls']
                for item in vgirls:
                    try:
                        vgirl = Girl.objects.get(pk=item['girl_id'])
                        mv.girls.add(vgirl)
                    except Girl.DoesNotExist as e:
                        return render(request, 'cawas/error.html', {"message": "No existe Girl. (" + e.message + ")"})

            # CARGAR CATEGORIES
            vcategories = decjson['Movie']['categories']
            for item in vcategories:
                try:
                    vcategory = Category.objects.get(pk=item['category_id'])
                    mv.category.add(vcategory)
                except Category.DoesNotExist as e:
                    return render(request, 'cawas/error.html', {"message": "No existe Categoria. (" + e.message + ")"})

            # ACTUALIZAR EL ASSET A MOVIE
            vasset.asset_type = "movie"
            vasset.save()

            # CARGAR METADATA
            vmoviesmetadata = decjson['Movie']['Moviesmetadata']
            # eliminar las movies metadata existentes


            MovieMetadata.objects.filter(movie=mv).delete()
            for item in vmoviesmetadata:
                if (item['Moviemetadata']['schedule_date'] != ''):
                    vpublishdate = datetime.datetime.strptime(item['Moviemetadata']['schedule_date'],
                                                              '%d-%m-%Y').strftime('%Y-%m-%d')
                else:
                    vpublishdate = datetime.datetime.now().strftime('%Y-%m-%d')

                try:
                    # CREAR METADATA POR IDIOMA
                    vlanguage = Language.objects.get(code=item['Moviemetadata']['language'])
                    try:
                        mmd = MovieMetadata.objects.get(movie=mv, language=vlanguage)
                    except MovieMetadata.DoesNotExist as e:
                        mmd = MovieMetadata();
                    mmd.language = vlanguage
                    mmd.movie = mv
                    mmd.title = item['Moviemetadata']['title']
                    mmd.summary_short = item['Moviemetadata']['summary_short']
                    mmd.summary_long = item['Moviemetadata']['summary_long']
                    mmd.publish_date = vpublishdate

                    mmd.save()
                    print "titulo title:" + mmd.title
                    # Recorrer el publicZone y genera un PublicQueue por cada idioma

                    vzones = PublishZone.objects.filter(enabled=True)
                    for zone in vzones:
                        # CREAR COLA DE PUBLICACION
                        vpublish = PublishQueue()
                        vpublish.item_id = vasset.asset_id
                        vpublish.item_lang = vlanguage
                        vpublish.item_type = 'AS'
                        vpublish.status = 'Q'
                        vpublish.publish_zone = zone
                        vpublish.schedule_date = vpublishdate
                        vpublish.save()

                except Language.DoesNotExist as e:
                    return render(request, 'cawas/error.html', {"message": "No existe Lenguaje. (" + e.message + ")"})
                except Exception as e:
                    return render(request, 'cawas/error.html',
                                  {"message": "Error al Guardar metadata. (" + e.message + ")"})

            # COLA DE PUBLICACION PARA IMAGENES
            try:
                vzones = PublishZone.objects.filter(enabled=True)
                for zone in vzones:
                    imgQueue = ImageQueue()
                    imgQueue.image = img
                    imgQueue.publish_zone = zone
                    imgQueue.schedule_date = datetime.datetime.now()
                    imgQueue.save()
            except Exception as e:
                return render(request, 'cawas/error.html',
                              {"message": "Error al Generar Cola de Imagen. (" + e.message + ")"})

            message = 'archivo subido ok'
            return redirect(menu_view)
            # FIN DE POST

        # VARIABLES PARA GET - CARGAR MOVIE
        try:
            vasset = Asset.objects.get(asset_id=asset_id)
            vmovie = Movie.objects.get(asset=vasset)

            i = len(vmovie.image.portrait.name)
            imgport = vmovie.image.portrait.name[5:i]

            i = len(vmovie.image.landscape.name)
            imgland = vmovie.image.landscape.name[5:i]

            vgirlselected = vmovie.girls.all()
            vgirlnotselected = Girl.objects.exclude(id__in=vgirlselected)
            vgirlselected = vmovie.girls.all()

            vmoviemetadata = MovieMetadata.objects.filter(movie=vmovie)
            vcategoryselected = vmovie.category.all()
            vcategorynotselected = Category.objects.exclude(id__in=vcategoryselected)
            languages = Language.objects.all()

            # nuevo diccionario para completar lenguages y metadata
            for itemlang in languages:
                vmoviemetadata = None
                try:
                    vmoviemetadata = MovieMetadata.objects.get(movie=vmovie, language=itemlang)
                    vlangmetadata.append(
                        {'checked': True, 'code': itemlang.code, 'name': itemlang.name, 'title': vmoviemetadata.title,
                         'summary_short': vmoviemetadata.summary_short, 'summary_long': vmoviemetadata.summary_long,
                         'publish_date': vmoviemetadata.publish_date})
                except MovieMetadata.DoesNotExist as a:
                    vlangmetadata.append({'checked': False, 'code': itemlang.code, 'name': itemlang.name, 'titulo': '',
                                          'descripcion': '', 'fechapub': ''})

        except Movie.DoesNotExist as e:
            return render(request, 'cawas/error.html',
                          {"message": "Asset no se encuentra Vinculado a Movie. (" + e.message + ")"})
        except Asset.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Asset no Existe. (" + e.message + ")"})
        except Category.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "Categoria no Existe. (" + e.message + ")"})
        except MovieMetadata.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "MovieMetaData No Existe . (" + e.message + ")"})

        # CARGAR VARIABLES USADAS EN FRONT
        assets = Asset.objects.filter(asset_type="unknown")
        channels = Channel.objects.all()
        girls = Girl.objects.all()
        categories = Category.objects.all()
        languages = Language.objects.all()
        title = 'Editar Movie'

        context = {'title': title, 'assets': assets, 'channels': channels, 'girls': girls, 'categories': categories,
                   'vmovie': vmovie, 'vgirlselected': vgirlselected, 'vgirlnotselected': vgirlnotselected,
                   'vcategoryselected': vcategoryselected, 'vcategorynotselected': vcategorynotselected,
                   'languages': languages, 'vmoviemetadata': vmoviemetadata, 'vlangmetadata': vlangmetadata,
                   'asset_id': asset_id, 'imgland': imgland, 'imgport': imgport}

        return render(request, 'cawas/movies/edit.html', context)
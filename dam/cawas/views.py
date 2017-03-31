# Create your views here.
import os, datetime, json
from django.shortcuts import render,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.http import  HttpResponse
from Controller.GirlController import GirlController
from Controller.MovieController import MovieController
from Controller.LogController import LogController
from models import Channel, Device, Slider, SliderMetadata, Episode, EpisodeMetadata, ImageQueue, PublishQueue, \
    Block, Serie, SerieMetadata, Movie, MovieMetadata, CategoryMetadata, PublishZone,Girl, GirlMetadata, Asset, Language, Category, Image, Setting
from django.contrib.auth import authenticate, login, logout
#from ..backend_sdk import ApiBackendResource



#FUNCIONES GENERALES
#Funcion para publicar Asset
def func_publish_queue(pid, planguage, pitem_type, pstatus,  pschedule_date):
    #fecha pschedule_date: ya tiene que estar parceada como strftime('%Y-%m-%d')

    vzones = PublishZone.objects.filter(enabled=True)
    for zone in vzones:
        # CREAR COLA DE PUBLICACION
        vpublish = PublishQueue()
        vpublish.item_id = pid
        vpublish.item_lang = planguage
        vpublish.item_type = pitem_type
        vpublish.status = pstatus
        vpublish.publish_zone = zone
        vpublish.schedule_date = pschedule_date
        vpublish.save()
        #except Exception as e:
        #    return render(request, 'cawas/error.html', {"message": "No existe Lenguaje. (" + e.message + ")"})


def func_publish_image(pimg):
    # COLA DE PUBLICACION PARA IMAGENES
    #try:
    vzones = PublishZone.objects.filter(enabled=True)
    for zone in vzones:
        imgQueue = ImageQueue()
        imgQueue.image = pimg
        imgQueue.publish_zone = zone
        imgQueue.schedule_date = datetime.datetime.now()
        imgQueue.save()
    #except Exception as e:
    #    return render(context , 'cawas/error.html',{"message": "Error al Generar Cola de Imagen. (" + e.message + ")"})

#/FUNCIONES GENERALES


def login_view(request):
    message='';
    if request.method == 'POST':
        username = request.POST['InputUser']
        password = request.POST['InputPassword']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(menu_view)
        else:
            message = 'Usuario o Contrasenia Incorrecto.'

    context = {'message': message}
    return render(request, 'cawas/login.html', context)


def menu_view (request):
    if not request.user.is_authenticated:
        return redirect(login_view)

    #<Definir Variables>
    idassetstype = 0
    message = 'Hay 0 contenidos sin publicar.'
    contentypes = (
        (1, "MOVIE"),
        (2, "BLOQUES"),
        (3, "CHICAS"),
        (4, "CATEGORIAS"),
        (5, "CAPITULOS"),
        (6, "SLIDERS")
    )

    assetstypes = (
        (1, "Movies"),
        (2, "Serie"),
        (3, "Bloques"),
        (4, "Chicas"),
        (6, "Capitulos"),
        (7, "Sliders")
    )
    # </Definir Variables>

    # si hizo click en menu_view.cargar_contenido
    if request.method == 'POST':
        idassetstype = request.POST['selassetstypes']
        #redireccionar segun tipo de contenido
        if(int(idassetstype) == 1):
            return redirect(add_movies_view)

    title = 'Menu Principal'
    context = {'title': title, 'assetstypes':assetstypes, 'message': message ,  'idassetstype': idassetstype}
    return render(request, 'cawas/menu.html', context)


def logout_view(request):
    logout(request)
    return redirect(login_view)



#<CRUD MOVIES>
def index_movies_view(request, opcion = 0):
    if not request.user.is_authenticated:
       return redirect(login_view)


    #SI ESTA AUTORIZADO...
    movies={}
    if request.method == 'GET':
        opcion = request.GET['opcion']
        if (opcion == 1): #pedientes de publicacion
            assets = Episode.objects.all()
        if (opcion == 2): #ver todas las movies cargadas
            assets = Episode.objects.all()
        if (opcion == 3): #serie y capitulos cargados
            assets = Episode.objects.all()
        if (opcion == 4): # ver todos los bloques cargados
            assets = Episode.objects.all()
        if (opcion == 5):  # ver todas las girls cargadas
            assets = Episode.objects.all()
        paginator = Paginator(assets, 25)

    id = 0

    if request.method =='POST':
        id = request.POST['inputid']
        if (id > 0):
            assets = Episode.objects.filter(asset=id)
        else:
            assets = Episode.objects.all()

    title = 'Movies'
    episodies = Episode.objects.all()
    context = {'episodies':episodies , 'assets':assets, 'title': title, 'opcion': opcion, 'id': id}
    return render(request, 'cawas/menu.html', context)







def prueba_json_view(request):
    if not request.user.is_authenticated:
        return redirect(login_view)

    context = {}
    return render(request, 'cawas/pruebas/prueba_json.html', context)




def add_movies_view(request):
    mc = MovieController()
    return mc.add(request)

'''
    if not request.user.is_authenticated:
       return redirect(login_view)
    #ALTA - MOVIE: en el GET debe cargar variables, y en POST debe leer JSON
    #cawas/static/images/landscape/  cawas/static/images/portrait/

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


       #VALIDAR IMAGEN
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

       #TRATAMIENTO DE IMAGEN Portrait
       img.portrait = request.FILES['ThumbHor']
       extension = os.path.splitext(img.portrait.name)[1]
       img.name = vasset.asset_id
       varchivo = pathfilesport.value + img.name + extension
       img.portrait.name = varchivo

       if os.path.isfile(varchivo):
           os.remove(varchivo)

       #Landscape
       img.landscape = request.FILES['ThumbVer']
       extension = os.path.splitext(img.landscape.name)[1]
       varchivo = pathfilesland.value + img.name + extension
       img.landscape.name = varchivo
       # si existe archivo, lo borra
       if os.path.isfile(varchivo):
           os.remove(varchivo)

       img.save()
       mv.image = img

       #Channel
       try:
           vchannel = Channel.objects.get(pk=decjson['Movie']['channel_id'])
       except Asset.DoesNotExist as e:
           return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})

       mv.asset = vasset
       mv.channel = vchannel
       mv.original_title = decjson['Movie']['original_title']

       if (decjson['Movie']['year']is not None ):
           mv.year = decjson['Movie']['year']
       if (decjson['Movie']['cast'] is not None):
            mv.cast = decjson['Movie']['cast']
       if (decjson['Movie']['directors'] is not None):
           mv.cast = decjson['Movie']['directors']

       mv.display_runtime = decjson['Movie']['display_runtime']
       #calcular runtime
       #mv.runtime
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
               #CREAR METADATA POR IDIOMA
               vlanguage = Language.objects.get(code=item['Moviemetadata']['language'])
               if (item['Moviemetadata']['schedule_date']!=''):
                   vpublishdate = datetime.datetime.strptime(item['Moviemetadata']['schedule_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
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

               #Recorrer el publicZone y genera un PublicQueue por cada idioma

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
               return render(request, 'cawas/error.html', {"message": "Error al Guardar metadata. (" + e.message + ")"})


       #COLA DE PUBLICACION PARA IMAGENES
       try:
           vzones = PublishZone.objects.filter(enabled=True)
           for zone in vzones:
               imgQueue = ImageQueue()
               imgQueue.image = img
               imgQueue.publish_zone = zone
               imgQueue.schedule_date = datetime.datetime.now()
               imgQueue.save()
       except Exception as e:
           return render(request, 'cawas/error.html', {"message": "Error al Generar Cola de Imagen. (" + e.message + ")"})
       vflag = "success"
       message = 'Registrado correctamente'
       #FIN DE POST


    #VARIABLES PARA GET
    #CARGAR VARIABLES USADAS EN FRONT
    assets = Asset.objects.filter(asset_type="unknown")
    vmovies = Movie.objects.all()
    channels = Channel.objects.all()
    girls = Girl.objects.all()
    categories = Category.objects.all()
    vlanguages = Language.objects.all()
    title = 'Nueva Movie'
    context = {'title': title, 'assets':assets, 'channels':channels, 'girls':girls,  'categories':categories,
               'movies':vmovies, 'vlanguages':vlanguages, 'flag':vflag }
    return render(request, 'cawas/movies/add.html', context)
    '''

# Fin add_movies_view



def edit_movies_view(request, asset_id):
    mc = MovieController()
    return mc.edit(request, asset_id)

    '''
    #AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
       return redirect(login_view)
    # EDIT - MOVIE: en el GET debe cargar variables, y en POST debe leer JSON
    vlangmetadata = []

    try:
        pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
        pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
    except Setting.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})

    #Post Movie - Graba datos
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
           return render(request, 'cawas/error.html', {"message": "No existe Movie asociado al Asset. (" + e.message + ")"})
       except Image.DoesNotExist as e:
           img = Image()
       except Asset.DoesNotExist as e:
           return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})

       #IMAGEN Portrait
       if (request.FILES.has_key('ThumbHor')):
          if request.FILES['ThumbHor'].name != '':
              img.portrait = request.FILES['ThumbHor']
              extension = os.path.splitext(img.portrait.name)[1]
              img.name = vasset.asset_id
              varchivo = pathfilesport.value + img.name + extension
              img.portrait.name = varchivo
              if os.path.isfile(varchivo):
                  os.remove(varchivo)

       #IMAGEN Landscape
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

       if (decjson['Movie']['year']is not None ):
           mv.year = decjson['Movie']['year']
       if (decjson['Movie']['cast'] is not None):
            mv.cast = decjson['Movie']['cast']
       if (decjson['Movie']['directors'] is not None):
           mv.cast = decjson['Movie']['directors']

       mv.display_runtime = decjson['Movie']['display_runtime']
       #calcular runtime
       #mv.runtime
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
       #eliminar las movies metadata existentes


       MovieMetadata.objects.filter(movie=mv).delete()
       for item in vmoviesmetadata:
           if (item['Moviemetadata']['schedule_date'] != ''):
               vpublishdate = datetime.datetime.strptime(item['Moviemetadata']['schedule_date'],
                                                         '%d-%m-%Y').strftime('%Y-%m-%d')
           else:
               vpublishdate = datetime.datetime.now().strftime('%Y-%m-%d')

           try:
               #CREAR METADATA POR IDIOMA
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
               #Recorrer el publicZone y genera un PublicQueue por cada idioma

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
               return render(request, 'cawas/error.html', {"message": "Error al Guardar metadata. (" + e.message + ")"})

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



    #VARIABLES PARA GET - CARGAR MOVIE
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

        #nuevo diccionario para completar lenguages y metadata
        for itemlang in languages:
            vmoviemetadata = None
            try:
                vmoviemetadata = MovieMetadata.objects.get(movie=vmovie, language=itemlang)
                vlangmetadata.append(
                    {'checked': True, 'code': itemlang.code, 'name': itemlang.name, 'title': vmoviemetadata.title,
                     'summary_short': vmoviemetadata.summary_short, 'summary_long': vmoviemetadata.summary_long,
                     'publish_date': vmoviemetadata.publish_date})
            except MovieMetadata.DoesNotExist as a:
                vlangmetadata.append({'checked':False, 'code':itemlang.code, 'name':itemlang.name,'titulo':'', 'descripcion':'', 'fechapub':''})

    except Movie.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Asset no se encuentra Vinculado a Movie. (" + e.message + ")"})
    except Asset.DoesNotExist as e:
        return render(request, 'cawas/error.html',{"message": "Asset no Existe. (" + e.message + ")"})
    except Category.DoesNotExist as e:
        return render(request, 'cawas/error.html',{"message": "Categoria no Existe. (" + e.message + ")"})
    except MovieMetadata.DoesNotExist as e:
        return render(request, 'cawas/error.html',{"message": "MovieMetaData No Existe . (" + e.message + ")"})


    #CARGAR VARIABLES USADAS EN FRONT
    assets = Asset.objects.filter(asset_type="unknown")
    channels = Channel.objects.all()
    girls = Girl.objects.all()
    categories = Category.objects.all()
    languages = Language.objects.all()
    title = 'Editar Movie'

    context = {'title': title, 'assets':assets, 'channels':channels, 'girls':girls, 'categories':categories,
               'vmovie':vmovie, 'vgirlselected':vgirlselected, 'vgirlnotselected':vgirlnotselected,
               'vcategoryselected':vcategoryselected, 'vcategorynotselected':vcategorynotselected,
               'languages':languages, 'vmoviemetadata':vmoviemetadata, 'vlangmetadata':vlangmetadata,
               'asset_id':asset_id,  'imgland':imgland, 'imgport':imgport}

    return render(request, 'cawas/movies/edit.html', context)
    '''
# Fin edit_movies_view

#</CRUD MOVIES>









#<ADD GIRL>
def add_girls_view(request):
    gc = GirlController()
    return gc.add(request)

#</fin ADD Girl>


def edit_girls_view(request, asset_id):
    #AUTENTICACION DE USUARIO
    gc = GirlController()
    #if request.method == 'GET':
    return gc.edit(request, asset_id)
    #if request.method == 'POST':
        #Si respuesta es True, quiere decir que se Grabo correctamente
    #    return gc.edit(request, asset_id)

#</Fin EDIT Girl>










#<CRUD SERIE>
def add_series_view(request):
    # AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)

    # VARIABLES LOCALES
    message = ''
    if request.method == 'POST':
        #VARIABLES
        vserie = Serie()
        vimg = Image()

        vasset = Asset()
        vasset.asset_type = "serie"
        vasset.save()

        # Parsear JSON
        strjson = request.POST['varsToJSON']
        decjson = json.loads(strjson)
        try:
            pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
        except Setting.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})

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
        #FIN IMAGEN

        #Datos de Serie
        vserie.asset = vasset
        vserie.original_title = decjson['Serie']['original_title']
        vserie.year = decjson['Serie']['year']
        vserie.cast = decjson['Serie']['cast']
        vserie.directors = decjson['Serie']['directors']
        vserie.image = vimg
        vserie.save()

        # CARGAR GIRLS
        vgirls = decjson['Serie']['girls']
        for item in vgirls:
            try:
                g = Girl.objects.get(pk=item['girl_id'])
                vserie.girls.add(g)
            except Girl.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Girl. (" + e.message + ")"})

        # CARGAR CATEGORIES
        vcategories = decjson['Serie']['categories']
        for item in vcategories:
            try:
                vserie.category.add(Category.objects.get(pk=item['category_id']))
            except Category.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Category. (" + e.message + ")"})

        #Channel
        try:
            vserie.channel = Channel.objects.get(pk=decjson['Serie']['channel_id'])
        except Channel.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Channel. (" + e.message + ")"})

        vserie.save()
        message = 'Categoria - Registrado Correctamente'
        #Fin datos serie

        # BORRAR Y CREAR METADATA
        vseriemetadatas = decjson['Serie']['Seriemetadatas']
        for item in vseriemetadatas:
            smd = SerieMetadata()
            try:
                smd.language = Language.objects.get(code=item['Seriemetadata']['language'])
            except Language.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe LANGUAGE. (" + e.message + ")"})
            vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
            smd.title = item['Seriemetadata']['title']
            smd.summary_short = item['Seriemetadata']['summary_short']
            smd.summary_long = item['Seriemetadata']['summary_long']
            smd.serie = vserie
            smd.publish_date = vschedule_date
            smd.save()

            # Publica en PublishQueue
            func_publish_queue(vasset.asset_id, smd.language, 'AS', 'Q', vschedule_date)

            # Publica en PublishImage
            func_publish_image(vimg)
        #Fin de POST



    # VARIABLES PARA GET - CARGAR GIRL
    try:
        message = ''


        vlanguages = Language.objects.all()
        vgirls = Girl.objects.all()
        vcategories = Category.objects.all()
        vchannels = Channel.objects.all()
        vseries = Serie.objects.all()


    except Serie.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Serie No Existe . (" + e.message + ")"})
    except Girl.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Girl No Existe . (" + e.message + ")"})
    except Category.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Categoria no Existe. (" + e.message + ")"})
    except Channel.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Canal no Existe. (" + e.message + ")"})
    except GirlMetadata.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "GirlMetaData No Existe . (" + e.message + ")"})

    context = {'message': message,'vgirls': vgirls, 'vlanguages':vlanguages, 'vcategories':vcategories, 'vchannels':vchannels, 'vseries':vseries}
    #return render(request, 'cawas/pruebas/subir_img.html', context)

    #Serie - OK
    #SerieMetadata -OK
    #Publishqueue - OK
    #Imagequeue - OK

    return render(request, 'cawas/series/add.html', context)
#Fin ADD SERIE


def edit_series_view(request, asset_id):
    # AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)

    # VARIABLES LOCALES
    message = ''
    if request.method == 'POST':
        # VARIABLES
        vserie = Serie()
        vimg = Image()
        vasset = Asset()
        # Parsear JSON
        try:
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)
            vasset = Asset.objects.get(asset_id=asset_id)
            vserie = Serie.objects.get(asset=vasset)
            vimg = Image.objects.get(name=vasset.asset_id)
            pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
        except Setting.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Setting. (" + e.message + ")"})
        except Asset.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Asset. (" + e.message + ")"})
        except Serie.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Serie. (" + e.message + ")"})
        except Image.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Imagen Asociada a la Serie. (" + e.message + ")"})

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
        # FIN IMAGEN

        # Datos de Serie
        vserie.asset = vasset
        vserie.original_title = decjson['Serie']['original_title']
        vserie.year = decjson['Serie']['year']
        vserie.cast = decjson['Serie']['cast']
        vserie.directors = decjson['Serie']['directors']
        vserie.image = vimg
        vserie.save()

        # CARGAR GIRLS
        vgirls = decjson['Serie']['girls']
        for item in vgirls:
            try:
                g = Girl.objects.get(pk=item['girl_id'])
                vserie.girls.add(g)
            except Girl.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Girl. (" + e.message + ")"})

        # CARGAR CATEGORIES
        vcategories = decjson['Serie']['categories']
        for item in vcategories:
            try:
                vserie.category.add(Category.objects.get(pk=item['category_id']))
            except Category.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Category. (" + e.message + ")"})

        # Channel
        try:
            vserie.channel = Channel.objects.get(pk=decjson['Serie']['channel_id'])
        except Channel.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Channel. (" + e.message + ")"})

        vserie.save()
        message = 'Categoria - Registrado Correctamente'
        # Fin datos serie

        # BORRAR Y CREAR METADATA

        vseriemetadatas = decjson['Serie']['Seriemetadatas']
        SerieMetadata.objects.filter(serie=vserie).delete()
        for item in vseriemetadatas:
            try:
                vlanguage = Language.objects.get(code=item['Seriemetadata']['language'])
                smd = SerieMetadata.objects.get(serie=vserie, language=vlanguage)
            except SerieMetadata.DoesNotExist as e:
                smd = SerieMetadata()
            except Language.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe LANGUAGE. (" + e.message + ")"})

            vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
            smd.language = vlanguage
            smd.title = item['Seriemetadata']['title']
            smd.summary_short = item['Seriemetadata']['summary_short']
            smd.summary_long = item['Seriemetadata']['summary_long']
            smd.serie = vserie
            smd.publish_date = vschedule_date
            smd.save()

            # Publica en PublishQueue
            func_publish_queue(vasset.asset_id, smd.language, 'AS', 'Q', vschedule_date)

            # Publica en PublishImage
            func_publish_image(vimg)
            context = {"flag": "success"}
            return render(request, 'cawas/series/edit.html', context)
            # Fin de POST

    # VARIABLES PARA GET - CARGAR GIRL
    try:
        message = ''
        vlanguages = Language.objects.all()
        vgirls = Girl.objects.all()
        vcategories = Category.objects.all()
        vchannels = Channel.objects.all()
        vseries = Serie.objects.all()
        vasset = Asset.objects.get(asset_id=asset_id)
        vserie = Serie.objects.get(asset=vasset)

        # carga imagenes
        i = len(vserie.image.portrait.name)
        imgport = vserie.image.portrait.name[5:i]
        i = len(vserie.image.landscape.name)
        imgland = vserie.image.landscape.name[5:i]

        vgirlselected = vserie.girls.all()
        vgirlnotselected = Girl.objects.exclude(id__in=vgirlselected)

        vcategoryselected = vserie.category.all()
        vcategorynotselected = Category.objects.exclude(id__in=vcategoryselected)

        # Nuevo diccionario para completar lenguages y metadata
        vlangmetadata = []
        for itemlang in vlanguages:
            vseriemetadata = None
            try:
                vseriemetadata = SerieMetadata.objects.get(serie=vserie, language=itemlang)
                vlangmetadata.append(
                    {'checked': True,
                     'code': itemlang.code,
                     'name': itemlang.name,
                     'title': vseriemetadata.title,
                     'summary_short': vseriemetadata.summary_short,
                     'summary_long': vseriemetadata.summary_long,
                     })
            except SerieMetadata.DoesNotExist as a:
                vlangmetadata.append({'checked': False,
                                      'code': itemlang.code,
                                      'name': itemlang.name,
                                      'title': '',
                                      'summary_short': '',
                                      'summary_long':''})


    except Asset.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Asset No Existe . (" + e.message + ")"})
    except Serie.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Serie No Existe . (" + e.message + ")"})
    except Girl.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Girl No Existe . (" + e.message + ")"})
    except Category.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Categoria no Existe. (" + e.message + ")"})
    except Channel.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Canal no Existe. (" + e.message + ")"})
    except GirlMetadata.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "GirlMetaData No Existe . (" + e.message + ")"})

    context = {'message': message, 'vgirls': vgirls,
               'vlanguages': vlanguages,
               'vcategories': vcategories,
               'vchannels': vchannels,
               'vseries': vseries,
               'vlangmetadata':vlangmetadata,
               'vserie':vserie,
               'imgport':imgport, 'imgland':imgland,
               'vgirlnotselected':vgirlnotselected,
               'vgirlselected':vgirlselected,
               'vcategoryselected':vcategoryselected,
               'vcategorynotselected':vcategorynotselected
               }
    # return render(request, 'cawas/pruebas/subir_img.html', context)

    # Serie - OK
    # SerieMetadata -
    # Publishqueue -
    # Imagequeue -

    return render(request, 'cawas/series/edit.html', context)

#</EDIT SERIE>














#<CRUD CATEGORIES>
def add_category_view(request):
    # AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)

    # VARIABLES LOCALES
    message = ''
    vg_pathfiles = 'cawas/static/files/categories/'

    if request.method == 'POST':
        #VARIABLES
        vcategory = Category()
        vimg = Image()

        # Parsear JSON
        strjson = request.POST['strjson']
        decjson = json.loads(strjson)

        # TRATAMIENTO DE IMAGEN: nombre de imagen = a Asset_id
        if not (request.FILES['imagehor'] is None):
            vimg.portrait = request.FILES['imagehor']
            vimg.name = request.FILES['imagehor'].name
            varchivo = vg_pathfiles + vimg.name + '.jpg'
            vimg.portrait.name = varchivo
            if os.path.isfile(varchivo):
                os.remove(varchivo)
            try:
                if not (Image.objects.filter(name=vimg.name).exists()): #si no esta en la base de datos, se crea IMAGE
                    #borra fisicamente imagen si existe
                    vimg.save()
                    vcategory.image = vimg
                else:
                    vcategory.image = Image.objects.get(name=vimg.name)  #se mantiene la imagen actual
            except IntegrityError  as e:
                message = "IMAGE - Ya existe una imagen con el mismo nombre. (" + e.message + ")"
                return render(request, 'cawas/error.html', {"message": message})

        # Datos de Category
        vcategory.original_name = decjson['Category']['original_name']
        vcategory.order = int(decjson['Category']['orden'])
        vcategory.save()
        message = 'Categoria - Registrado Correctamente'

        # BORRAR Y CREAR METADATA
        vcategorymetadatas = decjson['Category']['Categorymetadatas']
        for item in vcategorymetadatas:
            cmd = CategoryMetadata()
            try:
                vlanguage = Language.objects.get(code=item['Categorymetadata']['language'])
            except Language.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe LANGUAGE. (" + e.message + ")"})
            cmd.name = item['Categorymetadata']['name']
            cmd.category = vcategory
            cmd.language = vlanguage
            cmd.save()

    context = {'message': message}
    return render(request, 'cawas/pruebas/subir_img.html', context)


def edit_category_view(request):
    # AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)

    # VARIABLES LOCALES
    message = ''
    vg_pathfiles = 'cawas/static/files/categories/'

    if request.method == 'POST':
        # VARIABLES
        vcategory = Category()
        vimg = Image()

        # Parsear JSON
        strjson = request.POST['strjson']
        decjson = json.loads(strjson)

        # Leer CATEGORY desde category_id
        try:
            vcategory = Category.objects.get(category_id=decjson['Category']['category_id'])
        except Category.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Categoria. (" + e.message + ")"})

        # TRATAMIENTO DE IMAGEN: nombre de imagen = a Asset_id
        if not (request.FILES['imagehor'] is None):
            vimg.portrait = request.FILES['imagehor']
            vimg.name = request.FILES['imagehor'].name
            varchivo = vg_pathfiles + vimg.name + '.jpg'
            try:
                if not (Image.objects.filter(name=vimg.name).exists()):
                    #borra fisicamente imagen si existe
                    if os.path.isfile(varchivo):
                        os.remove(varchivo)
                    vimg.save()
                    vcategory.image = vimg
            except IntegrityError  as e:
                message = "IMAGE - Ya existe una imagen con el mismo nombre. (" + e.message + ")"
                return render(request, 'cawas/error.html', {"message": message})

        # Datos de Category
        vcategory.original_name = decjson['Category']['original_name']
        vcategory.order = int(decjson['Category']['orden'])
        vcategory.save()
        message = 'Categoria - Registrado Correctamente'

        # BORRAR Y CREAR METADATA
        vcategorymetadatas = decjson['Category']['Categorymetadatas']
        cmds = CategoryMetadata.objects.filter(category=vcategory)
        cmds.delete()
        for item in vcategorymetadatas:
            cmd = CategoryMetadata()
            try:
                vlanguage = Language.objects.get(code=item['Categorymetadata']['language'])
            except Language.DoesNotExist as e:
                message = "No existe LANGUAGE. (" + e.message + ")"
                return render(request, 'cawas/error.html', {"message": message})
            cmd.name = item['Categorymetadata']['name']
            cmd.category = vcategory
            cmd.language = vlanguage
            cmd.save()

        context = {"flag": "success"}
        return render(request, 'cawas/categories/edit.html', context)

    context = {'message': message}
    return render(request, 'cawas/pruebas/subir_img.html', context)

#</CRUD CATEGORIES>




def add_blocks_view(request):
    # AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)

    #VARIABLES LOCALES
    message = ''
    vflag = ''
    vschedule_date = ''
    if request.method == 'POST':
        # VARIABLES
        vblock = Block()
        # Parsear JSON
        try:
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)
            #pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            #pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            vblock.name = decjson['Block']['name']
            vschedule_date = datetime.datetime.strptime(decjson['Block']['publish_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
            vblock.publish_date = vschedule_date
            vblock.language = Language.objects.get(code=decjson['Block']['language'])
            vblock.channel = Channel.objects.get(pk=decjson['Block']['channel_id'])

            print "Device:" + str(decjson['Block']['target_device_id'])
            vblock.target_device = Device.objects.get(pk=int(decjson['Block']['target_device_id']))
            vblock.save()
            #vblock.target_device = Device.objects.get(pk=decjson['Block']['target_device_id'])

        except Setting.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Setting. (" + e.message + ")"})
        except Serie.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Serie. (" + e.message + ")"})
        except Image.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Imagen Asociada a la Serie. (" + e.message + ")"})
        except Language.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe LENGUAJE. (" + e.message + ")"})
        except Channel.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Channel. (" + e.message + ")"})
        except Device.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Device. (" + e.message + ")"})



        # CARGAR ASSETS
        vassets = decjson['Block']['assets']
        for item in vassets:
            try:
                asset_id = item['asset_id']
                print "asset_id" +asset_id
                vasset = Asset.objects.get(asset_id=asset_id)

                vblock.assets.add(vasset)
                # Publica en PublishQueue
                func_publish_queue(asset_id, vblock.language, 'AS', 'Q', vblock.publish_date)
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. "+ asset_id + "  (" + e.message + ")" })

        vblock.save()
        func_publish_queue(vblock.block_id, vblock.language, 'BL', 'Q', vblock.publish_date)
        context = {"flag": "success"}
        return render(request, 'cawas/blocks/add.html', context)
        # Fin datos Bloque

    #Variables Para GET
    vblocks = Block.objects.all()
    vchannels = Channel.objects.all()
    vdevices  = Device.objects.all()
    vgirls = Girl.objects.all()
    vlanguages = Language.objects.all()
    vmovies = Movie.objects.all()
    vcapitulos = Episode.objects.all()
    vseries = Serie.objects.all()

    context = {'message': message, 'vblocks':vblocks, 'vchannels':vchannels,'vdevices':vdevices, 'vgirls':vgirls,
               'vlanguages':vlanguages, 'vseries':vseries,
               'vmovies':vmovies, 'vcapitulos':vcapitulos }
    return render(request, 'cawas/blocks/add.html', context)
#</FIN ADD BLOCK>




def edit_blocks_view(request, block_id):
    # AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)
    vblock = Block()
    # VARIABLES LOCALES
    message = ''
    vflag = ''
    vschedule_date = ''
    if request.method == 'POST':

        # Parsear JSON
        try:
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)
            vblock = Block.objects.get(block_id=decjson['Block']['block_id'])
            vblock.name = decjson['Block']['name']
            vschedule_date = datetime.datetime.strptime(decjson['Block']['publish_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
            vblock.publish_date = vschedule_date
            vblock.language = Language.objects.get(code=decjson['Block']['language'])
            vblock.channel = Channel.objects.get(pk=decjson['Block']['channel_id'])
            print "Device:" + str(decjson['Block']['target_device_id'])
            vdevice = Device.objects.get(pk=int(decjson['Block']['target_device_id']))

            vblock.target_device_id = int(decjson['Block']['target_device_id'])
            vblock.save()
        except Setting.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Setting. (" + e.message + ")"})
        except Serie.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Serie. (" + e.message + ")"})
        except Image.DoesNotExist as e:
            return render(request, 'cawas/error.html',
                          {"message": "No Existe Imagen Asociada a la Serie. (" + e.message + ")"})
        except Language.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe LENGUAJE. (" + e.message + ")"})
        except Channel.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Channel. (" + e.message + ")"})
        except Device.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Device. (" + e.message + ")"})
        except Block.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Bloque1. (" + e.message + ")"})



        # CARGAR NUEVOS ASSETS SELECCIONADOS
        assetall = []

        vassets = decjson['Block']['assets']
        for itemactual in vassets:
            if itemactual['asset_id'] not in assetall:
                assetall.append(itemactual['asset_id'])

        for itemactual in vblock.assets.all():
            if itemactual.asset_id not in assetall:
                assetall.append(itemactual.asset_id)

        #Bloque en Cawas
        vblock.assets.clear()
        for item in vassets:
            try:
                 asset_id = item['asset_id']
                 vasset = Asset.objects.get(asset_id=asset_id)
                 vblock.assets.add(vasset)
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})
        vblock.save()

        #Publicacion
        for item in assetall:
            try:
                #asset_id = item['asset_id']
                #vasset = Asset.objects.get(asset_id=item)
                #vblock.assets.add(vasset)
                func_publish_queue(item, vblock.language, 'AS', 'Q', vblock.publish_date)
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})



        # Publica en PublishQueue

        func_publish_queue(vblock.block_id, vblock.language, 'BL', 'Q', vblock.publish_date)
        context = {"flag": "success"}
        return render(request, 'cawas/blocks/edit.html', context)
        # Fin datos Bloque


    try:
        print "block_id" + block_id
        vblock = Block.objects.get(block_id=block_id)
        vassetselect = vblock.assets.all()
        #
        vmovienotselect = Movie.objects.exclude(asset__in=vassetselect)
        vserienotselect = Serie.objects.exclude(asset__in=vassetselect)
        vgirlnotselect = Girl.objects.exclude(asset__in=vassetselect)
        vepisodenotselect = Episode.objects.exclude(asset__in=vassetselect)

        vmovieselect = Movie.objects.filter(asset__in=vassetselect)
        vserieselect = Serie.objects.filter(asset__in=vassetselect)
        vgirlselect = Girl.objects.filter(asset__in=vassetselect)
        vepisodeselect = Episode.objects.filter(asset__in=vassetselect)

    except Block.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "No existe Bloque2. (" + e.message + ")"})

    # Variables Para GET

    vchannels = Channel.objects.all()
    vseries = Serie.objects.all()
    vgirls = Girl.objects.all()
    vlanguages = Language.objects.all()




    context = {'message': message, 'vchannels': vchannels,
               'vgirls': vgirls, 'vlanguages': vlanguages,
               'vseries': vseries, 'vblock':vblock,
               'vmovienotselect':vmovienotselect, 'vgirlnotselect':vgirlnotselect,
               'vepisodenotselect':vepisodenotselect,'vmovieselect':vmovieselect,
               'vgirlselect':vgirlselect, 'vepisodeselect':vepisodeselect,
               'vserienotselect':vserienotselect, 'vserieselect':vserieselect
               }
    return render(request, 'cawas/blocks/edit.html', context)
#<Fin EDIT BLOCKS>



def add_episodes_view(request):
    # AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)

    # VARIABLES LOCALES
    message = ''
    vflag = ''
    vschedule_date = ''
    if request.method == 'POST':
        # VARIABLES
        vepisode = Episode()

        try:
            pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')

            #Parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)
            # DATOS OBLIGATORIOS
            vasset = Asset.objects.get(asset_id=decjson['Episode']['asset_id'])
            vasset.asset_type = "episode"
            vasset.save()
            vepisode.asset = vasset
            vepisode.original_title = decjson['Episode']['original_title']
            vepisode.channel = Channel.objects.get(pk=decjson['Episode']['channel_id'])
            vepisode.display_runtime = decjson['Episode']['display_runtime']
            vasset_serie = Asset.objects.get(asset_id=decjson['Episode']['serie_id'])
            vepisode.serie = Serie.objects.get(asset=vasset_serie)
            vepisode.chapter = decjson['Episode']['chapter']
            vepisode.season = decjson['Episode']['season']

            #Datos OPCIONALES
            if (decjson['Episode']['year'] is not None):
                vepisode.year = decjson['Episode']['year']

            if (decjson['Episode']['cast'] is not None):
                vepisode.cast = decjson['Episode']['cast']

            if (decjson['Episode']['directors'] is not None):
                vepisode.directors = decjson['Episode']['directors']

            try:
                vimg = Image.objects.get(name=vasset.asset_id)
            except Image.DoesNotExist as e:
                vimg = Image()
                vimg.name = vasset.asset_id

            # IMAGEN Portrait
            if (request.FILES.has_key('ThumbHor')):
                if request.FILES['ThumbHor'].name != '':
                    vimg.portrait = request.FILES['ThumbHor']
                    extension = os.path.splitext(vimg.portrait.name)[1]
                    varchivo = pathfilesport.value +  vimg.name + extension
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
            vepisode.image = vimg
            vepisode.save()
        except Asset.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Asset. (" + e.message + ")"})
        except Setting.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Setting. (" + e.message + ")"})
        except Serie.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Serie. (" + e.message + ")"})
        except Image.DoesNotExist as e:
            return render(request, 'cawas/error.html',
                          {"message": "No Existe Imagen Asociada a la Serie. (" + e.message + ")"})
        except Language.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe LENGUAJE. (" + e.message + ")"})
        except Channel.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Channel. (" + e.message + ")"})
        except Device.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Device. (" + e.message + ")"})


        # CARGAR ASSETS
        vgirls = decjson['Episode']['girls']
        for item in vgirls:
            try:
                # print item['asset_id']
                asset_id = item['girl_id']
                print "AssetId add episode"+ asset_id
                vgirl = Girl.objects.get(asset_id=item['girl_id'])
                vepisode.girls.add(vgirl)
            except Girl.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Girl. (" + e.message + ")"})
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})

        # CARGAR CATEGORY
        vcategories = decjson['Episode']['categories']
        for item in vcategories:
            try:
                category_id = item['category_id']
                print "category_id add episode" + category_id
                vcategory = Category.objects.get(pk=category_id)
                vepisode.category.add(vcategory)
            except Category.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Categoria. (" + e.message + ")"})
        vepisode.save()


        vepisodemetadata = decjson['Episode']['Episodemetadatas']
        for item in vepisodemetadata:
            try:
                emd = EpisodeMetadata()
                #convertDateYMDnowIsNull
                if (item['Episodemetadata']['schedule_date'] !=''):
                    vschedule_date = datetime.datetime.strptime(item['Episodemetadata']['schedule_date'],'%d-%m-%Y').strftime('%Y-%m-%d')
                else:
                    vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')

                vlang = Language.objects.get(code=item['Episodemetadata']['language'])
                emd.language = vlang
                emd.title = item['Episodemetadata']['title']
                emd.summary_short = item['Episodemetadata']['summary_short']
                emd.summary_long = item['Episodemetadata']['summary_long']
                emd.publish_date = vschedule_date
                emd.episode = vepisode
                emd.save()
                # Publica en PublishQueue
                func_publish_queue(vasset, vlang, 'AS', 'Q', vschedule_date)
                # Publica en PublishImage
                func_publish_image(vimg)

            except Language.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "Lenguaje no Existe. (" + e.message + ")"})
            except Exception as e:
                return render(request, 'cawas/error.html',{"message": "Error al Guardar Episode Metadata. (" + str(e.message) + ")"})

        vflag = "success"
        context = {"flag":vflag}
        return render(request, 'cawas/episodes/add.html', context)
        # Fin datos EPISODE

    # Variables Para GET
    vseries = Serie.objects.all()
    vchannels = Channel.objects.all()
    vcategories = Category.objects.all()
    vgirls = Girl.objects.all()
    vlanguages = Language.objects.all()
    vmovies = Movie.objects.all()
    vcapitulos = Episode.objects.all()
    vassets = Asset.objects.filter(asset_type="unknown")

    context = {'message': message, 'vcategories': vcategories, 'vchannels': vchannels, 'vgirls': vgirls,
               'vlanguages': vlanguages, 'vseries':vseries, 'vmovies': vmovies, 'vcapitulos': vcapitulos,
               'vassets':vassets}

    #Episode > OK
    #Asset > OK
    #Imagenes > OK
    #Metadata Falta
    #categorias OK
    #girls OK
    return render(request, 'cawas/episodes/add.html', context)




def edit_episodes_view(request, episode_id):
    # AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)

    # VARIABLES LOCALES
    message = ''
    vflag = ''
    vschedule_date = ''
    vasset = Asset()
    vepisode = Episode()

    try:
        vasset = Asset.objects.get(asset_id=episode_id)
        print "episode: " +episode_id
        vepisode = Episode.objects.get(asset=vasset)
        i = len(vepisode.image.portrait.name)
        imgport = vepisode.image.portrait.name[5:i]
        i = len(vepisode.image.landscape.name)
        imgland = vepisode.image.landscape.name[5:i]
        print "episodio " + vepisode.original_title

    except Asset.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "No Existe Asset1. (" + e.message + ")"})
    except Setting.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "No Existe Episode. (" + e.message + ")"})


    if request.method == 'POST':
        # VARIABLES


        try:
            pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')

            # Parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)
            # DATOS OBLIGATORIOS
            vepisode.original_title = decjson['Episode']['original_title']
            vepisode.channel = Channel.objects.get(pk=decjson['Episode']['channel_id'])
            vepisode.display_runtime = decjson['Episode']['display_runtime']
            print "Serie_id" + decjson['Episode']['serie_id']
            vasset_serie = Asset.objects.get(asset_id=decjson['Episode']['serie_id'])
            vepisode.serie = Serie.objects.get(asset=vasset_serie)
            vepisode.chapter = decjson['Episode']['chapter']
            vepisode.season = decjson['Episode']['season']

            # Datos OPCIONALES
            if (decjson['Episode']['year'] is not None):
                vepisode.year = decjson['Episode']['year']

            if (decjson['Episode']['cast'] is not None):
                vepisode.cast = decjson['Episode']['cast']

            if (decjson['Episode']['directors'] is not None):
                vepisode.directors = decjson['Episode']['directors']

            try:
                vimg = Image.objects.get(name=vasset.asset_id)
            except Image.DoesNotExist as e:
                vimg = Image()
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
            vepisode.image = vimg
            vepisode.save()
        except Asset.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Asset 3. (" + e.message + ")"})
        except Setting.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Setting. (" + e.message + ")"})
        except Serie.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No Existe Serie. (" + e.message + ")"})
        except Image.DoesNotExist as e:
            return render(request, 'cawas/error.html',
                          {"message": "No Existe Imagen Asociada a la Serie. (" + e.message + ")"})
        except Language.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe LENGUAJE. (" + e.message + ")"})
        except Channel.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Channel. (" + e.message + ")"})
        except Device.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Device. (" + e.message + ")"})
        except Episode.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Episode. (" + e.message + ")"})

        # CARGAR ASSETS
        vgirls = decjson['Episode']['girls']
        for item in vgirls:
            try:
                # print item['asset_id']
                asset_id = item['girl_id']
                print "AssetId add episode" + asset_id
                vgirl = Girl.objects.get(asset_id=item['girl_id'])
                vepisode.girls.add(vgirl)
            except Girl.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Girl. (" + e.message + ")"})
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset2. (" + e.message + ")"})

        # CARGAR CATEGORY
        vcategories = decjson['Episode']['categories']
        for item in vcategories:
            try:
                category_id = item['category_id']
                print "category_id add episode" + category_id
                vcategory = Category.objects.get(pk=category_id)
                vepisode.category.add(vcategory)
            except Category.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Categoria. (" + e.message + ")"})
        vepisode.save()

        EpisodeMetadata.objects.filter(episode=vepisode).delete()
        vepisodemetadata = decjson['Episode']['Episodemetadatas']
        for item in vepisodemetadata:
            try:

                vlang = Language.objects.get(code=item['Episodemetadata']['language'])
                try:
                    emd = EpisodeMetadata.objects.get(episode=vepisode, language=vlang)
                except EpisodeMetadata.DoesNotExist as e:
                    emd = EpisodeMetadata();

                # convertDateYMDnowIsNull
                if (item['Episodemetadata']['schedule_date'] != ''):
                    vschedule_date = datetime.datetime.strptime(item['Episodemetadata']['schedule_date'],
                                                                '%d-%m-%Y').strftime('%Y-%m-%d')
                else:
                    vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                emd.language = vlang
                emd.title = item['Episodemetadata']['title']
                emd.summary_short = item['Episodemetadata']['summary_short']
                emd.summary_long = item['Episodemetadata']['summary_long']
                emd.publish_date = vschedule_date
                emd.episode = vepisode
                emd.save()
                # Publica en PublishQueue
                func_publish_queue(vasset, vlang, 'AS', 'Q', vschedule_date)
                # Publica en PublishImage
                func_publish_image(vimg)

            except Language.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "Lenguaje no Existe. (" + e.message + ")"})
            except Exception as e:
                return render(request, 'cawas/error.html',
                              {"message": "Error al Guardar Episode Metadata. (" + str(e.message) + ")"})

        context = {"flag":"success"}
        return render(request, 'cawas/episodes/edit.html', context)
        #return redirect(menu_view)
        # Fin POST Bloque

    try:
        vchannels = Channel.objects.all()
        vcategories = Category.objects.all()
        vgirls = Girl.objects.all()
        vlanguages = Language.objects.all()
        vmovies = Movie.objects.all()
        vcapitulos = Episode.objects.all()
        vassets = Asset.objects.filter(asset_type="unknown")


        vgirlselected = vepisode.girls.all()
        vgirlnotselected = Girl.objects.exclude(id__in=vgirlselected)
        vcategoryselected = vepisode.category.all()
        vcategorynotselected = Category.objects.exclude(id__in=vcategoryselected)
        vseries = Serie.objects.all()

        # nuevo diccionario para completar lenguages y metadata
        vlangmetadata = []
        for itemlang in vlanguages:
            try:
                vepisodemetadata = EpisodeMetadata.objects.get(episode=vepisode, language=itemlang)
                vlangmetadata.append({
                    'checked': True, 'code': itemlang.code, 'name': itemlang.name,
                    'title': vepisodemetadata.title, 'summary_short': vepisodemetadata.summary_short,
                    'summary_long': vepisodemetadata.summary_long, 'publish_date': vepisodemetadata.publish_date
                    })
            except EpisodeMetadata.DoesNotExist as a:
                vlangmetadata.append({'checked': False, 'code': itemlang.code,'name': itemlang.name, 'titulo':'', 'descripcion':'','fechapub': ''})

    except Girl.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "No existe Chica. (" + e.message + ")"})
    except Category.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "No existe Categoria. (" + e.message + ")"})


    context = {'message': message,'vgirlnotselected':vgirlnotselected,
               'vgirlselected':vgirlselected,
               'imgland': imgland, 'imgport': imgport, 'vepisode': vepisode,
               'vcategorynotselected':vcategorynotselected, 'vcategoryselected':vcategoryselected,
               'vchannels':vchannels,'vlangmetadata':vlangmetadata, 'vseries':vseries
               }

    # Episode >
    # Asset >
    # Imagenes >
    # Metadata >
    # categorias >
    # girls >
    return render(request, 'cawas/episodes/edit.html', context)




def add_sliders_view(request):
    if not request.user.is_authenticated:
        return redirect(login_view)

        # VARIABLES LOCALES
    message = ''
    vflag = ""
    vschedule_date = ''
    vasset = Asset()
    vslider = Slider()

    if request.method == 'POST':
        # VARIABLES
        try:
            # Parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)
            print "DEBUG: "+ decjson['Slider']['media_type']

            vasset = Asset.objects.get(asset_id=decjson['Slider']['asset_id'] )
            print "ASSET_ID: " + decjson['Slider']['asset_id']
            vslider.asset = vasset
            vslider.media_url = decjson['Slider']['media_url']
            vslider.media_type = decjson['Slider']['media_type']

            print "ASSET_ID: "+decjson['Slider']['media_type']

            vdevice = Device.objects.get(id=decjson['Slider']['target_device_id'])
            vslider.target_device = vdevice
            vslider.media_type = decjson['Slider']['target_device_id']
            vslider.save()
        except Device.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Device. (" + e.message + ")"})
        except Asset.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})

        print "METADATA"
        #METADATA
        vslidermetadata = decjson['Slider']['Slidermetadatas']
        print decjson['Slider']['Slidermetadatas']
        vflag = "success"

        #SliderMetadata.objects.filter(slider=vslider).delete()
        for item in vslidermetadata:
            try:
                smd = SliderMetadata()
                print "DEBUG1: " + item['Slidermetadata']['schedule_date']
                if (item['Slidermetadata']['schedule_date'] != ''):
                    vschedule_date = datetime.datetime.strptime(item['Slidermetadata']['schedule_date'],'%d-%m-%Y').strftime('%Y-%m-%d')
                else:
                    vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
                vlang = Language.objects.get(code=item['Slidermetadata']['language'])
                smd.language = vlang
                smd.text = item['Slidermetadata']['text']
                print "DEBUG1" +  item['Slidermetadata']['text']
                smd.slider = vslider
                smd.publish_date = vschedule_date
                smd.save()

                # Publica en PublishQueue
                print "DEBUG:" + vschedule_date
                func_publish_queue(vasset, vlang, 'AS', 'Q', vschedule_date)
                vflag = "success"
            except Language.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "Lenguaje no Existe. (" + str(e.message) + ")"})
            except Exception as e:
                return render(request, 'cawas/error.html',{"message": "Error al Guardar Metadata. (" + str(e.message) + ")"})
            vflag = "success"


    vassets = Asset.objects.all()
    vsliders = Slider.objects.all()
    vlanguages = Language.objects.all()
    vdevices = Device.objects.all()
    vtypes  = {"image": "Image", "video": "Video"}
    message =''
    context = {'message': message, 'vtypes':vtypes,'vassets':vassets, 'vsliders':vsliders,
               'vlanguages':vlanguages, 'vdevices':vdevices, 'flag':vflag}
    return render(request, 'cawas/sliders/add.html', context)


def edit_sliders_view(request, slider_id):
    if not request.user.is_authenticated:
        return redirect(login_view)

        # VARIABLES LOCALES
    vflag = ""
    vschedule_date = ''
    vasset = Asset()
    vslider = Slider()

    try:
        vslider = Slider.objects.get(slider_id=slider_id)

        vassets = Asset.objects.all()
        vsliders = Slider.objects.all()
        vlanguages = Language.objects.all()
        vdevices = Device.objects.all()
        vtypes = {"image": "Image", "video": "Video"}

        # nuevo diccionario para completar lenguages y metadata
        vlangmetadata = []
        for itemlang in vlanguages:
            try:
                vslidermetadata = SliderMetadata.objects.get(slider=vslider, language=itemlang)
                vlangmetadata.append({
                    'checked': True, 'code': itemlang.code, 'name': itemlang.name,
                    'text': vslidermetadata.text, 'publish_date': vslidermetadata.publish_date
                })
            except SliderMetadata.DoesNotExist as a:
                vlangmetadata.append(
                    {'checked': False, 'code': itemlang.code, 'name': itemlang.name, 'text': '', 'text': '','publish_date': ''})

    except Slider.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "No Existe Slider. (" + str(e.message) + ")"})


    if request.method == 'POST':
        # VARIABLES
        try:
            # Parsear JSON
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)
            print "DEBUG: "+ decjson['Slider']['asset_id']

            vasset = Asset.objects.get(asset_id=decjson['Slider']['asset_id'] )
            print "ASSET_ID: " + decjson['Slider']['asset_id']
            vslider.asset = vasset
            vslider.media_url = decjson['Slider']['media_url']
            vslider.media_type = decjson['Slider']['media_type']

            print "ASSET_ID: "+decjson['Slider']['media_type']

            vdevice = Device.objects.get(id=decjson['Slider']['target_device_id'])
            vslider.target_device = vdevice
            vslider.media_type = decjson['Slider']['target_device_id']
            vslider.save()
        except Device.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Device. (" + e.message + ")"})
        except Asset.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})


        #METADATA
        vslidermetadata = decjson['Slider']['Slidermetadatas']
        print decjson['Slider']['Slidermetadatas']
        vflag = "success"

        #SliderMetadata.objects.filter(slider=vslider).delete()
        for item in vslidermetadata:
            try:
                smd = SliderMetadata()
                print "DEBUG1: " + item['Slidermetadata']['schedule_date']
                if (item['Slidermetadata']['schedule_date'] != ''):
                    vschedule_date = datetime.datetime.strptime(item['Slidermetadata']['schedule_date'],'%d-%m-%Y').strftime('%Y-%m-%d')
                else:
                    vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')

                vlang = Language.objects.get(code=item['Slidermetadata']['language'])
                smd.language = vlang
                smd.text = item['Slidermetadata']['text']
                print "DEBUG12" +  item['Slidermetadata']['text']
                print "DEBUG12" + vschedule_date
                smd.slider = vslider
                smd.publish_date = vschedule_date
                smd.save()

                # Publica en PublishQueue
                func_publish_queue(vasset, vlang, 'AS', 'Q', vschedule_date)
                vflag = "success"
            except Language.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "Lenguaje no Existe. (" + str(e.message) + ")"})
            except Exception as e:
                return render(request, 'cawas/error.html',{"message": "Error al Guardar Metadata. (" + str(e.message) + ")"})
            vflag = "success"


    context = {'vtypes':vtypes,'vassets':vassets, 'vsliders':vsliders,
               'vlanguages':vlanguages, 'vdevices':vdevices, 'flag':vflag,'vslider':vslider,
               'vlangmetadata':vlangmetadata}
    return render(request, 'cawas/sliders/edit.html', context)



def add_asset_view(request):
    try:
        strjson = request.body
        decjson = json.loads(strjson)
        if Asset.objects.filter(asset_id=decjson['asset_id']).exists():
            return HttpResponse('Conflict', status=409)
        else:
            vasset = Asset()
            vasset.asset_id = decjson['asset_id']
            vasset.asset_type = "unknown"
            vasset.save()
            message = "Asset Generado Correctamente"

    except ValueError, e:
        message = "Error al leer archivo JSON. (" + e.message + ")"
        return render(request, 'cawas/error.html', {"message": message})

    context = {'message': message}
    return render(request, 'cawas/pruebas/blank.html', context)




#Funciones de Despublicacion
def unpublish_movies_view(request, id):
    if not request.user.is_authenticated:
        return redirect(login_view)

    try:
        moviemetadata = MovieMetadata.objects.get(id=id)
        backend_asset_url = Setting.objects.get(CODE='backend_asset_url')
        vzones = PublishZone.objects.filter(enabled=True)
        for zone in vzones:
            abr = ApiBackendResource(zone.backend_url ,backend_asset_url )
            param = ({"asset_id": moviemetadata.movie.asset.asset_id,"asset_type":"show", "lang":moviemetadata.language.code  })
            abr.delete(param)

        flag = 'Movie ' + moviemetadata.movie.asset.asset_id + 'Despublicada Correctamente'
    except PublishZone.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "PublishZone no Existe. (" + str(e.message) + ")"})
    except MovieMetadata.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Metadata de Movie no Existe. (" + str(e.message) + ")"})

    context = {'flag':flag}
    return render(request, 'cawas/movies/list.html', context)




def unpublish_girls_view(request, id):
    if not request.user.is_authenticated:
        return redirect(login_view)
    try:
        girlmetadata = GirlMetadata.objects.get(id=id)
        backend_asset_url = Setting.objects.get(CODE='backend_asset_url')
        vzones = PublishZone.objects.filter(enabled=True)
        for zone in vzones:
            abr = ApiBackendResource(zone.backend_url ,backend_asset_url )
            param = ({"asset_id": girlmetadata.girl.asset.asset_id,"asset_type":"show", "lang":girlmetadata.language.code  })
            abr.delete(param)

        flag = 'Girl ' + girlmetadata.girl.asset.asset_id + 'Despublicada Correctamente'
    except PublishZone.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "PublishZone no Existe. (" + str(e.message) + ")"})
    except MovieMetadata.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Metadata de Movie no Existe. (" + str(e.message) + ")"})

    context = {'flag':flag}
    return render(request, 'cawas/girls/list.html', context)


#Funciones de Despublicacion
def unpublish_series_view(request, id):
    if not request.user.is_authenticated:
        return redirect(login_view)

    try:
        seriemetadata = SerieMetadata.objects.get(id=id)
        backend_asset_url = Setting.objects.get(CODE='backend_asset_url')
        vzones = PublishZone.objects.filter(enabled=True)
        for zone in vzones:
            abr = ApiBackendResource(zone.backend_url ,backend_asset_url )
            param = ({"asset_id": seriemetadata.serie.asset.asset_id,"asset_type":"show", "lang":seriemetadata.language.code  })
            abr.delete(param)

        flag = 'Serie ' + seriemetadata.serie.asset.asset_id + ' Despublicada Correctamente'
    except PublishZone.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "PublishZone no Existe. (" + str(e.message) + ")"})
    except SerieMetadata.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Metadata de Serie no Existe. (" + str(e.message) + ")"})

    context = {'flag':flag}
    return render(request, 'cawas/movies/list.html', context)


#Funciones de Despublicacion
def unpublish_blocks_view(request, id):
    if not request.user.is_authenticated:
        return redirect(login_view)
    #recorrer los assets asociados, quitar la relacion del bloque con los asset
    # y volver a publicar los assets
    flag= ''
    '''
    try:
        block = Block.objects.get(id=id)
        backend_asset_url = Setting.objects.get(CODE='backend_asset_url')
        vzones = PublishZone.objects.filter(enabled=True)
        for zone in vzones:
            abr = ApiBackendResource(zone.backend_url ,backend_asset_url )
            param = ({"asset_id": block.block_id,"asset_type":"show", "lang":block.language.code  })
            abr.delete(param)

        flag = 'Bloque ' + block.asset.asset_id + 'Despublicada Correctamente'
    except PublishZone.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "PublishZone no Existe. (" + str(e.message) + ")"})
    except MovieMetadata.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Metadata de Movie no Existe. (" + str(e.message) + ")"})
    '''
    context = {'flag':flag}
    return render(request, 'cawas/blocks/list.html', context)


#Funciones de Despublicacion
def unpublish_episodes_view(request, id):
    if not request.user.is_authenticated:
        return redirect(login_view)

    try:
        episodemetadata = MovieMetadata.objects.get(id=id)
        backend_asset_url = Setting.objects.get(CODE='backend_asset_url')
        vzones = PublishZone.objects.filter(enabled=True)
        for zone in vzones:
            abr = ApiBackendResource(zone.backend_url ,backend_asset_url )
            param = ({"asset_id": episodemetadata.movie.asset.asset_id,"asset_type":"show", "lang":episodemetadata.language.code  })
            abr.delete(param)

        flag = 'Capitulo ' + episodemetadata.episode.asset.asset_id + ' Despublicada Correctamente'
    except PublishZone.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "PublishZone no Existe. (" + str(e.message) + ")"})
    except EpisodeMetadata.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Metadata de Capitulo no Existe. (" + str(e.message) + ")"})

    context = {'flag':flag}
    return render(request, 'cawas/movies/list.html', context)


#Funciones de Despublicacion
def unpublish_sliders_view(request, id):
    if not request.user.is_authenticated:
        return redirect(login_view)

    try:
        slidermetadata = MovieMetadata.objects.get(id=id)
        backend_asset_url = Setting.objects.get(CODE='backend_asset_url')
        vzones = PublishZone.objects.filter(enabled=True)
        for zone in vzones:
            abr = ApiBackendResource(zone.backend_url ,backend_asset_url )
            param = ({"asset_id": slidermetadata.movie.asset.asset_id,"asset_type":"show", "lang":slidermetadata.language.code  })
            abr.delete(param)

        flag = 'Slider ' + slidermetadata.slider.asset.asset_id + ' Despublicada Correctamente'
    except PublishZone.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "PublishZone no Existe. (" + str(e.message) + ")"})
    except MovieMetadata.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "Metadata de Movie no Existe. (" + str(e.message) + ")"})

    context = {'flag':flag}
    return render(request, 'cawas/movies/list.html', context)


# Borrar comentario
def list_movies_view(request):
    if not request.user.is_authenticated:
        return redirect(login_view)

    usuario = request.user
    message = "Error"
    titulo = ''
    page = request.GET.get('page')
    request.POST.get('page')
    movies_list= None

    if request.POST:
        titulo = request.POST['inputTitulo']
        selectestado = request.POST['selectestado']
        #movies_list = MovieMetadata.objects.all().order_by('movie_id')

        if titulo != '':
            movies_sel = Movie.objects.filter(original_title__icontains=titulo)
        else:
            movies_sel = Movie.objects.all()

        if selectestado !='':
            movies_list = MovieMetadata.objects.filter(movie__in=movies_sel, publish_status=selectestado ).order_by('movie_id')
        else:
            movies_list = MovieMetadata.objects.filter(movie__in=movies_sel).order_by('movie_id')


    if movies_list is None:
        movies_list = MovieMetadata.objects.all().order_by('movie_id')

    paginator = Paginator(movies_list, 20)  # Show 25 contacts per page
    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        movies = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        movies = paginator.page(paginator.num_pages)


    context = {'message': message, 'registros':movies, 'titulo':titulo, 'usuario':usuario}

    return render(request, 'cawas/movies/list.html', context)




def list_girls_view(request):
    if not request.user.is_authenticated:
        return redirect(login_view)

    usuario = request.user
    message = "Error"
    titulo = ''
    page = request.GET.get('page')
    request.POST.get('page')
    girls_list = None

    if request.POST:
        titulo = request.POST['inputTitulo']
        selectestado = request.POST['selectestado']

        #FILTROS
        if titulo != '':
            if selectestado != '':
                girls_list = Girl.objects.filter(name__icontains=titulo, publish_status=selectestado).order_by('girl_id')
            else:
                girls_list = Girl.objects.filter(name__icontains=titulo).order_by('girl_id')
        elif selectestado != '':
            girls_list = Girl.objects.filter( publish_status=selectestado).order_by('girl_id')
        else:
            girls_list = Girl.objects.all().order_by('girl_id')



    if girls_list is None:
        girls_list = GirlMetadata.objects.all().order_by('girl_id')


    paginator = Paginator(girls_list, 20)  # Show 25 contacts per page
    try:
        girls = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        girls = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        girls = paginator.page(paginator.num_pages)

    context = {'message': message, 'registros': girls, 'titulo': titulo, 'usuario': usuario}
    return render(request, 'cawas/girls/list.html', context)




def list_blocks_view(request):
    if not request.user.is_authenticated:
        return redirect(login_view)

    usuario = request.user
    message = "Error"
    titulo = ''
    page = request.GET.get('page')
    request.POST.get('page')
    blocks_list = None

    if request.POST:
        titulo = request.POST['inputTitulo']
        selectestado = request.POST['selectestado']

        # FILTROS
        if titulo != '':
            if selectestado != '':
                blocks_list = Block.objects.filter(name__icontains=titulo, publish_status=selectestado).order_by('block_id')
            else:
                blocks_list = Block.objects.filter(name__icontains=titulo).order_by('block_id')
        elif selectestado != '':
            blocks_list = Block.objects.filter(publish_status=selectestado).order_by('block_id')
        else:
            blocks_list = Block.objects.all().order_by('block_id')


    if blocks_list is None:
        blocks_list = Block.objects.all().order_by('block_id')

    paginator = Paginator(blocks_list, 20)  # Show 25 contacts per page
    try:
        blocks = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        blocks = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        blocks = paginator.page(paginator.num_pages)

    context = {'message': message, 'registros': blocks, 'titulo': titulo, 'usuario': usuario}
    return render(request, 'cawas/blocks/list.html', context)




def list_episodes_view(request):
    if not request.user.is_authenticated:
        return redirect(login_view)

    usuario = request.user
    message = "Error"
    titulo = ''
    page = request.GET.get('page')
    request.POST.get('page')
    episodes_list = None

    if request.POST:
        titulo = request.POST['inputTitulo']
        selectestado = request.POST['selectestado']
        # FILTROS
        if titulo != '':
            if selectestado != '':
                episodes_list = EpisodeMetadata.objects.filter(title__icontains=titulo, publish_status=selectestado).order_by('episode_id')
            else:
                episodes_list = EpisodeMetadata.objects.filter(title__icontains=titulo).order_by('episode_id')
        elif selectestado != '':
            episodes_list = EpisodeMetadata.objects.filter(publish_status=selectestado).order_by('episode_id')
        else:
            episodes_list = EpisodeMetadata.objects.all().order_by('episode_id')

    if episodes_list is None:
        episodes_list = EpisodeMetadata.objects.all().order_by('episode_id')

    paginator = Paginator(episodes_list, 20)  # Show 25 contacts per page
    try:
        episodes = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        episodes = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        episodes = paginator.page(paginator.num_pages)

    context = {'message': message, 'registros':episodes, 'titulo':titulo, 'usuario':usuario}
    return render(request, 'cawas/episodes/list.html', context)



def list_series_view(request):
    if not request.user.is_authenticated:
        return redirect(login_view)

    usuario = request.user
    message = "Error"
    titulo = ''
    page = request.GET.get('page')
    request.POST.get('page')
    series_list = None

    if request.POST:
        titulo = request.POST['inputTitulo']
        selectestado = request.POST['selectestado']
        # FILTROS
        if titulo != '':
            if selectestado != '':
                series_list = SerieMetadata.objects.filter(title__icontains=titulo, publish_status=selectestado).order_by('serie_id')
            else:
                series_list = SerieMetadata.objects.filter(title__icontains=titulo).order_by('serie_id')
        elif selectestado != '':
            series_list = SerieMetadata.objects.filter(publish_status=selectestado).order_by('serie_id')
        else:
            series_list = SerieMetadata.objects.all().order_by('serie_id')

    if series_list is None:
        series_list = SerieMetadata.objects.all().order_by('serie_id')

    paginator = Paginator(series_list, 20)  # Show 25 contacts per page
    try:
        series = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        series = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        series = paginator.page(paginator.num_pages)

    context = {'message': message, 'registros':series, 'titulo':titulo, 'usuario':usuario}
    return render(request, 'cawas/series/list.html', context)




def list_sliders_view(request):
    if not request.user.is_authenticated:
        return redirect(login_view)

    usuario = request.user
    message = "Error"
    titulo = ''
    page = request.GET.get('page')
    request.POST.get('page')
    sliders_list = None

    if request.POST:
        titulo = request.POST['inputTitulo']
        selectestado = request.POST['selectestado']
        # FILTROS
        if titulo != '':
            sliders = Slider.objects.filter(media_url__icontains=titulo).order_by('slider_id')
            if selectestado != '':
                sliders_list = SliderMetadata.objects.filter(slider__in=sliders, publish_status=selectestado).order_by('slider_id')
            else:
                sliders_list = SliderMetadata.objects.filter(slider__in=sliders).order_by('slider_id')
        elif selectestado != '':
            sliders_list = SliderMetadata.objects.filter(publish_status=selectestado).order_by('slider_id')
        else:
            sliders_list = SliderMetadata.objects.all().order_by('slider_id')

    if sliders_list is None:
        sliders_list = SliderMetadata.objects.all().order_by('slider_id')

    paginator = Paginator(sliders_list, 20)  # Show 25 contacts per page
    try:
        sliders = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        sliders = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        sliders = paginator.page(paginator.num_pages)

    context = {'message': message, 'registros':sliders, 'titulo':titulo, 'usuario':usuario}
    return render(request, 'cawas/sliders/list.html', context)
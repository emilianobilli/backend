from django.shortcuts import render

# Create your views here.
import datetime, os, json
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import Channel, Asset, Device, Episode, EpisodeMetadata, ImageQueue, PublishQueue, Setting,  Block, Serie, SerieMetadata, Movie, MovieMetadata, Girl,GirlMetadata,  Category,CategoryMetadata, Language, Image, PublishZone
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse
from django.conf import settings
from django.db import IntegrityError

#FUNCIONES GENERALES
#Funcion para publicar Asset
def func_publish_queue(passet, planguage, pitem_type, pstatus,  pschedule_date):
    #fecha pschedule_date: ya tiene que estar parceada como strftime('%Y-%m-%d')

    vzones = PublishZone.objects.filter(enabled=True)
    for zone in vzones:
        # CREAR COLA DE PUBLICACION
        vpublish = PublishQueue()
        vpublish.item_id = passet.asset_id
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
        (5, "CAPITULOS")
    )

    assetstypes = (
        (1, "Movies"),
        (2, "Serie"),
        (3, "Bloques"),
        (4, "Chicas"),
        (5, "Categoria"),
        (6, "Capitulos")
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
    return render(request, 'cawas/movies/index.html', context)







def prueba_json_view(request):
    if not request.user.is_authenticated:
        return redirect(login_view)

    context = {}
    return render(request, 'cawas/pruebas/prueba_json.html', context)




def add_movies_view(request):
   #AUTENTICACION DE USUARIO
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
                   #vpublish.schedule_date = datetime.datetime.strptime(item['Moviemetadata']['schedule_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
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
# Fin add_movies_view



def edit_movies_view(request, asset_id):
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
       mv.year = int(decjson['Movie']['year'])
       mv.cast = decjson['Movie']['cast']
       mv.directors = decjson['Movie']['directors']
       mv.display_runtime = decjson['Movie']['display_runtime']
       #calcular runtime
       #mv.runtime
       mv.save()

       # CARGAR GIRLS
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
           print "mmdLanguaje:" + item['Moviemetadata']['language']
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
                   vpublish.schedule_date = datetime.datetime.strptime(item['Moviemetadata']['schedule_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
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
                vpublishqueue = PublishQueue.objects.filter(item_id=vasset.asset_id, item_lang = itemlang)[:1]
                if PublishQueue.objects.filter(item_id=vasset.asset_id, item_lang = itemlang).exists():
                    vpublishqueue = ''
                else:
                    vpublishqueue = PublishQueue.objects.filter(item_id=vasset.asset_id, item_lang=itemlang)[:1].only('schedule_date')
                vlangmetadata.append(
                    {'checked': True, 'code': itemlang.code, 'name': itemlang.name, 'title': vmoviemetadata.title,
                     'summary_short': vmoviemetadata.summary_short, 'summary_long': vmoviemetadata.summary_long,
                     'publish_date': vpublishqueue})
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
# Fin edit_movies_view

#</CRUD MOVIES>









#<ADD GIRL>
def add_girls_view(request):
    #AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)
    message = ''
    vimg = Image()
    try:
        pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
        pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
    except Setting.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "No Setting. (" + e.message + ")"})

    #POST - Obtener datos del formulario y guardar la metadata
    if request.method == 'POST':
        # parsear JSON
        strjson = request.POST['varsToJSON']
        decjson = json.loads(strjson)

        # VARIABLES
        vgirl = Girl()
        vasset = Asset()
        vasset.asset_type = "girl"
        vasset.save()

        try:
            vimg.name = vasset.asset_id
            #IMAGEN Portrait
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

            #CREAR GIRL
            vgirl.asset = vasset
            vgirl.name  = decjson['Girl']['name']
            vgirl.type = decjson['Girl']['type_girl']
            vgirl.birth_date = datetime.datetime.strptime(decjson['Girl']['birth_date'],'%d-%m-%Y').strftime('%Y-%m-%d')
            vgirl.height = decjson['Girl']['height']
            vgirl.weight = decjson['Girl']['weight']
            vgirl.image = vimg
            vgirl.save()
        except Exception as e:
            return render(request, 'cawas/error.html', {"message": "Error al Guardar Girl. (" + str(e.message) + ")."})


        message ='Girl, generada'
        # Luego del POST redirige a pagina principal
        return redirect(menu_view)

        # CARGAR METADATA

    #Cargar variables para presentar en templates
    vgirls = Girl.objects.all()
    vcategories = Category.objects.all()
    vlanguages = Language.objects.all()

    vtypegirl = {"pornstar":"Pornstar", "playmate":"Playmate"}
    context = {'message':message, 'vgirls':vgirls, 'vcategories':vcategories, 'vlanguages':vlanguages,'vtypegirl':vtypegirl }
    #checks:
    #Imagenes - OK
    #Girl - OK
    #Girl metadata - OK
    #Publishqueue - NO
    #Publishimage - NO
    return render(request, 'cawas/girls/add.html', context)
#</fin ADD Girl>


def edit_girls_view(request, asset_id):
    #AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)

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
            func_publish_queue(vasset, vlanguage, 'AS', 'Q', vschedule_date)
            # Publica en PublishImage
            func_publish_image(vimg)

        #Luego del POST redirige a pagina principal
        return redirect(menu_view)

    context = {'message': message,  'vlanguages': vlanguages, 'vgirl':vgirl, 'vtypegirl':vtypegirl,'vlangmetadata':vlangmetadata,
               'imgport':imgport, 'imgland':imgland}
    # checks:
    # Imagenes -
    # Girl - OK
    # Girl metadata - OK
    # Publishqueue - OK
    # Publishimage - OK
    # Bugs:

    return render(request, 'cawas/girls/edit.html', context)
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
            func_publish_queue(vasset, smd.language, 'AS', 'Q', vschedule_date)

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
            func_publish_queue(vasset, smd.language, 'AS', 'Q', vschedule_date)

            # Publica en PublishImage
            func_publish_image(vimg)
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
                #print item['asset_id']
                asset_id = item['asset_id']
                print asset_id
                vasset = Asset.objects.get(pk=asset_id)
                vblock.save()
                vblock.assets.add(vasset)
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})
        # Publica en PublishQueue
        func_publish_queue(vasset, vblock.language, 'AS', 'Q', vblock.publish_date)
        vblock.save()
        vflag = "success"
        message = 'Bloque - Registrado Correctamente'
        # Fin datos Bloque

    #Variables Para GET
    vblocks = Block.objects.all()
    vchannels = Channel.objects.all()
    vdevices  = Device.objects.all()
    vgirls = Girl.objects.all()
    vlanguages = Language.objects.all()
    vmovies = Movie.objects.all()
    vcapitulos = Episode.objects.all()

    context = {'message': message, 'vblocks':vblocks, 'vchannels':vchannels,'vdevices':vdevices, 'vgirls':vgirls, 'vlanguages':vlanguages,
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
            print str(strjson)
            decjson = json.loads(strjson)
            # pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            # pathfilesland = Setting.objects.get(code='image_repository_path_landscape')

            print "deviceID:" + decjson['Block']['target_device_id']
            vblock = Block.objects.get(block_id=decjson['Block']['block_id'])
            vblock.name = decjson['Block']['name']
            vschedule_date = datetime.datetime.strptime(decjson['Block']['publish_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
            vblock.publish_date = vschedule_date
            vblock.language = Language.objects.get(code=decjson['Block']['language'])
            vblock.channel = Channel.objects.get(pk=decjson['Block']['channel_id'])
            print "Device:" + str(decjson['Block']['target_device_id'])
            vdevice = Device.objects.get(pk=int(decjson['Block']['target_device_id']))

            vblock.target_device_id = int(decjson['Block']['target_device_id'])
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

        # CARGAR ASSETS
        vassets = decjson['Block']['assets']
        for item in vassets:
            try:
                # print item['asset_id']
                asset_id = item['asset_id']
                vasset = Asset.objects.get(pk=asset_id)
                vblock.save()
                vblock.assets.add(vasset)
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})
        # Publica en PublishQueue
        func_publish_queue(vasset, vblock.language, 'AS', 'Q', vblock.publish_date)
        vblock.save()
        vflag = "success"
        message = 'Bloque - Registrado Correctamente'
        # Fin datos Bloque


    try:
        print "block_id" + block_id
        vblock = Block.objects.get(block_id=block_id)
        vassetselect = vblock.assets.all()
        vmovienotselect = Movie.objects.exclude(asset__in=vassetselect)
        vgirlnotselect = Girl.objects.exclude(asset__in=vassetselect)
        vepisodenotselect = Episode.objects.exclude(asset__in=vassetselect)
        vmovieselect = Movie.objects.filter(asset__in=vassetselect)
        vgirlselect = Girl.objects.filter(asset__in=vassetselect)
        vepisodeselect = Episode.objects.filter(asset__in=vassetselect)

    except Block.DoesNotExist as e:
        return render(request, 'cawas/error.html', {"message": "No existe Bloque2. (" + e.message + ")"})

    # Variables Para GET
    vblocks = Block.objects.all()
    vchannels = Channel.objects.all()
    vdevices = Device.objects.all()
    vgirls = Girl.objects.all()
    vlanguages = Language.objects.all()

    vmovies = Movie.objects.all()
    vcapitulos = Episode.objects.all()

    context = {'message': message, 'vblocks': vblocks, 'vchannels': vchannels,
               'vdevices': vdevices, 'vgirls': vgirls, 'vlanguages': vlanguages,
               'vmovies': vmovies, 'vcapitulos': vcapitulos, 'vblock':vblock,
               'vmovienotselect':vmovienotselect, 'vgirlnotselect':vgirlnotselect,
               'vepisodenotselect':vepisodenotselect,'vmovieselect':vmovieselect,
               'vgirlselect':vgirlselect, 'vepisodeselect':vepisodeselect
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
        # Parsear JSON
        try:
            pathfilesport = Setting.objects.get(code='image_repository_path_portrait')
            pathfilesland = Setting.objects.get(code='image_repository_path_landscape')
            strjson = request.POST['varsToJSON']
            decjson = json.loads(strjson)

            vasset = Asset.objects.get(asset_id=decjson['Episode']['asset_id'])
            print "asset_episode " + vasset.asset_id
            vasset.asset_type = "episode"
            vasset.save()

            vepisode.asset = vasset

            vepisode.original_title = decjson['Episode']['original_title']
            vepisode.channel = Channel.objects.get(pk=decjson['Episode']['channel_id'])
            print "YEAR: " + decjson['Episode']['year']
            if (decjson['Episode']['year']!=''):
                vepisode.year = decjson['Episode']['year']

            vepisode.cast = decjson['Episode']['cast']
            vepisode.directors = decjson['Episode']['directors']
            vepisode.display_runtime = decjson['Episode']['display_runtime']
            print "Asset_serie_id" + decjson['Episode']['serie_id']
            vasset_serie = Asset.objects.get(asset_id=decjson['Episode']['serie_id'])
            vepisode.serie = Serie.objects.get(asset=vasset_serie)
            vepisode.chapter = decjson['Episode']['chapter']
            vepisode.season = decjson['Episode']['season']

            #vschedule_date = datetime.datetime.strptime(decjson['Episode']['publish_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
            #vepisode.publish_date = vschedule_date
            #vepisode.language = Language.objects.get(code=decjson['Block']['language'])



            #print "Device:" + str(decjson['Block']['target_device_id'])
            #vepisode.target_device = Device.objects.get(pk=int(decjson['Block']['target_device_id']))

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

        """
        vepisodemetadata = decjson['Episode']['Episodemetadatas']
        for item in vepisodemetadata:
            try:
                emd = EpisodeMetadata()
                vlang = Language.objects.get(code=item['Episodemetadata']['language'])
                emd.language = vlang
                emd.title = item['Episodemetadata']['title']
                emd.summary_short = item['Episodemetadata']['summary_short']
                emd.summary_long = item['Episodemetadata']['summary_long']
                emd.subtitle = item['Episodemetadata']['subtitle']
                vschedule_date = datetime.datetime.now().strftime('%Y-%m-%d')
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
                              {"message": "Error al Guardar MetadataGirl. (" + e.message + ")"})
        """
        vflag = "success"
        message = 'Bloque - Registrado Correctamente'
        # Fin datos Bloque

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
               'vlanguages': vlanguages, 'vseries':vseries, 'vmovies': vmovies, 'vcapitulos': vcapitulos, 'vassets':vassets}

    #Episode OK
    #Asset OK
    #Imagenes OK
    #Metadata Falta
    #categorias OK
    #girls OK
    #
    return render(request, 'cawas/episodes/add.html', context)


def edit_episodes_view(request, asset_id):

    context = {'message': 'mensaje'}
    return render(request, 'cawas/episodes/edit.html', context)




def add_asset_view(request):
    try:
        print request.POST
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


# Borrar comentario
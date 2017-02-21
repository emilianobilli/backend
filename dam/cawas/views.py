from django.shortcuts import render

# Create your views here.
import datetime, os, json
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import Channel, Asset, Episode, PublishQueue,  Block, Serie, SerieMetadata, Movie, MovieMetadata, Girl,GirlMetadata,  Category,CategoryMetadata, Language, Image
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.http import Http404
from django.conf import settings
from django.db import IntegrityError




"""
def enqueue_item(item_id, item_type, sched_date):
    job = PublishQueue()

    job.item_id       = item_id
    job.item_type     = item_type
    job.schedule_date = sched_date
    # Traer endpoint de la configuracion
    job.endpoint      = "http://www.zolechamedia.net:8000"
"""


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
        (1, "MOVIE/CAPITULOS"),
        (2, "BLOQUES"),
        (3, "CHICAS"),
        (4, "CATEGORIAS")
    )

    assetstypes = (
        (1, "Movies/Capitulos"),
        (2, "Serie"),
        (3, "Bloques"),
        (4, "Chicas"),
        (5, "Categoria")
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

    pathfiles = 'cawas/static/files/movies/'
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

       #TRATAMIENTO DE IMAGEN Portrait
       img = Image()
       img.portrait =  request.FILES['ThumbHor']
       img.name = 'M' + vasset.asset_id

       varchivo = pathfiles + img.name + '-portrait.jpg'
       img.portrait.name = varchivo
       #si existe archivo, lo borra
       if os.path.isfile(varchivo):
           os.remove(varchivo)

       #Landscape
       img.landscape = request.FILES['ThumbVer']
       varchivo = pathfiles + img.name + '-landscape.jpg'
       img.landscape.name = varchivo
       # si existe archivo, lo borra
       if os.path.isfile(varchivo):
           os.remove(varchivo)

       img.save()
       mv.image = img

       print varchivo

       #Channel
       try:
           vchannel = Channel.objects.get(pk=decjson['Movie']['channel_id'])
       except Asset.DoesNotExist as e:
           return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})

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
       for item in vmoviesmetadata:
           try:
               #CREAR METADATA POR IDIOMA
               mmd = MovieMetadata();
               vlanguage = Language.objects.get(code=item['Moviemetadata']['language'])
               mmd.language = vlanguage
               mmd.title = item['Moviemetadata']['title']
               mmd.summary_short = item['Moviemetadata']['summary_short']
               mmd.summary_long = item['Moviemetadata']['summary_long']
               mmd.movie = mv
               mmd.save()

               #recorrer el publicZone y genera un PublicQueue por cada idioma
               #vzones = PublishZone.objects.all()
               #for zone in vzones:

               # CREAR COLA DE PUBLICACION
               vpublish = PublishQueue()
               vpublish.item_id = vasset.asset_id
               vpublish.item_lang = vlanguage
               vpublish.item_type = 'AS'
               vpublish.status = 'Q'
               #vpublish.zone = zone
               vpublish.schedule_date = datetime.datetime.strptime(item['Moviemetadata']['schedule_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
               vpublish.save()

           except Language.DoesNotExist as e:
               return render(request, 'cawas/error.html', {"message": "No existe Lenguaje. (" + e.message + ")"})

       message = 'Registrado correctamente'
       # FIN DE POST


    #VARIABLES PARA GET
    #CARGAR VARIABLES USADAS EN FRONT
    assets = Asset.objects.filter(asset_type="unknown")
    vmovies = Movie.objects.all()
    channels = Channel.objects.all()
    girls = Girl.objects.all()
    categories = Category.objects.all()
    vlanguages = Language.objects.all()
    title = 'Nueva Movie'
    context = {'title': title, 'assets':assets, 'channels':channels, 'girls':girls,  'categories':categories, 'movies':vmovies, 'vlanguages':vlanguages }
    return render(request, 'cawas/movies/add.html', context)
# Fin add_movies_view



def edit_movies_view(request, asset_id):
    #AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
       return redirect(login_view)
    # EDIT - MOVIE: en el GET debe cargar variables, y en POST debe leer JSON

    pathfiles = 'cawas/static/files/movies/'

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
       except Asset.DoesNotExist as e:
           return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})
       except Movie.DoesNotExist as e:
           return render(request, 'cawas/error.html', {"message": "No existe Movie asociado al Asset. (" + e.message + ")"})

       #TRATAMIENTO DE IMAGEN Portrait
       mv.image.portrait = request.FILES['ThumbHor']
       varchivo = pathfiles + mv.image.name + '-portrait.jpg'
       mv.image.portrait.name = varchivo
       #si existe archivo, lo borra
       if os.path.isfile(varchivo):
           os.remove(varchivo)


       #Landscape
       mv.image.landscape = request.FILES['ThumbVer']
       varchivo = pathfiles + mv.image.name + '-landscape.jpg'
       mv.image.landscape.name = varchivo
       # si existe archivo, lo borra
       if os.path.isfile(varchivo):
           os.remove(varchivo)
       mv.image.save()

       #mv.image = img
       print decjson['Movie']['asset_id']

       #Channel
       try:
           vchannel = Channel.objects.get(pk=decjson['Movie']['channel_id'])
       except Asset.DoesNotExist as e:
           return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})

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
       for item in vmoviesmetadata:
           try:
               #CREAR METADATA POR IDIOMA
               mmd = MovieMetadata();
               vlanguage = Language.objects.get(code=item['Moviemetadata']['language'])
               mmd.language = vlanguage
               mmd.title = item['Moviemetadata']['title']
               mmd.summary_short = item['Moviemetadata']['summary_short']
               mmd.summary_long = item['Moviemetadata']['summary_long']
               mmd.movie = mv
               mmd.save()

               # CREAR COLA DE PUBLICACION
               vpublish = PublishQueue()
               vpublish.item_id = vasset.asset_id
               vpublish.item_lang = vlanguage
               vpublish.item_type = 'AS'
               vpublish.status = 'Q'
               vpublish.schedule_date = datetime.datetime.strptime(item['Moviemetadata']['schedule_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
               vpublish.save()


           except Language.DoesNotExist as e:
               return render(request, 'cawas/error.html', {"message": "No existe Lenguaje. (" + e.message + ")"})

       message = 'archivo subido ok'
       # FIN DE POST

    #VARIABLES PARA GET - CARGAR MOVIE
    try:
        vasset = Asset.objects.get(asset_id=asset_id)
        vmovie = Movie.objects.get(asset=vasset)
        vgirlselected = vmovie.girls.all()
        vgirlnotselected = Girl.objects.exclude(id__in=vgirlselected)
        vgirlselected = vmovie.girls.all()
        vmoviemetadata = MovieMetadata.objects.filter(movie=vmovie)
        vcategoryselected = vmovie.category.all()
        vcategorynotselected = Category.objects.exclude(id__in=vcategoryselected)
        languages = Language.objects.all()

        #nuevo diccionario para completar lenguages y metadata
        vlangmetadata=[]
        for itemleng in languages:
            vmoviemetadata = None
            try:
                vmoviemetadata = MovieMetadata.objects.get(movie=vmovie, language=itemleng)
                vlangmetadata.append({'checked':True, 'code':itemleng.code, 'name':itemleng.name, 'title': vmoviemetadata.title,
                                      'summary_short': vmoviemetadata.summary_short, 'summary_long': vmoviemetadata.summary_long,
                                      'publish_date': vmoviemetadata.publish_date})
            except:
                vlangmetadata.append({'code':itemleng.code, 'name':itemleng.name,'titulo':'', 'descripcion':'', 'fechapub':''})


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
               'asset_id':asset_id}

    return render(request, 'cawas/movies/edit.html', context)
# Fin edit_movies_view

#</CRUD MOVIES>




#<CRUD GIRL>
def add_girl_view(request):
    #AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)

    vg_pathfiles = 'cawas/static/files/girls/'
    message = ''

    #POST - Obtener datos del formulario y guardar la metadata
    if request.method == 'POST':
        # VARIABLES
        vasset = Asset()
        g = Girl()
        vimg = Image()

        #parsear JSON
        strjson = request.POST['strjson']
        decjson = json.loads(strjson)

        #CREAR UN ASSET
        vasset.asset_type = "girl"
        vasset.save()

        # TRATAMIENTO DE IMAGEN: nombre de imagen = a Asset_id
        if request.FILES['imagehor'] :
            vimg.portrait = request.FILES['imagehor']
            vimg.name = vasset.asset_id
            varchivo = vg_pathfiles + vimg.name + '.jpg'
            if os.path.isfile(varchivo):
                os.remove(varchivo)
            vimg.portrait.name = varchivo
            try:
                vimg.save()
            except IntegrityError  as e:
                raise Http404("IMANGE - Ya existe una imagen con el mismo nombre.")
            g.image = vimg

        #CREAR GIRL
        g.asset = vasset
        g.name  = decjson['Girl']['name']
        g.type = decjson['Girl']['type']
        #df = DateFormat(decjson['Girl']['birth_date'])
        #g.birth_date = decjson['Girl']['birth_date']
        g.height = decjson['Girl']['height']
        g.weight = decjson['Girl']['weight']
        g.save()

        #CREAR METADATAGIRL
        vgirlmetadata = decjson['Girl']['Girlmetadatas']
        for item in vgirlmetadata:
            gmd = GirlMetadata()
            gmd.language = get_object_or_404(Language, code=item['Girlmetadata']['language'])
            gmd.description = item['Girlmetadata']['description']
            gmd.nationality = item['Girlmetadata']['nationality']
            gmd.girl = g
            gmd.save()

        message ='Girl, generada'
        # CARGAR METADATA

    context = {'message':message}
    #return render(request, 'cawas/girls/add.html', context)
    return render(request, 'cawas/pruebas/subir_img.html', context)



def edit_girl_view(request):
    #AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)

    #VARIABLES LOCALES
    message= ''
    vg_pathfiles = 'cawas/static/files/girls/'

    if request.method == 'POST':
        #VARIABLES
        vasset = Asset()
        vgirl = Girl()
        vimg = Image()

        # Parsear JSON
        strjson = request.POST['strjson']
        decjson = json.loads(strjson)

        # Leer GIRL desde AssetID
        try:
            vasset = Asset.objects.get(asset_id=decjson['Girl']['asset_id'])
            vgirl = Girl.objects.get(asset=vasset)
        except Asset.DoesNotExist:
            raise Http404("ASSET - No existe registro.")
        except Girl.DoesNotExist:
            raise Http404("GIRL - No existe registro.")


        # TRATAMIENTO DE IMAGEN: nombre de imagen = a Asset_id
        if  not(request.FILES['imagehor'] is None):
            vimg.portrait = request.FILES['imagehor']
            vimg.name = vasset.asset_id
            varchivo = vg_pathfiles + vimg.name + '.jpg'
            if os.path.isfile(varchivo):
                os.remove(varchivo)
            vimg.portrait.name = varchivo
            try:
                vimg.save()
            except IntegrityError  as e:
                raise Http404("IMANGE - Ya existe una imagen con el mismo nombre.")
            vgirl.image = vimg

        #Editar Girl
        vgirl.name = decjson['Girl']['name']
        vgirl.type = decjson['Girl']['type']
        # df = DateFormat(decjson['Girl']['birth_date'])
        # g.birth_date = decjson['Girl']['birth_date']
        vgirl.height = decjson['Girl']['height']
        vgirl.weight = decjson['Girl']['weight']
        vgirl.save()

        #BORRAR Y CREAR METADATA
        vgirlmetadatas = decjson['Girl']['Girlmetadatas']
        gmds = GirlMetadata.objects.filter(girl=vgirl)
        gmds.delete()
        for item in vgirlmetadatas:
            gmd = GirlMetadata()
            gmd.language = get_object_or_404(Language, code=item['Girlmetadata']['language'])
            gmd.description = item['Girlmetadata']['description']
            gmd.nationality = item['Girlmetadata']['nationality']
            gmd.girl = vgirl
            gmd.save()

    context = {'message': message}
    return render(request, 'cawas/pruebas/subir_img.html', context)
#</CRUD GIRL>



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




#<CRUD SERIE>
def add_serie_view(request):
    # AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)

    # VARIABLES LOCALES
    message = ''
    vg_pathfiles = 'cawas/static/files/series/'

    if request.method == 'POST':
        #VARIABLES
        vserie = Serie()
        vimg = Image()
        vasset = Asset()

        # Parsear JSON
        strjson = request.POST['strjson']
        decjson = json.loads(strjson)

        vasset.asset_type="serie"
        vasset.save()

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
                    vserie.image = vimg
                else:
                    vserie.image = Image.objects.get(name=vimg.name)  #se mantiene la imagen actual
            except IntegrityError  as e:
                message = "SERIE - Ya existe una imagen con el mismo nombre. (" + e.message + ")"
                return render(request, 'cawas/error.html', {"message": message})
        #FIN IMAGEN

        #Datos de Serie
        vserie.asset = vasset
        vserie.original_title = decjson['Serie']['original_title']
        vserie.year = decjson['Serie']['year']
        vserie.cast = decjson['Serie']['cast']
        vserie.directors = decjson['Serie']['directors']
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
            smd.title = item['Seriemetadata']['title']
            smd.summary_short = item['Seriemetadata']['summary_short']
            smd.summary_long = item['Seriemetadata']['summary_long']
            smd.serie = vserie
            smd.save()

    context = {'message': message}
    return render(request, 'cawas/pruebas/subir_img.html', context)



def edit_serie_view(request):
    # AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)

    # VARIABLES LOCALES
    message = ''
    vg_pathfiles = 'cawas/static/files/series/'

    if request.method == 'POST':
        # VARIABLES
        vserie = Serie()
        vimg = Image()
        vasset = Asset()

        # Parsear JSON
        strjson = request.POST['strjson']
        decjson = json.loads(strjson)

        # Leer GIRL desde AssetID
        try:
            vasset = Asset.objects.get(asset_id=decjson['Serie']['asset_id'])
            vserie = Serie.objects.get(asset=vasset)
        except Asset.DoesNotExist:
            raise Http404("ASSET - No existe registro.")

        # TRATAMIENTO DE IMAGEN: nombre de imagen = a Asset_id
        if not (request.FILES['imagehor'] is None):
            vimg.portrait = request.FILES['imagehor']
            vimg.name = request.FILES['imagehor'].name
            varchivo = vg_pathfiles + vimg.name + '.jpg'
            vimg.portrait.name = varchivo
            if os.path.isfile(varchivo):
                os.remove(varchivo)
            try:
                if not (Image.objects.filter(name=vimg.name).exists()):  # si no esta en la base de datos, se crea IMAGE
                    # borra fisicamente imagen si existe
                    vimg.save()
                    vserie.image = vimg
                else:
                    vserie.image = Image.objects.get(name=vimg.name)  # se mantiene la imagen actual
            except IntegrityError  as e:
                message = "SERIE - Ya existe una imagen con el mismo nombre. (" + e.message + ")"
                return render(request, 'cawas/error.html', {"message": message})
        # FIN IMAGEN

        # Datos de Serie
        vserie.asset = vasset
        vserie.original_title = decjson['Serie']['original_title']
        vserie.year = decjson['Serie']['year']
        vserie.cast = decjson['Serie']['cast']
        vserie.directors = decjson['Serie']['directors']
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
        smds = SerieMetadata.objects.filter(serie=vserie)
        smds.delete()
        for item in vseriemetadatas:
            smd = SerieMetadata()
            try:
                smd.language = Language.objects.get(code=item['Seriemetadata']['language'])
            except Language.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe LANGUAGE. (" + e.message + ")"})
            smd.title = item['Seriemetadata']['title']
            smd.summary_short = item['Seriemetadata']['summary_short']
            smd.summary_long = item['Seriemetadata']['summary_long']
            smd.serie = vserie
            smd.save()

    context = {'message': message}
    return render(request, 'cawas/pruebas/subir_img.html', context)

#</CRUD SERIE>




#<CRUD BLOCK>
def add_block_view(request):
    # AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)

    # VARIABLES LOCALES
    message = ''
    vg_pathfiles = 'cawas/static/files/block/'

    if request.method == 'POST':
        # VARIABLES
        vblock = Block()
        vasset = Asset()
        vchannel = Channel()

        # Parsear JSON
        strjson = request.POST['strjson']
        decjson = json.loads(strjson)

        # Datos de Serie
        vblock.asset = vasset
        vblock.name = decjson['Block']['name']
        vblock.save()

        # Lenguaje
        try:
            vasset.language = Language.objects.get(code=decjson['Serie']['language'])
        except Language.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe LENGUAJE. (" + e.message + ")"})

        # Channel
        try:
            vchannel.channel = Channel.objects.get(pk=decjson['Serie']['channel_id'])
        except Channel.DoesNotExist as e:
            return render(request, 'cawas/error.html', {"message": "No existe Channel. (" + e.message + ")"})



        # CARGAR ASSETS
        vassets = decjson['Serie']['assets']
        for item in vassets:
            try:
                vasset = Asset.objects.get(pk=item['asset_id'])
                vblock.assets.add(vasset)
            except Asset.DoesNotExist as e:
                return render(request, 'cawas/error.html', {"message": "No existe Asset. (" + e.message + ")"})



        vblock.save()
        message = 'Bloque - Registrado Correctamente'
        # Fin datos Bloque


    context = {'message': message}
    return render(request, 'cawas/pruebas/subir_img.html', context)
#<CRUD BLOCK>



def add_asset_view(request):
    try:
        print request.POST
        strjson = request.body
        decjson = json.loads(strjson)

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
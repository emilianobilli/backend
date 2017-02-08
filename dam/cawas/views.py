from django.shortcuts import render

# Create your views here.

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import Movie, Channel, Asset, Episode, Serie, MovieMetadata,Girl, Category, Language, GirlMetadata,Image
import datetime, os
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.shortcuts import get_object_or_404, render
from django.http import Http404
from django.conf import settings
from datetime import datetime



#<PRUEBAS - QUITAR ESTO>


def pruebas(request):
    registros = Movie.objects.get(pk=1)
    context = {'registros': registros}
    return render(request, 'cawas/pruebas/prueba.html', context)


def current_datetime(request):
    #now = datetime.datetime.now()
    #html = "<html><body>It is now%s.</body></html>" % now
    #return HttpResponse(html)
    now = datetime.datetime.now
    #t = Template("<html><body>It is now asdfasdf {{ current_date }}.</body></html>")
    #html = t.render(Context({'current_date': now}))
    #return HttpResponse(html)

    #t = get_template('cawas/pruebas/current_datetime.html')
    #html = t.render(Context({'current_date': now}))
    #return HttpResponse(html)
    current_date = datetime.datetime.now

    return render_to_response('cawas/pruebas/current_datetime.html', locals())
    #return render_to_response('cawas/pruebas/current_datetime.html', {'current_date': current_date})




def hours_ahead(request, offset):
    offset = int(offset)
    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
    html = "<html><body>In%s hour(s), it will be%s.</body></html>"% (offset, dt)
    #return HttpResponse(html)


#</PRUEBAS - QUITAR ESTO >


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
   # ALTA - MOVIE: en el GET debe cargar variables, y en POST debe leer JSON
   # VARIABLES

    pathfiles = 'cawas/static/files/movies/'
    if request.method == 'POST':
       # parsear JSON
       strjson = request.POST['strjson']
       decjson = json.loads(strjson)

       # DECLARACION DE OBJECTOS
       mv = Movie()

       #TRATAMIENTO DE IMAGEN
       img = Image()
       img.portrait = request.FILES['imagehor']
       img.name = img.portrait.name
       varchivo = pathfiles + img.portrait.name
       if os.path.isfile(varchivo):
           os.remove(varchivo)
       img.portrait.name = varchivo
       img.save()

       # CARGAR MOVIE
       vasset = get_object_or_404(Asset, asset_id=decjson['Movie']['asset_id'])
       vchannel = get_object_or_404(Channel, pk=decjson['Movie']['channel_id'])
       mv.image = img
       mv.asset = vasset
       mv.channel = vchannel
       mv.original_title = decjson['Movie']['original_title']
       mv.year = int(decjson['Movie']['year'])
       mv.cast = decjson['Movie']['cast']
       mv.directors = decjson['Movie']['directors']
       mv.display_runtime = decjson['Movie']['display_runtime']
       mv.save()

       # CARGAR GIRLS
       vgirls = decjson['Movie']['girls']
       for item in vgirls:
           girl = get_object_or_404(Girl, pk=item['girl_id'])
           mv.girls.add(girl)

       # CARGAR CATEGORIES
       vcategories = decjson['Movie']['categories']
       for item in vcategories:
           c = get_object_or_404(Category, pk=item['category_id'])
           mv.category.add(c)

       # CARGAR METADATA
       vmoviesmetadata = decjson['Movie']['Moviesmetadata']
       for item in vmoviesmetadata:
           mmd = MovieMetadata();
           mmd.language = get_object_or_404(Language, code=item['Moviemetadata']['language'])
           mmd.title = item['Moviemetadata']['title']
           mmd.summary_short = item['Moviemetadata']['summary_short']
           mmd.summary_long = item['Moviemetadata']['summary_long']
           mmd.movie = mv
           mmd.save()

       # ACTUALIZAR EL ASSET A MOVIE
       vasset.asset_type = "movie"
       vasset.save()

       message = 'archivo subido ok'
       # FIN DE POST

    #CARGAR VARIABLES USADAS EN FRONT
    assets = Asset.objects.filter(asset_type="unknown")
    channels = Channel.objects.all()
    girls = Girl.objects.all()
    categories = Category.objects.all()
    title = 'Nueva Movie'
    context = {'title': title, 'assets':assets, 'channels':channels, 'girls':girls,  'categories':categories }
    return render(request, 'cawas/pruebas/subir_img.html', context)
# Fin add_movies_view




def edit_movies_view(request):
    #AUTORIZACION DE USUARIO
    if not request.user.is_authenticated:
        return redirect(login_view)

    #EDIT - MOVIE: en el GET debe cargar variables, y en POST debe leer JSON

    #VARIABLES
    pathfiles = 'cawas/static/files/movies/'

    if request.method == 'POST':
        #parsear JSON
        strjson  = request.POST['strjson']
        decjson = json.loads(strjson)

        # DECLARACION DE OBJECTOS
        img = Image()
        # Leer Movie desde AssetID
        vasset = get_object_or_404(Asset, asset_id=decjson['Movie']['asset_id'])
        mv =  get_object_or_404(Movie, asset=vasset)
        imgback = mv.image

        img.portrait = request.FILES['imagehor']
        img.name = img.portrait.name

        #comparar imagen de BD con Imagen que subio el usuario
        if imgback.name <> img.name:
            varchivo = pathfiles + img.portrait.name
            if os.path.isfile(varchivo):
                os.remove(varchivo)
            img.portrait.name = varchivo
            img.save()


        #CARGAR MOVIE
        vchannel = get_object_or_404(Channel, pk=decjson['Movie']['channel_id'])
        mv.image = img
        mv.channel = vchannel
        mv.original_title = decjson['Movie']['original_title']
        mv.year = int(decjson['Movie']['year'])
        mv.cast = decjson['Movie']['cast']
        mv.directors = decjson['Movie']['directors']
        mv.display_runtime = decjson['Movie']['display_runtime']
        mv.save()

        #CARGAR GIRLS
        vgirls = decjson['Movie']['girls']
        for item in vgirls:
            girl = get_object_or_404(Girl, pk=item['girl_id'])
            mv.girls.add(girl)

        #CARGAR CATEGORIES
        categories= []
        mv.category = categories
        vcategories = decjson['Movie']['categories']
        for item in vcategories:
            c = get_object_or_404(Category, pk=item['category_id'])
            mv.category.add(c)

        #CARGAR METADATA
        vmoviesmetadata = decjson['Movie']['Moviesmetadata']
        c = get_object_or_404(Category, pk=item['category_id'])

        mmds = MovieMetadata.objects.filter(movie=mv)
        mmds.delete()
        for item in vmoviesmetadata:
            mmd = MovieMetadata();
            mmd.language = get_object_or_404(Language, code=item['Moviemetadata']['language'])
            mmd.title = item['Moviemetadata']['title']
            mmd.summary_short = item['Moviemetadata']['summary_short']
            mmd.summary_long = item['Moviemetadata']['summary_long']
            mmd.movie = mv
            mmd.save()
        #NO SE ACTUALIZA EL ASSET TYPE

        message='archivo subido ok'
        #FIN DE POST

    # CARGAR VARIABLES USADAS EN FRONT
    assets = Asset.objects.filter(asset_type="unknown")
    channels = Channel.objects.all()
    girls = Girl.objects.all()
    categories = Category.objects.all()
    title = 'Nueva Movie'

    context = {'title': title, 'assets': assets, 'channels': channels, 'girls': girls, 'categories': categories}
    #return render(request, 'cawas/movies/add.html', context)
    return render(request, 'cawas/pruebas/subir_img.html', context)
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
            vimg.save()
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
        except Asset.DoesNotExist:
            raise Http404("ASSET - No existe registro.")

        try:
            vgirl = Girl.objects.get(asset=vasset)
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
            vimg.save()
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
    # return render(request, 'cawas/girls/add.html', context)
    return render(request, 'cawas/pruebas/subir_img.html', context)


#</CRUD GIRL>

def notFoundObject(request, message):
    context = {'message': message}
    return render(request, 'cawas/pruebas/notfound.html', context)
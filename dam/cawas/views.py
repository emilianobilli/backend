from django.shortcuts import render

# Create your views here.

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from .models import Movie, Channel, Asset, Episode, Serie, MovieMetadata,Girl, Category, Language
#from django.template import Template, Context
#from django.http import HttpResponse
import datetime
#from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger





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



def add_movies_view(request):
    #AUTENTICACION DE USUARIO
    if not request.user.is_authenticated:
       return redirect(login_view)

    vasset_id = '0'
    vgirls = ''
    #POST - Obtener datos del formulario y guardar la metadata
    if request.method == 'POST':
        #leer variables
        vasset_id = request.POST['selectedID2']
        vchannel_id = request.POST['canal']
        vgirls = request.POST.getlist('pornostart1')
        vcategorias = request.POST.getlist('categories')

        #obtener objetos
        asset = Asset.objects.get(asset_id=vasset_id)
        vchannel = Channel.objects.get(id=vchannel_id)

        #Crear Movie
        mv = Movie()
        mv.asset = asset
        mv.channel = vchannel
        mv.original_title = request.POST['orginalTitle']
        mv.cast = request.POST['elenco']
        mv.save()

        for item in vgirls:
            mv.girls.add(Girl.objects.get(id=item))
        for item in vcategorias:
            mv.category.add(Category.objects.get(id=item))

        #Actualizar el tipo de Assets a Movie
        asset.asset_type = "movie"
        asset.save()

        #Obtener los idiomas seleccionados, por cada idioma crear un metadatamovie
        #mv.year = request.POST['year']
        #mv.image = request.POST['ThumbHor']
        #mv.image =
        #mv.runtime =
        #mv.display_runtime =
        #mv.thumbnails =

        #CREAR  MovieMetadata
        #Identificar el Idioma y luego guardar

        # summary_long - falta
        # subtitle - falta
        # modification_dat - falta
        # publish_date - falta
        # publish_status - falta
        lang = Language()
        if (request.POST['chk_es'] is not None):
            vtituto = request.POST['tit_spa']
            vshort_desc = request.POST['short_desc_spa']
            vdate = request.POST['date_spa']
            vides = request.POST['id_es']
            lang = Language.objects.get(pk=vides)
            mmd = MovieMetadata(movie=mv, language=lang,title=vtituto,summary_short=vshort_desc,publish_date=vdate)

        #PORTUGUES METADATA
        if (request.POST['chk_pt'] is not None):
            vtituto = request.POST['tit_por']
            vshort_desc = request.POST['short_desc_por']
            vdate = request.POST['date_por']
            vidpt = request.POST['id_pt']
            lang = Language.objects.get(pk=vidpt)
            mmd = MovieMetadata(movie=mv, language=lang, title=vtituto, summary_short=vshort_desc, publish_date=vdate)

        #INGLES METADATA
        if (request.POST['chk_en'] is not None):
            vtituto = request.POST['tit_eng']
            vshort_desc = request.POST['short_desc_eng']
            vdate = request.POST['date_eng']
            viden = request.POST['id_en']
            lang = Language.objects.get(pk=viden)
            mmd = MovieMetadata(movie=mv, language=lang, title=vtituto, summary_short=vshort_desc, publish_date=vdate)
    #FIN DE POST



    #CARGAR VARIABLES USADAS EN FRONT
    assets = Asset.objects.filter(asset_type="unknown")
    channels = Channel.objects.all()
    girls = Girl.objects.all()
    categories = Category.objects.all()
    title = 'Nueva Movie'
    context = {'title': title, 'assets':assets, 'vasset_id':vasset_id, 'channels':channels, 'girls':girls, 'vgirls': vgirls, 'categories':categories }

    return render(request, 'cawas/movies/add.html', context)
    # Fin add_movies_view


#</CRUD MOVIES>


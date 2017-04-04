# Create your views here.
import os, datetime, json
from django.shortcuts import render,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.http import  HttpResponse
from Controller.GirlController import GirlController
from Controller.MovieController import MovieController
from Controller.SerieController import SerieController
from Controller.BlockController import BlockController
from Controller.EpisodeController import EpisodeController
from Controller.SliderController import SliderController
from Controller.GirlController import GirlController
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


def edit_movies_view(request, asset_id):
    mc = MovieController()
    return mc.edit(request, asset_id)


#<GIRL>
def add_girls_view(request):
    gc = GirlController()
    return gc.add(request)

def edit_girls_view(request, asset_id):
    #AUTENTICACION DE USUARIO
    gc = GirlController()
    return gc.edit(request, asset_id)


#<CRUD SERIE>
def add_series_view(request):
    # AUTENTICACION DE USUARIO
    controller = SerieController()
    return controller.add(request)

def edit_series_view(request, asset_id):
    # AUTENTICACION DE USUARIO
    controller = SerieController()
    return controller.edit(request, asset_id)


def add_blocks_view(request):
    controller = BlockController()
    return controller.edit(request)

#</FIN ADD BLOCK>


def edit_blocks_view(request, block_id):
    controller = BlockController()
    return controller.edit(request, block_id)

#<Fin EDIT BLOCKS>



def add_episodes_view(request):
    controller = EpisodeController()
    return controller.add(request)


def edit_episodes_view(request, episode_id):
    controller = EpisodeController()
    return controller.edit(request, episode_id)



def add_sliders_view(request):
    controller = SliderController()
    return controller.add(request)


def edit_sliders_view(request, slider_id):
    controller = SliderController()
    return controller.edit(request, slider_id)



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
    gc = GirlController()

    if gc.unpublish_girls_view(request,id)== 0 :
        flag='success'
        message = gc.message_return

    if gc.unpublish_girls_view(request, id) == -1:
        flag = 'error'
        message = gc.message_return

    context = {'flag':flag, 'message':message}
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


# Listados
def list_movies_view(request):
    gc = MovieController()
    return gc.list(request)


def list_girls_view(request):
    gc = GirlController()
    return gc.list(request)

def list_blocks_view(request):
    gc = BlockController()
    return gc.list(request)



def list_episodes_view(request):
    gc = EpisodeController()
    return gc.list(request)



def list_series_view(request):
    gc = SerieController()
    return gc.list(request)



def list_sliders_view(request):
    gc = SliderController()
    return gc.list(request)




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


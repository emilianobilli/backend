# Create your views here.
import os, datetime, json
from django.shortcuts import render,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.http import  HttpResponse
from django.core.urlresolvers import reverse
from Controller.MovieController import MovieController
from Controller.VideoLogController import VideoLogController
from Controller.SerieController import SerieController
from Controller.GirlController import GirlController
from Controller.EpisodeController import EpisodeController
from Controller.BlockController import BlockController
from Controller.CategoryController import CategoryController
from Controller.SliderController import SliderController
from Controller.CableOperatorController import CableOperatorController
from Controller.TagController import TagController
from Controller.ContractController import ContractController

from Controller.LogController import LogController
from models import Channel, Device, Slider,  Episode, EpisodeMetadata, ImageQueue, PublishQueue, \
    Block, Serie, SerieMetadata, Movie, MovieMetadata, CategoryMetadata, PublishZone,Girl, GirlMetadata, Asset, Language, Category, Image, Setting
from django.contrib.auth import authenticate, login, logout
#from ..backend_sdk import ApiBackendResource
from Helpers.GlobalValues import *


#Variables:
MESSAGE_TMP = ''
FLAG_TMP = ''


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




def menu_view(request):
    if not request.user.is_authenticated:
        return redirect(login_view)

    message = ''
    flag = ''

    if request.session.has_key('list_menu_message'):
        if request.session['list_menu_message'] != '':
            message = request.session['list_menu_message']
            request.session['list_menu_message'] = ''

    if request.session.has_key('list_menu_flag'):
        if request.session['list_menu_flag'] != '':
            flag = request.session['list_menu_flag']
            request.session['list_menu_flag'] = ''

    #<Definir Variables>
    idassetstype = 0

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
        (5, "Categorias"),
        (6, "Capitulos"),
        (7, "Sliders")
    )

    # </Definir Variables>
    #  008360
    # si hizo click en menu_view.cargar_contenido
    if request.method == 'GET':
        if 'inputid' in request.GET:
            id = request.GET['inputid']
            request.session['search_id'] = id

            print 'episode_id '+ id
            #Buscar en Movie, Girl, Category
            if (Asset.objects.filter(asset_id=id).count() > 0 ):
                asset = Asset.objects.get(asset_id=id)
                if asset.asset_type =='movie':
                    #return redirect(edit_movies_view(request, asset.asset_id))
                    return redirect(edit_movies_view, asset_id=asset.asset_id)

                if asset.asset_type == 'episode':
                    #return redirect(edit_episodes_view(request, id))
                    return redirect(edit_episodes_view, episode_id=asset.asset_id)

                if asset.asset_type == 'girl':
                    print 'isgirl'
                    #return redirect(edit_girls_view(request, asset.asset_id))
                    return redirect(edit_girls_view, asset_id=asset.asset_id)

                if asset.asset_type == 'serie':
                    print 'ingreso a serie'+ asset.asset_id
                    return redirect(edit_series_view, asset_id=asset.asset_id)


            if (Category.objects.filter(category_id=id).count() > 0 ):
                 return redirect(edit_category_view, category_id=id)

            if (Block.objects.filter(block_id = id).count() > 0 ):
                return redirect(edit_blocks_view, block_id=id)

            if (Slider.objects.filter(slider_id=id).count() > 0):
                return redirect(edit_sliders_view, slider_id=id)

            request.session['list_menu_flag'] = FLAG_ALERT
            request.session['list_menu_message'] = 'ID "'+ id + '" No Existe.'
            return redirect(menu_view)

    title = 'Menu Principal'
    context = {'message': message, 'flag':flag,'title': title, 'assetstypes':assetstypes,  'idassetstype': idassetstype}
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






#ABM VIDEOLOG
def list_videolog_view(request):
    c = VideoLogController()
    return c.index(request)

def add_videolog_view(request, asset_id):
    c = VideoLogController()
    return c.add(request,asset_id)


def edit_videolog_view(request, asset_id):
    c = VideoLogController()
    return c.edit(request, asset_id)


def findbyassetid_videolog_view(request):
    c = VideoLogController()
    return c.findByAssetId(request)


def delete_videolog_view(request):
    c = VideoLogController()
    return c.delete(request)



# ABM VIDEOLOG - FIN


#ABM TAGS
def list_tags_view(request):
    c = TagController()
    return c.index(request)


def add_tag_view(request):
    c = TagController()
    return c.add(request)

def edit_tag_view(request, tag_id):
    c = TagController()
    return c.edit(request, tag_id)

def delete_tag_view(request):
    c = TagController()
    return c.delete(request)


#ABM TAGS - Fin




def add_movies_view(request):
    mc = MovieController()
    if request.method == 'GET':
        return mc.add(request)
    if request.method == 'POST':
        mc.add(request)
        return redirect(list_movies_view)


def edit_movies_view(request, asset_id):
    mc = MovieController()
    response = mc.edit(request, asset_id)

    if request.method == 'GET':
        if mc.code_return == RETURN_ERROR:
            return redirect(list_movies_view)
        if mc.code_return == RETURN_OK:
            return response

    if request.method == 'POST':
        return redirect(list_movies_view)


def api_edit_movies_view(request):
    mc = MovieController()
    resp = mc.api_edit(request)
    return HttpResponse(resp)



#<CONTRACTS>
def add_contracts_view(request):
    mc = ContractController()
    resp = mc.add(request)
    return HttpResponse(resp)


def edit_contracts_view(request):
    mc = ContractController()
    resp = mc.edit(request)
    return HttpResponse(resp)

def delete_contracts_view(request):
    mc = ContractController()
    resp = mc.delete(request)
    return HttpResponse(resp)

def list_contracts_view(request):
    mc = ContractController()
    resp = mc.list(request)
    return HttpResponse(resp)

#</CONTRACTS>


#<GIRL>
def add_girls_view(request):
    gc = GirlController()
    if request.method == 'GET':
        return gc.add(request)
    if request.method == 'POST':
        gc.add(request)
        return redirect(list_girls_view)



def edit_girls_view(request, asset_id):
    #AUTENTICACION DE USUARIO
    gc = GirlController()
    if request.method == 'GET':
        return gc.edit(request, asset_id)
    if request.method == 'POST':
        gc.edit(request, asset_id)
        return redirect(list_girls_view)


#<CRUD SERIE>
def add_series_view(request):
    # AUTENTICACION DE USUARIO
    controller = SerieController()
    if request.method == 'GET':
        return controller.add(request)
    if request.method == 'POST':
        controller.add(request)
        return redirect(list_series_view)


def edit_series_view(request, asset_id):
    #AUTENTICACION DE USUARIO
    controller = SerieController()
    if request.method == 'GET':
        return controller.edit(request, asset_id)
    if request.method == 'POST':
        controller.edit(request, asset_id)
        return redirect(list_series_view)

def add_blocks_view(request):
    controller = BlockController()
    if request.method == 'GET':
        return controller.add(request)
    if request.method == 'POST':
        controller.add(request)
        return redirect(list_blocks_view)


def edit_blocks_view(request, block_id):
    controller = BlockController()
    if request.method == 'GET':
        return controller.edit(request, block_id)
    if request.method == 'POST':
        controller.edit(request, block_id)
        return redirect(list_blocks_view)


def add_episodes_view(request):
    controller = EpisodeController()
    if request.method == 'GET':
        return controller.add(request)
    if request.method == 'POST':
        controller.add(request)
        return redirect(list_episodes_view)


def edit_episodes_view(request, episode_id):
    controller = EpisodeController()
    if request.method == 'GET':
        return controller.edit(request, episode_id)
    if request.method == 'POST':
        controller.edit(request, episode_id)
        return redirect(list_episodes_view)



def add_sliders_view(request):
    controller = SliderController()
    if request.method == 'GET':
        return controller.add(request)
    if request.method == 'POST':
        controller.add(request)
        return redirect(list_sliders_view)


def edit_sliders_view(request, slider_id):
    controller = SliderController()
    if request.method == 'GET':
        return controller.edit(request, slider_id)
    if request.method == 'POST':
        controller.edit(request, slider_id)
        return redirect(list_sliders_view)




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
            return HttpResponse('Asset Generado Correctamente', status=200)
    except ValueError, e:
        message = "Error al leer archivo JSON. (" + e.message + ")"
        return render(request, 'cawas/error.html', {"message": message})

    context = {'message': message}
    return render(request, 'cawas/pruebas/blank.html', context)






#Funciones de Despublicacion
def unpublish_categories_view(request, id):
    controller = CategoryController()
    controller.unpublish(request, id)
    if controller.code_return == RETURN_OK:
        return redirect(list_categories_view)



def unpublish_movies_view(request, id):
    controller = MovieController()
    controller.unpublish(request, id)
    if controller.code_return == RETURN_OK:
        return redirect(list_movies_view)


def unpublish_girls_view(request, id):
    controller = GirlController()
    controller.unpublish(request, id)
    if controller.code_return == RETURN_OK:
        return redirect(list_girls_view)

# Funciones de Despublicacion
def unpublish_series_view(request, id):
    controller = SerieController()
    controller.unpublish(request, id)
    if controller.code_return == RETURN_OK:
        return redirect(list_series_view)

# Funciones de Despublicacion
def unpublish_blocks_view(request, id):
    controller = BlockController()
    controller.unpublish(request, id)
    if controller.code_return == RETURN_OK:
        return redirect(list_blocks_view)

# Funciones de Despublicacion
def unpublish_episodes_view(request, id):
    controller = EpisodeController()
    controller.unpublish(request, id)
    if controller.code_return == RETURN_OK:
        return redirect(list_episodes_view)


def unpublish_sliders_view(request, id):
    controller = SliderController()
    controller.unpublish(request, id)
    if controller.code_return == RETURN_OK:
        return redirect(list_sliders_view)



#Publicaciones
def publish_movies_view(request, id):
    controller = MovieController()
    controller.publish(request, id)
    if controller.code_return == RETURN_OK:
        return redirect(list_movies_view)

def publish_girls_view(request, id):
    controller = GirlController()
    controller.publish(request, id)
    if controller.code_return == RETURN_OK:
        return redirect(list_girls_view)

def publish_series_view(request, id):
    controller = SerieController()
    controller.publish(request, id)
    return redirect(list_series_view)


def publish_blocks_view(request, id):
    controller = BlockController()
    controller.publish(request, id)
    if controller.code_return == RETURN_OK:
        return redirect(list_blocks_view)


def publish_episodes_view(request, id):
    controller = EpisodeController()
    controller.publish(request, id)
    if controller.code_return == RETURN_OK:
        return redirect(list_episodes_view)

def publish_sliders_view(request, id):
    controller = SliderController()
    controller.publish(request, id)
    if controller.code_return == RETURN_OK:
        return redirect(list_sliders_view)

def publish_categories_view(request, id):
    controller = CategoryController()
    controller.publish(request, id)
    if controller.code_return == RETURN_OK:
        return redirect(list_categories_view)


def list_category_view(request):
    gc = CategoryController()
    return gc.list(request)


# Listados
def list_movies_view(request):
    gc = MovieController()
    return gc.list(request)



def list_girls_view(request):
    gc = GirlController()
    return gc.list(request)

def list_json_girls_view(request):
    gc = GirlController()
    return gc.list_json(request)

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

def list_categories_view(request):
    gc = CategoryController()
    return gc.list(request)






#<CRUD CATEGORIES>
def add_category_view(request):
    controller = CategoryController()
    if request.method == 'GET':
        return controller.add(request)
    if request.method == 'POST':
        controller.add(request)
        return redirect(list_categories_view)

def edit_category_view(request, category_id):
    controller = CategoryController()
    if request.method == 'GET':
        return controller.edit(request, category_id)
    if request.method == 'POST':
        controller.edit(request, category_id)
        return redirect(list_categories_view)
#</CRUD CATEGORIES>



#<CRUD CABLE OPERATOR>
def add_cableoperators_view(request):
    controller = CableOperatorController()
    if request.method == 'GET':
        return controller.add(request)
    if request.method == 'POST':
        controller.add(request)
        return redirect(list_cableoperators_view)

def edit_cableoperators_view(request, cableoperator_id):
    controller = CableOperatorController()
    if request.method == 'GET':
        return controller.edit(request, cableoperator_id)
    if request.method == 'POST':
        controller.edit(request, cableoperator_id)
        return redirect(list_cableoperators_view)


def list_cableoperators_view(request):
    c = CableOperatorController()
    return c.list(request)

def unpublish_cableoperators_view(request, id):
    controller = CableOperatorController()
    controller.unpublish(request, id)
    if controller.code_return == RETURN_OK:
        return redirect(list_cableoperators_view)

def publish_cableoperators_view(request, id):
    controller = CableOperatorController()
    controller.publish(request, id)
    if controller.code_return == RETURN_OK:
        return redirect(list_cableoperators_view)

#</CRUD CATEGORIES>

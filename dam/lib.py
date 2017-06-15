import django
import os
from django.core.exceptions import *
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dam.settings")
django.setup()
from cawas.models import *

from django.utils import timezone
from cawas.backend_sdk import *

import json
import datetime

from urlparse import urlparse
import httplib2


class SerializerException(Exception):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)


def girls_to_list(girl_list):
    girls_id = []
    girls_name = []
    girls_display = []

    for girl in girl_list:
        girls_id.append(girl.asset.asset_id)
        girls_name.append(girl.name)
        js = {}
        js["name"] = girl.name
        js["id"] = girl.asset.asset_id
        girls_display.append(json.dumps(js))

    return girls_id, girls_name, girls_display


def block_serializer(block_id):
    ret = []
    try:
        block = Block.objects.get(block_id=block_id)
    except ObjectDoesNotExist:
        msg = "Block with ID %s does not exist" % block_id
        raise SerializerException(msg)

    ret.append(block.toDict())

    return ret


def slider_serializer(slider_id):
    ret = []
    try:
        slider = Slider.objects.get(slider_id=slider_id)
    except:
        msg = "Slider with ID %s does not exist" % slider_id
        raise SerializerException(msg)

    ret.append(slider.toDict())

    return ret


def category_serializer(cat_id, lang=''):
    ret = []
    try:
        category = Category.objects.get(category_id=cat_id)
    except ObjectDoesNotExist:
        msg = "Category with ID %s does not exist" % cat_id
        raise SerializerException(msg)

    category_dict = category.toDict()

    if lang == '':
        metadata_list = CategoryMetadata.objects.filter(category=category)
    else:
        try:
            language = Language.objects.get(code=lang)
        except ObjectDoesNotExist:
            msg = "Language code %s does not exist for category %s" % (lang, cat_id)
            raise SerializerException(msg)
        metadata_list = CategoryMetadata.objects.filter(category=category, language=language)

    if len(metadata_list) == 0:
        ret.append(category_dict)
    else:
        for metadata in metadata_list:
            ret.append(dict(category_dict.items() + metadata.toDict().items()))

    return ret


def channel_serializer(channel_name):
    ret = []
    try:
        channel = Channel.objects.get(name=channel_name)
    except ObjectDoesNotExist:
        msg = "Channel with name %s does not exist" % channel_name
        raise SerializerException(msg)

    ret.append(channel.toDict())

    return ret


def cableoperator_serializer(co_id):
    try:
        co = CableOperator.objects.get(cableoperator_id=co_id)
    except ObjectDoesNotExist:
        msg = "Cable Operator with ID %s does not exist" % co_id
        raise SerializerException(msg)

    try:
        CDNURL = Setting.objects.get(code="image_cdn_landscape").value
    except:
        msg = "Setting with code image_cdn_landscape does not exist"
        raise SerializerException(msg)

    co_dict = co.toDict()
    co_dict['co_media_url'] = "%s%s" % (CDNURL, co_dict['co_media_url'])

    return co_dict


def publish_cableoperator(co_id, co_url, apikey, publish_zone):
    co = cableoperator_serializer(co_id)
    endpoint = publish_zone.backend_url
    ep = ApiBackendResource(endpoint, co_url, apikey)
    try:
        print co
        ep.add(co)
        return 0, "success"
    except ApiBackendException as err:
        return -1, str(err.value)


def asset_serializer(asset_id, lang=''):
    ret = []

    try:
        asset = Asset.objects.get(asset_id=asset_id)
    except ObjectDoesNotExist:
        msg = "Asset with ID %s does not exist" % asset_id
        raise SerializerException(msg)

    if asset.asset_type == "movie":
        asset_list = movie_serializer(asset, lang)
    elif asset.asset_type == "serie":
        asset_list = serie_serializer(asset, lang)
    elif asset.asset_type == "episode":
        asset_list = episode_serializer(asset, lang)
    elif asset.asset_type == "girl":
        asset_list = girl_serializer(asset, lang)
    else:
        msg = "Invalid asset type: %s" % asset.asset_type
        raise SerializerException(msg)

    asset_dict = asset.toDict()

    block_list = Block.objects.filter(assets=asset)

    if len(block_list) > 0:
        blocks = []
        for block in block_list:
            blocks.append(block.block_id)
        asset_dict["blocks"] = blocks

    for ast in asset_list:
        ret.append(dict(ast.items() + asset_dict.items()))

    return ret


def movie_serializer(asset, lang):
    ret = []

    try:
        movie = Movie.objects.get(asset=asset)
    except ObjectDoesNotExist:
        msg = "Movie with asset id %s does not exist" % asset.asset_id
        raise SerializerException(msg)

    movie_dict = movie.toDict()

    girls_list = movie.girls.all()
    if len(girls_list) > 0:
        girls_id, girls_name, girls_display = girls_to_list(girls_list)
        movie_dict["girls_id"] = girls_id
        movie_dict["girls_name"] = girls_name
        movie_dict["girls_display"] = girls_display

    if lang == '':
        metadata_list = MovieMetadata.objects.filter(movie=movie)
    else:
        try:
            language = Language.objects.get(code=lang)
        except ObjectDoesNotExist:
            msg = "Language code %s does not exist for asset ID %s" % (lang, asset.asset_id)
            raise SerializerException(msg)
        metadata_list = MovieMetadata.objects.filter(movie=movie, language=language)

    if len(metadata_list) == 0:
        ret.append(movie_dict)
    else:
        for metadata in metadata_list:
            ret.append(dict(movie_dict.items() + metadata.toDict().items()))

    return ret


def serie_serializer(asset, lang):
    ret = []

    try:
        serie = Serie.objects.get(asset=asset)
    except ObjectDoesNotExist:
        msg = "Serie with asset id %s does not exist" % asset.asset_id
        raise SerializerException(msg)

    serie_dict = serie.toDict()

    girls_list = serie.girls.all()
    if len(girls_list) > 0:
        girls_id, girls_name, girls_display = girls_to_list(girls_list)
        serie_dict["girls_id"]      = girls_id
        serie_dict["girls_name"]    = girls_name
        serie_dict["girls_display"] = girls_display

    if lang == '':
        metadata_list = SerieMetadata.objects.filter(serie=serie)
    else:
        try:
            language = Language.objects.get(code=lang)
        except ObjectDoesNotExist:
            msg = "Language code %s does not exist for asset ID %s" % (lang, asset.asset_id)
            raise SerializerException(msg)
        metadata_list = SerieMetadata.objects.filter(serie=serie, language=language)

    if len(metadata_list) == 0:
        ret.append(serie_dict)
    else:
        for metadata in metadata_list:
            ret.append(dict(serie_dict.items() + metadata.toDict().items()))

    return ret


def episode_serializer(asset, lang):
    ret = []

    try:
        episode = Episode.objects.get(asset=asset)
    except ObjectDoesNotExist:
        msg = "Serie with asset id %s does not exist" % asset.asset_id
        raise SerializerException(msg)

    episode_dict = episode.toDict()

    girls_list = episode.girls.all()
    if len(girls_list) > 0:
        girls_id, girls_name, girls_display = girls_to_list(girls_list)
        episode_dict["girls_id"]      = girls_id
        episode_dict["girls_name"]    = girls_name
        episode_dict["girls_display"] = girls_display

    if lang == '':
        metadata_list = EpisodeMetadata.objects.filter(episode=episode)
    else:
        try:
            language = Language.objects.get(code=lang)
        except ObjectDoesNotExist:
            msg = "Language code %s does not exist for asset ID %s" % (lang, asset.asset_id)
            raise SerializerException(msg)
        metadata_list = EpisodeMetadata.objects.filter(episode=episode, language=language)

    if len(metadata_list) == 0:
        ret.append(episode_dict)
    else:
        for metadata in metadata_list:
            ret.append(dict(episode_dict.items() + metadata.toDict().items()))

    return ret


def girl_serializer(asset, lang):
    ret = []

    try:
        girl = Girl.objects.get(asset=asset)
    except ObjectDoesNotExist:
        msg = "Girl with asset id %s does not exist" % asset.asset_id
        raise SerializerException(msg)

    girl_dict = girl.toDict()

    if lang == '':
        metadata_list = GirlMetadata.objects.filter(girl=girl)
    else:
        try:
            language = Language.objects.get(code=lang)
        except ObjectDoesNotExist:
            msg = "Language code %s does not exist for asset ID %s" % (lang, asset.asset_id)
            raise SerializerException(msg)
        metadata_list = GirlMetadata.objects.filter(girl=girl, language=language)

    if len(metadata_list) == 0:
        ret.append(girl_dict)
    else:
        for metadata in metadata_list:
            ret.append(dict(girl_dict.items() + metadata.toDict().items()))

    return ret


######################### MISC ######################################




class EnqueuerException(Exception):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)


class ImporterException(Exception):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)


def check_thumbnail(asset_id):
    method = 'GET'
    body = ''
    url = "http://cdnlevel3.zolechamedia.net/%s/thumbs/%s.vtt" % (asset_id, asset_id)

    if url is not None:
        uri = urlparse(url)
    else:
        raise ImporterException('get(): url cannot be None')

    http = httplib2.Http()

    try:
        response, content = http.request(uri.geturl(), method, body)
    except socket.error as err:
        raise ImporterException(err)

    if response['status'] == '200':
        return True
    else:
        return False


def check_subtitle(asset_id, lang):
    method = 'GET'
    body = ''
    url = "http://videoauth.zolechamedia.net/subtitle/%s/%s/vtt/check" % (asset_id, lang)

    if url is not None:
        uri = urlparse(url)
    else:
        raise ImporterException('get(): url cannot be None')

    http = httplib2.Http()

    try:
        response, content = http.request(uri.geturl(), method, body)
    except socket.error as err:
        raise ImporterException(err)

    if response['status'] == '200':
        return True
    else:
        return False


def __get_language(language):
    try:
        lang = Language.objects.get(code=language)
    except ObjectDoesNotExist:
        msg = "Lenguage %s no existe" % language
        raise ImporterException(msg)
    return lang


def __get_channel(ch):
    try:
        channel = Channel.objects.get(name=ch)
    except ObjectDoesNotExist:
        msg = "El Canal %s no existe" % ch
        raise ImporterException(msg)
    return channel


def __get_girls(g):
    girls = []
    if g != '':
        g_list = g.split(",")
    else:
        g_list = []

    for girl in g_list:
        try:
            girl = Girl.objects.get(name=girl)
            girls.append(girl)
        except ObjectDoesNotExist:
            msg = "La chica %s no existe" % girl
            raise ImporterException(msg)
    return girls


def __get_categories(cat):
    categories = []
    if cat != '':
        cat = cat.replace(", ", ",")
        cat_list = cat.split(",")
    else:
        cat_list = []

    for category in cat_list:
        try:
            cat = Category.objects.get(original_name=category)
            categories.append(cat)
        except ObjectDoesNotExist:
            msg = "La Categoria %s no existe" % category
            raise ImporterException(msg)
    return categories


"""
IMPORTACION DE CATEGORIAS
"""

def __update_category(category, c_json):
    try:
        i = Image.objects.get(name=category.category_id)
    except ObjectDoesNotExist:
        i = Image()
    i.name     = category.category_id
    i.portrait = c_json["image_portrait"]
    i.save()

    category.image = i
    category.save()

    return category


def __create_category(c_json):
    category = Category()
    category.original_name = c_json["name_es"]

    ret = __update_category(category, c_json)

    return ret


def __create_category_metadata(data, category, lang):
    metadata = CategoryMetadata()
    metadata.category = category
    metadata.language = lang
    m = __update_category_metadata(data, metadata)

    return m


def __update_category_metadata(data, metadata):
    name_key = "name_%s" % metadata.language.code
    metadata.name = data[name_key]
    metadata.save()

    return metadata


def import_category(file):
    with open(file) as f:
        buf = f.read()
    f.close()

    json_list = json.loads(buf)

    languages = []

    for c_json in json_list:
        if "name_es" in c_json:
            lang = __get_language("es")
            languages.append(lang)
        if "name_pt" in c_json:
            lang = __get_language("pt")
            languages.append(lang)

        try:
            category = Category.objects.get(original_name=c_json["name_es"])
            c = __update_category(category, c_json)
        except ObjectDoesNotExist:
            c = __create_category(c_json)

        for lang in languages:
            try:
                met = CategoryMetadata.objects.get(category=c, language=lang)
                __update_category_metadata(c_json, met)
            except:
                __create_category_metadata(c_json, c, lang)


"""
IMPORTACION DE GIRLS
"""

def __update_girl(girl, g_json, up_img=False):
    if up_img:
        a = girl.asset

        try:
            i = Image.objects.get(name=a.asset_id)
        except ObjectDoesNotExist:
            i = Image()
        i.name = a.asset_id
        i.portrait = g_json["image_portrait"]
        i.save()

        girl.image = i

    girl.name = g_json["name"]
    girl.type = g_json["tipo"]
    if g_json["birth_date"] != '':
        girl.birth_date = g_json["birth_date"]
    girl.save()

    return girl


def __create_girl(g_json, up_img):
    asset = Asset()
    asset.asset_type = "girl"
    asset.save()

    girl = Girl()
    girl.asset = asset
    ret = __update_girl(girl, g_json, up_img)

    return ret


def __create_girl_metadata(data, girl, lang):
    metadata = GirlMetadata()
    metadata.girl = girl
    metadata.language = lang
    m = __update_girl_metadata(data, metadata)

    return m


def __update_girl_metadata(data, metadata):
    metadata.description = data["summary_long"]
    metadata.nationality = data["nationality"]
    metadata.save()

    return metadata


def import_girl(file, up_img=False):
    with open(file) as f:
        buf = f.read()
    f.close()

    json_list = json.loads(buf)

    for g_json in json_list:
        # Verifico que el lenguage exista
        lang = __get_language(g_json["Idioma"])

        try:
            girl = Girl.objects.get(name=g_json["name"])
            print "Actualizando chica: %s" % g_json["name"]
            g = __update_girl(girl, g_json, up_img)
        except ObjectDoesNotExist:
            print "Creando chica: %s" % g_json["name"]
            g = __create_girl(g_json, True)

        try:
            met = GirlMetadata.objects.get(girl=g, language=lang)
            __update_girl_metadata(g_json, met)
        except ObjectDoesNotExist:
            __create_girl_metadata(g_json, g, lang)


"""
IMPORTACION DE SERIES
"""

def __update_serie(serie, s_json, up_img):
    # Verifico que el canal exista
    if "channel" in s_json:
        channel = __get_channel(s_json["channel"])
    else:
        channel = None

    # Verifico que las chicas existan
    girls = __get_girls(s_json["girls"])

    # Verifico que las categorias existan
    if "category" in s_json:
        categories = __get_categories(s_json["category"])
    else:
        categories = []

    if up_img:
        a = serie.asset

        try:
            i = Image.objects.get(name=a.asset_id)
        except ObjectDoesNotExist:
            i = Image()
        i.name = a.asset_id
        i.landscape = s_json["image_lanscape"]
        i.save()

        serie.image = i

    serie.original_title = s_json["original_title"]
    if channel is not None:
        serie.channel = channel
    if "year" in s_json:
        serie.year = int(s_json["year"])
    if "cast" in s_json:
        serie.cast = s_json["cast"]
    if "directors" in s_json:
        serie.directors = s_json["directors"]
    serie.save()

    for girl in girls:
        serie.girls.add(girl)

    for category in categories:
        serie.category.add(category)

    return serie


def __create_serie(s_json, up_img):
    asset = Asset()
    asset.asset_type = "serie"
    asset.save()

    serie = Serie()
    serie.asset = asset
    ret = __update_serie(serie, s_json, up_img)

    return ret


def __create_serie_metadata(data, serie, lang):
    metadata = SerieMetadata()
    metadata.serie = serie
    metadata.language = lang
    m = __update_serie_metadata(data, metadata)

    return m


def __update_serie_metadata(data, metadata):
    metadata.title = data["title"]
    metadata.summary_long = data["summary_long"].replace("<p>", "").replace("</p>", "").rstrip()
    metadata.save()

    return metadata


def import_serie(file, up_img=False):
    with open(file) as f:
        buf = f.read()
    f.close()

    json_list = json.loads(buf)

    for s_json in json_list:
        # Verifico que el lenguage exista
        lang = __get_language(s_json["language"])

        try:
            serie = Serie.objects.get(original_title=s_json["original_title"])
            print "Actualizando serie: %s" % s_json["original_title"]
            s = __update_serie(serie, s_json, up_img)
        except ObjectDoesNotExist:
            print "Creando serie: %s" % s_json["original_title"]
            s = __create_serie(s_json, True)

        try:
            met = SerieMetadata.objects.get(serie=s, language=lang)
            __update_serie_metadata(s_json, met)
        except ObjectDoesNotExist:
            __create_serie_metadata(s_json, s, lang)


"""
IMPORTACION DE EPISODE
"""

def __update_episode(episode, e_json, up_img):
    # Verifico que el canal exista
    if "channel" in e_json:
        channel = __get_channel(e_json["channel"])
    else:
        channel = None

    # Verifico que las chicas existan
    girls = __get_girls(e_json["girls"])

    # Verifico que las categorias existan
    if "category" in e_json:
        categories = __get_categories(e_json["category"])
    else:
        categories = []

    if up_img:
        a = episode.asset

        try:
            i = Image.objects.get(name=a.asset_id)
        except ObjectDoesNotExist:
            i = Image()
        print "creando imagen"
        i.name = a.asset_id
        i.portrait = e_json["image_portrait"]
        i.landscape = e_json["image_landscape"]
        i.save()
        episode.image = i

    if e_json["serie"] != '':
        try:
            serie = Serie.objects.get(original_title=e_json["serie"])
        except ObjectDoesNotExist:
            msg = "La serie %s no existe" % e_json["serie"]
            raise ImporterException(msg)
    else:
        msg = "La key serie es vacia: %s" % episode.asset.asset_id
        raise ImporterException(msg)

    episode.original_title = e_json["original_title"]
    episode.channel = channel
    episode.year = int(e_json["year"])
    episode.cast = e_json["cast"]
    episode.directors = e_json["directors"]
    episode.runtime = int(e_json["runtime"])
    episode.display_runtime = str(datetime.timedelta(seconds=episode.runtime))[:4]
    #episode.thumbnails = check_thumbnail(a.asset_id)
    if e_json["chapter"] != '':
        episode.chapter = int(e_json["chapter"])
    if e_json["season"] != '':
        episode.season  = int(e_json["season"])
    episode.serie = serie
    episode.save()

    for girl in girls:
        episode.girls.add(girl)

    for category in categories:
        episode.category.add(category)

    return episode


def __create_episode(e_json, up_img):
    asset = Asset()
    asset.asset_id = e_json["asset_id"]
    asset.asset_type = "episode"
    asset.save()

    episode = Episode()
    episode.asset = asset
    ret = __update_episode(episode, e_json, up_img)

    return ret


def __create_episode_metadata(data, episode, lang):
    metadata = EpisodeMetadata()
    metadata.episode = episode
    metadata.language = lang
    m = __update_episode_metadata(data, metadata, lang)

    return m


def __update_episode_metadata(data, metadata, lang):
    metadata.title = data["title01"]
    metadata.summary_short = data["summary_short"].replace("<p>", "").replace("</p>", "").rstrip()
    metadata.summary_long = data["summary_long"].replace("<p>", "").replace("</p>", "").rstrip()
    #metadata.subtitle = check_subtitle(metadata.episode.asset.asset_id, lang.code)
    metadata.save()

    return metadata


def import_episode(file, up_img=False):
    with open(file) as f:
        buf = f.read()
    f.close()

    json_list = json.loads(buf)

    for e_json in json_list:
        print "asset_id: %s" % e_json["asset_id"]
        # Verifico que el lenguage exista
        lang = __get_language(e_json["idioma"])

        # Verifico que el json tenga runtime
        if e_json["runtime"] == '':
            print "El asset %s no tiene runtime" % e_json["asset_id"]
            continue

        try:
            asset = Asset.objects.get(asset_id=e_json["asset_id"])
            try:
                episode = Episode.objects.get(asset=asset)
            except ObjectDoesNotExist:
                msg = "No existe una episodio asociado al asset ID %s" % e_json["asset_id"]
                raise ImporterException(msg)
            try:
                ep = __update_episode(episode, e_json, up_img)
            except ImporterException as err:
                print err.value
                continue
        except ObjectDoesNotExist:
            try:
                ep = __create_episode(e_json, True)
            except ImporterException as err:
                print err.value
                continue

        try:
            met = EpisodeMetadata.objects.get(episode=ep, language=lang)
            try:
                __update_episode_metadata(e_json, met, lang)
            except ImporterException as err:
                print err.value
                continue
        except ObjectDoesNotExist:
            try:
                __create_episode_metadata(e_json, ep, lang)
            except ImporterException as err:
                print err.value
                continue



"""
IMPORTACION DE MOVIES
"""

def __update_movie(movie, m_json, up_img):
    # Verifico que el canal exista
    if "channel" in m_json:
        channel = __get_channel(m_json["channel"])
    else:
        channel = None

    # Verifico que las chicas existan
    girls = __get_girls(m_json["girls"])

    # Verifico que las categorias existan
    if "category" in m_json:
        categories = __get_categories(m_json["category"])
    else:
        categories = []

    if up_img:
        a = movie.asset
        try:
            i = Image.objects.get(name=a.asset_id)
        except ObjectDoesNotExist:
            i = Image()
        i.name = a.asset_id
        i.portrait = m_json["image_portrait"]
        i.landscape = m_json["image_landscape"]
        i.save()
        movie.image = i

    movie.original_title = m_json["original_title"]
    movie.channel = channel
    movie.year = int(m_json["year"])
    movie.cast = m_json["cast"]
    movie.directors = m_json["directors"]
    movie.runtime = int(m_json["runtime"])
    movie.display_runtime = str(datetime.timedelta(seconds=movie.runtime))[:4]
    #movie.thumbnails = check_thumbnail(a.asset_id)
    movie.save()

    for girl in girls:
        movie.girls.add(girl)

    for category in categories:
        movie.category.add(category)

    return movie


def __create_movie(m_json, up_img):
    asset = Asset()
    asset.asset_id = m_json["asset_id"]
    asset.asset_type = "movie"
    asset.save()

    movie = Movie()
    movie.asset = asset
    ret = __update_movie(movie, m_json, up_img)

    return ret


def __create_movie_metadata(data, movie, lang):
    metadata = MovieMetadata()
    metadata.movie = movie
    metadata.language = lang
    m = __update_movie_metadata(data, metadata, lang)

    return m


def __update_movie_metadata(data, metadata, lang):
    metadata.title = data["title01"]
    metadata.summary_short = data["summary_short"].replace("<p>", "").replace("</p>", "").rstrip()
    metadata.summary_long = data["summary_long"].replace("<p>", "").replace("</p>", "").rstrip()
    #metadata.subtitle = check_subtitle(metadata.movie.asset.asset_id, lang.code)
    metadata.save()

    return metadata


def import_movie(file, up_img=False):
    with open(file) as f:
        buf = f.read()
    f.close()

    json_list = json.loads(buf)

    for m_json in json_list:
        print "asset_id: %s" % m_json["asset_id"]
        # Verifico que el lenguage exista
        lang = __get_language(m_json["idioma"])

        # Verifico que el json tenga runtime
        if m_json["runtime"] == '':
            print "El asset %s no tiene runtime" % m_json["asset_id"]
            continue

        try:
            asset = Asset.objects.get(asset_id=m_json["asset_id"])
            try:
                movie = Movie.objects.get(asset=asset)
            except ObjectDoesNotExist:
                msg = "No existe una movie asociada al asset ID %s" % m_json["asset_id"]
                raise ImporterException(msg)
            try:
                image = Image.objects.get(name=asset.asset_id)
                if str(image.portrait).startswith("http://"):
                    mov = __update_movie(movie, m_json, True)
                    print "Imagen actualizada"
                elif str(image.landscape).startswith("http://"):
                    mov = __update_movie(movie, m_json, True)
                    print "Imagen actualizada"
                else:
                    mov = __update_movie(movie, m_json, up_img)
            except ImporterException as err:
                print err.value
                continue
        except ObjectDoesNotExist:
            #try:
            mov = __create_movie(m_json, True)
            #except ImporterException as err:
                #print str(err.value)
                #continue

        try:
            met = MovieMetadata.objects.get(movie=mov, language=lang)
            try:
                __update_movie_metadata(m_json, met, lang)
            except ImporterException as err:
                print err.value
                continue
        except ObjectDoesNotExist:
            try:
                __create_movie_metadata(m_json, mov, lang)
            except ImporterException as err:
                print err.value
                continue


def enqueue_girl(girl, pzone, language=''):
    try:
        publish_zone = PublishZone.objects.get(name=pzone)
    except ObjectDoesNotExist:
        msg = "Publish Zone %s does not exist" % pzone
        raise EnqueuerException(msg)

    if language == '':
        metadata_list = GirlMetadata.objects.filter(girl=girl)
        for metadata in metadata_list:
            enqueue_item(girl.asset.asset_id, metadata.language, 'AS', publish_zone)
    else:
        # Verifico que el lenguage exista
        try:
            lang = __get_language(language)
        except ImporterException as e:
            raise EnqueuerException(e.value)
        try:
            GirlMetadata.objects.get(girl=girl, language=lang)
        except ObjectDoesNotExist:
            msg = "Metadata in %s does not exist for girl %s" % (language, girl.name)
            raise EnqueuerException(msg)
        enqueue_item(girl.asset.asset_id, lang, 'AS', publish_zone)


def enqueue_movie(movie, pzone, language=''):
    try:
        publish_zone = PublishZone.objects.get(name=pzone)
    except ObjectDoesNotExist:
        msg = "Publish Zone %s does not exist" % pzone
        raise EnqueuerException(msg)

    if language == '':
        metadata_list = MovieMetadata.objects.filter(movie=movie)
        for metadata in metadata_list:
            enqueue_item(movie.asset.asset_id, metadata.language, 'AS', publish_zone)
    else:
        # Verifico que el lenguage exista
        try:
            lang = __get_language(language)
        except ImporterException as e:
            raise EnqueuerException(e.value)
        try:
            MovieMetadata.objects.get(movie=movie, language=lang)
        except ObjectDoesNotExist:
            msg = "Metadata in %s does not exist for movie %s" % (language, movie.asset.asset_id)
            raise EnqueuerException(msg)
        enqueue_item(movie.asset.asset_id, lang, 'AS', publish_zone)


def enqueue_serie(serie, pzone, language=''):
    try:
        publish_zone = PublishZone.objects.get(name=pzone)
    except ObjectDoesNotExist:
        msg = "Publish Zone %s does not exist" % pzone
        raise EnqueuerException(msg)

    if language == '':
        metadata_list = SerieMetadata.objects.filter(serie=serie)
        for metadata in metadata_list:
            enqueue_item(serie.asset.asset_id, metadata.language, 'AS', publish_zone)
    else:
        # Verifico que el lenguage exista
        try:
            lang = __get_language(language)
        except ImporterException as e:
            raise EnqueuerException(e.value)
        try:
            SerieMetadata.objects.get(serie=serie, language=lang)
        except ObjectDoesNotExist:
            msg = "Metadata in %s does not exist for serie %s" % (language, serie.asset.asset_id)
            raise EnqueuerException(msg)
        enqueue_item(serie.asset.asset_id, lang, 'AS', publish_zone)


def enqueue_episode(episode, pzone, language=''):
    try:
        publish_zone = PublishZone.objects.get(name=pzone)
    except ObjectDoesNotExist:
        msg = "Publish Zone %s does not exist" % pzone
        raise EnqueuerException(msg)

    if language == '':
        metadata_list = EpisodeMetadata.objects.filter(episode=episode)
        for metadata in metadata_list:
            enqueue_item(episode.asset.asset_id, metadata.language, 'AS', publish_zone)
    else:
        # Verifico que el lenguage exista
        try:
            lang = __get_language(language)
        except ImporterException as e:
            raise EnqueuerException(e.value)
        try:
            EpisodeMetadata.objects.get(episode=episode, language=lang)
        except ObjectDoesNotExist:
            msg = "Metadata in %s does not exist for episode %s" % (language, episode.asset.asset_id)
            raise EnqueuerException(msg)
        enqueue_item(episode.asset.asset_id, lang, 'AS', publish_zone)


def enqueue_category(category, pzone, language=''):
    try:
        publish_zone = PublishZone.objects.get(name=pzone)
    except ObjectDoesNotExist:
        msg = "Publish Zone %s does not exist" % pzone
        raise EnqueuerException(msg)

    if language == '':
        metadata_list = CategoryMetadata.objects.filter(category=category)
        for metadata in metadata_list:
            enqueue_item(category.category_id, metadata.language, 'CA', publish_zone)
    else:
        # Verifico que el lenguage exista
        try:
            lang = __get_language(language)
        except ImporterException as e:
            raise EnqueuerException(e.value)
        try:
            CategoryMetadata.objects.get(category=category, language=lang)
        except ObjectDoesNotExist:
            msg = "Metadata in %s does not exist for category ID %s" % (language, category.category_id)
            raise EnqueuerException(msg)
        enqueue_item(category.category_id, lang, 'CA', publish_zone)


def enqueue_slider(slider, pzone):
    try:
        publish_zone = PublishZone.objects.get(name=pzone)
    except ObjectDoesNotExist:
        msg = "Publish Zone %s does not exist" % pzone
        raise EnqueuerException(msg)

    enqueue_item(slider.slider_id, slider.language, 'SL', publish_zone)


def enqueue_asset(asset, pzone, language=''):
    if asset.asset_type == "movie":
        movie = Movie.objects.get(asset=asset)
        enqueue_movie(movie, pzone, language)
    elif asset.asset_type == "episode":
        episode = Episode.objects.get(asset=asset)
        enqueue_episode(episode, pzone, language)
    elif asset.asset_type == "serie":
        serie = Serie.objects.get(asset=asset)
        enqueue_serie(serie, pzone, language)
    elif asset.asset_type == "girl":
        girl = Girl.objects.get(asset=asset)
        enqueue_girl(girl, pzone, language)


def enqueue_block(block, pzone):
    try:
        publish_zone = PublishZone.objects.get(name=pzone)
    except ObjectDoesNotExist:
        msg = "Publish Zone %s does not exist" % pzone
        raise EnqueuerException(msg)

    for asset in block.assets.all():
        if asset.asset_type != 'episode':
            try:
                enqueue_asset(asset, pzone, block.language.code)
            except:
                print asset.asset_id
                pass
        else:
            print asset.asset_id
    enqueue_item(block.block_id, block.language, 'BL', publish_zone)


def enqueue_item(id, lang, type, publish_zone):
    q = PublishQueue()
    q.item_id = id
    q.item_lang = lang
    q.item_type = type
    q.publish_zone = publish_zone
    q.schedule_date = timezone.now()
    q.save()


def enqueue_image(image):
    p_zones = PublishZone.objects.filter(enabled=True)
    for zone in p_zones:
        q = ImageQueue()
        q.image = image
        q.publish_zone = zone
        q.schedule_date = timezone.now()
        q.save()


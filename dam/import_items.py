import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dam.settings")
django.setup()
from django.core.exceptions import *
from cawas.models import *
from django.utils import timezone


import json
import datetime

from urlparse import urlparse
import httplib2


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


def chech_subtitle(asset_id, lang):
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
    girl.type = g_json["type"]
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
        lang = __get_language(g_json["language"])

        try:
            girl = Girl.objects.get(name=g_json["name"])
            g = __update_girl(girl, g_json, up_img)
        except ObjectDoesNotExist:
            g = __create_girl(g_json, up_img)

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
            s = __update_serie(serie, s_json, up_img)
        except ObjectDoesNotExist:
            s = __create_serie(s_json, up_img)

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
        i.name = a.asset_id
        i.portrait = e_json["image_portrait"]
        i.landscape = e_json["image_big"]
        i.save()
        episode.image = i

    if e_json["serie"] != '':
        try:
            serie = Serie.objects.get(original_title=e_json["serie"])
        except ObjectDoesNotExist:
            msg = "La serie %s no existe" % e_json["serie"]
            raise ImporterException(msg)
    else:
        msg = "La key serie es vacia"
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
    metadata.title = data["title"]
    metadata.summary_short = data["summary_short"].replace("<p>", "").replace("</p>", "").rstrip()
    metadata.summary_long = data["summary_long"].replace("<p>", "").replace("</p>", "").rstrip()
    #metadata.subtitle = chech_subtitle(metadata.episode.asset.asset_id, lang.code)
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
        lang = __get_language(e_json["language"])

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
                ep = __create_episode(e_json, up_img)
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
        i.landscape = m_json["image_big"]
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
    metadata.title = data["title"]
    metadata.summary_short = data["summary_short"].replace("<p>", "").replace("</p>", "").rstrip()
    metadata.summary_long = data["summary_long"].replace("<p>", "").replace("</p>", "").rstrip()
    #metadata.subtitle = chech_subtitle(metadata.movie.asset.asset_id, lang.code)
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
        lang = __get_language(m_json["language"])

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
                mov = __update_movie(movie, m_json, up_img)
            except ImporterException as err:
                print err.value
                continue
        except ObjectDoesNotExist:
            try:
                mov = __create_movie(m_json, up_img)
            except ImporterException as err:
                print err.value
                continue

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


def enqueue_slider(slider, pzone, language=''):
    try:
        publish_zone = PublishZone.objects.get(name=pzone)
    except ObjectDoesNotExist:
        msg = "Publish Zone %s does not exist" % pzone
        raise EnqueuerException(msg)

    if language == '':
        metadata_list = SliderMetadata.objects.filter(slider=slider)
        for metadata in metadata_list:
            enqueue_item(slider.slider_id, metadata.language, 'SL', publish_zone)
    else:
        # Verifico que el lenguage exista
        try:
            lang = __get_language(language)
        except ImporterException as e:
            raise EnqueuerException(e.value)
        try:
            SliderMetadata.objects.get(slider=slider, language=lang)
        except ObjectDoesNotExist:
            msg = "Metadata in %s does not exist for slider ID %s" % (language, slider.slider_id)
            raise EnqueuerException(msg)
        enqueue_item(slider.slider_id, lang, 'SL', publish_zone)


def enqueue_block(block, pzone):
    try:
        publish_zone = PublishZone.objects.get(name=pzone)
    except ObjectDoesNotExist:
        msg = "Publish Zone %s does not exist" % pzone
        raise EnqueuerException(msg)
    enqueue_item(block.block_id, block.language, 'BL', publish_zone)


def enqueue_item(id, lang, type, publish_zone):
    q = PublishQueue()
    q.item_id = id
    q.item_lang = lang
    q.item_type = type
    q.publish_zone = publish_zone
    q.schedule_date = timezone.now()
    q.save()

"""
try:
    import_girl('girl.json.es')
    import_girl('girl.json.pt')
except ImporterException as err:
    print err.value
"""
"""
try:
    import_category('category.json')
except ImporterException as err:
    print err.value
"""
"""
try:
    import_serie('serie.json.es')
    import_serie('serie.json.pt')
except ImporterException as err:
    print err.value
"""
"""
try:
    import_movie('movie.json.es')
    import_movie('movie.json.pt')
except ImporterException as err:
    print err.value
"""
"""
try:
    import_episode('episode.json.es')
    import_episode('episode.json.pt')
except ImporterException as err:
    print err.value
"""

"""
girls_list = Girl.objects.all()
for girl in girls_list:
    try:
        enqueue_girl(girl, ENDPOINT,'es')
        #enqueue_girl(girl)
    except EnqueuerException as err:
        print err.value
"""
"""
movies_list = Movie.objects.all()
for movie in movies_list:
    try:
        enqueue_movie(movie, ENDPOINT, 'es')
        #enqueue_movie(movie)
    except EnqueuerException as err:
        print err.value
"""

serie_list = Serie.objects.all()
for serie in serie_list:
    try:
        enqueue_serie(serie, "Virginia", 'es')
        #enqueue_serie(serie)
    except EnqueuerException as err:
        print err.value

"""
episode_list = Episode.objects.all()
for episode in episode_list:
    try:
        enqueue_episode(episode, ENDPOINT, 'es')
        #enqueue_episode(episode, ENDPOINT)
    except EnqueuerException as err:
        print err.value
"""

"""
category_list = Category.objects.all()
for category in category_list:
    try:
        enqueue_category(category, ENDPOINT, 'es')
        #enqueue_category(category)
    except EnqueuerException as err:
        print err.value
"""
"""
slider_list = Slider.objects.all()
for slider in slider_list:
    try:
        enqueue_slider(slider, ENDPOINT, 'es')
        #enqueue_slider(slider)
    except EnqueuerException as err:
        print err.value
"""
"""
block_list = Block.objects.all()
for block in block_list:
    try:
        enqueue_block(block, ENDPOINT)
    except EnqueuerException as err:
        print err.value
"""

"""
for item in PublishQueue.objects.filter(status='E'):
    item.status  = 'Q'
    item.message = ''
    item.save()
"""
"""
for item in PublishQueue.objects.all():
    item.status  = 'Q'
    item.message = ''
    item.save()
"""

#q = Movie.objects.filter(year=0).annotate(Count('runtime'))
#print q.runtime__count
#print Movie.objects.filter(year=0).distinct('original_title')
#print Movie.objects.filter(year=0).values_list('runtime', flat=True).distinct().count()
#movies = Movie.objects.filter(year=0)


#asset = Asset.obje
#girl = Girl.objects.get(asset=)

"""
images = Image.objects.all()
for image in images:
    if image.portrait:
        image.portrait  = "%s.jpg" % image.name
    if image.landscape:
        image.landscape = "%s.jpg" % image.name
    image.save()
"""


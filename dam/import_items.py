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


ENDPOINT = "http://backend.zolechamedia.net"

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


def import_girl(file):
    with open(file) as f:
        buf = f.read()
    f.close()

    girl_list = json.loads(buf)

    for girl in girl_list:
        try:
            g = Girl.objects.get(name=girl["name"])
        except ObjectDoesNotExist:
            a            = Asset()
            a.asset_type = "girl"
            a.save()

            i          = Image()
            i.name     = a.asset_id
            i.portrait = girl["image_portrait"]
            i.save()

            g            = Girl()
            g.asset      = a
            g.name       = girl["name"]
            g.type       = girl["type"]
            g.image      = i
            if girl["birth_date"] != '':
                g.birth_date = girl["birth_date"]
            g.save()

        m             = GirlMetadata()
        m.girl        = g
        lang = Language.objects.get(code=girl["lang"])
        m.language    = lang
        m.description = girl["summary_long"].replace("<p>", "").replace("</p>", "").rstrip()
        m.nationality = girl["nationality"]
        m.save()


def import_category(file):
    with open(file) as f:
        buf = f.read()
    f.close()

    category_list = json.loads(buf)

    for category in category_list:
        try:
            i = Image.objects.get(name=category["name_es"])
        except ObjectDoesNotExist:
            i          = Image()
            i.name     = category["name_es"]
            i.portrait = category["image_portrait"]
            i.save()

        cat = Category()
        cat.original_name = category["name_es"]
        cat.image = i
        cat.save()

        languages = Language.objects.all()
        for lang in languages:
            key = "name_%s" % lang.code
            metadata          = CategoryMetadata()
            metadata.category = cat
            lang              = Language.objects.get(code=lang.code)
            metadata.language = lang
            metadata.name     = category[key]
            metadata.save()


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
IMPORTACION DE SERIES
"""

def __update_serie(serie, s_json):
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


def __create_serie(s_json):
    asset = Asset()
    asset.asset_type = "serie"
    asset.save()

    serie = Serie()
    serie.asset = asset
    ret = __update_serie(serie, s_json)

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


def import_serie(file):
    with open(file) as f:
        buf = f.read()
    f.close()

    json_list = json.loads(buf)

    for s_json in json_list:
        # Verifico que el lenguage exista
        lang = __get_language(s_json["language"])

        try:
            serie = Serie.objects.get(original_title=s_json["original_title"])
            s = __update_serie(serie, s_json)
        except ObjectDoesNotExist:
            s = __create_serie(s_json)

        try:
            met = SerieMetadata.objects.get(serie=s, language=lang)
            __update_serie_metadata(s_json, met)
        except ObjectDoesNotExist:
            __create_serie_metadata(s_json, s, lang)


"""
IMPORTACION DE EPISODE
"""

def __update_episode(episode, e_json):
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

    a = episode.asset

    try:
        i = Image.objects.get(name=a.asset_id)
    except ObjectDoesNotExist:
        i = Image()
    i.name = a.asset_id
    i.portrait = e_json["image_portrait"]
    i.big = e_json["image_big"]
    i.save()

    if e_json["serie"] != '':
        try:
            serie = Serie.objects.get(original_title=e_json["serie"])
        except ObjectDoesNotExist:
            msg = "La serie %s no existe" % ejson["serie"]
            raise ImporterException(msg)
    else:
        msg = "La key serie es vacia"
        raise ImporterException(msg)



    episode.image = i
    episode.original_title = e_json["original_title"]
    episode.channel = channel
    episode.year = int(e_json["year"])
    episode.cast = e_json["cast"]
    episode.directors = e_json["directors"]
    episode.runtime = int(e_json["runtime"])
    episode.display_runtime = str(datetime.timedelta(seconds=episode.runtime))[:4]
    episode.thumbnails = check_thumbnail(a.asset_id)
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


def __create_episode(e_json):
    asset = Asset()
    asset.asset_id = e_json["asset_id"]
    asset.asset_type = "episode"
    asset.save()

    episode = Episode()
    episode.asset = asset
    ret = __update_episode(episode, e_json)

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
    metadata.subtitle = chech_subtitle(metadata.episode.asset.asset_id, lang.code)
    metadata.save()

    return metadata


def import_episode(file):
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
                ep = __update_episode(episode, e_json)
            except ImporterException as err:
                print err.value
                continue
        except ObjectDoesNotExist:
            try:
                ep = __create_episode(e_json)
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

def __update_movie(movie, m_json):
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

    a = movie.asset

    try:
        i = Image.objects.get(name=a.asset_id)
    except ObjectDoesNotExist:
        i = Image()
    i.name = a.asset_id
    i.portrait = m_json["image_portrait"]
    i.big = m_json["image_big"]
    i.save()

    movie.image = i
    movie.original_title = m_json["original_title"]
    movie.channel = channel
    movie.year = int(m_json["year"])
    movie.cast = m_json["cast"]
    movie.directors = m_json["directors"]
    movie.runtime = int(m_json["runtime"])
    movie.display_runtime = str(datetime.timedelta(seconds=movie.runtime))[:4]
    movie.thumbnails = check_thumbnail(a.asset_id)
    movie.save()

    for girl in girls:
        movie.girls.add(girl)

    for category in categories:
        movie.category.add(category)

    return movie


def __create_movie(m_json):
    asset = Asset()
    asset.asset_id = m_json["asset_id"]
    asset.asset_type = "movie"
    asset.save()

    movie = Movie()
    movie.asset = asset
    ret = __update_movie(movie, m_json)

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
    metadata.subtitle = chech_subtitle(metadata.movie.asset.asset_id, lang.code)
    metadata.save()

    return metadata


def import_movie(file):
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
                mov = __update_movie(movie, m_json)
            except ImporterException as err:
                print err.value
                continue
        except ObjectDoesNotExist:
            try:
                mov = __create_movie(m_json)
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


def enqueue_girl(girl, lang=''):
    if lang == '':
        metadata_list = GirlMetadata.objects.filter(girl=girl)
        for metadata in metadata_list:
            q = PublishQueue()
            q.item_id       = girl.asset.asset_id
            print metadata.language.code
            q.item_lang     = metadata.language
            q.item_type     = 'AS'
            q.endpoint      = ENDPOINT
            q.schedule_date = timezone.now()
            q.save()
    else:
        try:
            GirlMetadata.objects.get(girl=girl, language=lang)
        except ObjectDoesNotExist:
            msg = "Metadata in %s does not exist for girl %s" % (lang, girl.name)
            raise EnqueuerException(msg)
        q = PublishQueue()
        q.item_id = girl.asset.asset_id
        q.item_lang = lang
        q.item_type = 'AS'
        q.endpoint = ENDPOINT
        q.schedule_date = timezone.now()
        q.save()


def enqueue_movie(movie, lang=''):
    if lang == '':
        metadata_list = MovieMetadata.objects.filter(movie=movie)
        for metadata in metadata_list:
            q = PublishQueue()
            q.item_id = movie.asset.asset_id
            q.item_lang = metadata.language
            q.item_type = 'AS'
            q.endpoint = ENDPOINT
            q.schedule_date = timezone.now()
            q.save()
    else:
        try:
            MovieMetadata.objects.get(movie=movie, language=lang)
        except ObjectDoesNotExist:
            msg = "Metadata in %s does not exist for movie %s" % (lang, movie.asset.asset_id)
            raise EnqueuerException(msg)
        q = PublishQueue()
        q.item_id = movie.asset.asset_id
        q.item_lang = lang
        q.item_type = 'AS'
        q.endpoint = ENDPOINT
        q.schedule_date = timezone.now()
        q.save()


def enqueue_serie(serie, lang=''):
    if lang == '':
        metadata_list = SerieMetadata.objects.filter(serie=serie)
        for metadata in metadata_list:
            q = PublishQueue()
            q.item_id = serie.asset.asset_id
            q.item_lang = metadata.language
            q.item_type = 'AS'
            q.endpoint = ENDPOINT
            q.schedule_date = timezone.now()
            q.save()
    else:
        try:
            SerieMetadata.objects.get(serie=movie, language=lang)
        except ObjectDoesNotExist:
            msg = "Metadata in %s does not exist for serie %s" % (lang, serie.asset.asset_id)
            raise EnqueuerException(msg)
        q = PublishQueue()
        q.item_id = serie.asset.asset_id
        q.item_lang = lang
        q.item_type = 'AS'
        q.endpoint = ENDPOINT
        q.schedule_date = timezone.now()
        q.save()


#import_girl('girl.json.pt')
#import_category('category.json')
#import_serie('serie.json.es')
"""
try:
    import_movie('movie.json')
except ImporterException as err:
    print err.value
"""
"""
try:
    import_episode('episode.json.es')
except ImporterException as err:
    print err.value
"""

"""
try:
    import_movie('movie.json')
except ImporterException as e:
    print e.value
"""
"""
girls_list = Girl.objects.all()
for girl in girls_list:
    try:
        #enqueue_girl(girl, 'pt')
        #enqueue_girl(girl)
    except EnqueuerException as err:
        print err.value
"""
"""
movies_list = Movie.objects.all()
for movie in movies_list:
    try:
        #enqueue_movie(movie 'pt')
        enqueue_movie(movie)
    except EnqueuerException as err:
        print err.value
"""
"""
serie_list = Serie.objects.all()
for serie in serie_list:
    try:
        #enqueue_movie(movie 'pt')
        enqueue_serie(serie)
    except EnqueuerException as err:
        print err.value
"""

#q = Movie.objects.filter(year=0).annotate(Count('runtime'))
#print q.runtime__count
#print Movie.objects.filter(year=0).distinct('original_title')
#print Movie.objects.filter(year=0).values_list('runtime', flat=True).distinct().count()
#movies = Movie.objects.filter(year=0)


#asset = Asset.obje
#girl = Girl.objects.get(asset=)



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
            i.name     = girl["name"]
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


def import_movie(file):
    with open(file) as f:
        buf = f.read()
    f.close()

    movie_list = json.loads(buf)

    for movie in movie_list:
        # Verifico que el lenguage exista
        try:
            lang = Language.objects.get(code=movie["language"])
        except ObjectDoesNotExist:
            msg = "Lenguage %s no existe" % movie["language"]
            #print msg
            raise ImporterException(msg)

        # Verifico que el canal exista
        try:
            channel = Channel.objects.get(name=movie["channel"])
        except ObjectDoesNotExist:
            msg = "El Canal %s no existe" % movie["channel"]
            #print msg
            raise ImporterException(msg)

        # Verifico que las chicas existan
        girls  = []
        if movie["girls"] != '':
            g_list = movie["girls"].split(",")
        else:
            g_list = []

        for girl in g_list:
            try:
                girl = Girl.objects.get(name=girl)
                girls.append(girl)
            except ObjectDoesNotExist:
                msg = "La chica %s no existe" % girl
                #print msg
                raise ImporterException(msg)

        # Verifico que las categorias existan
        categories = []
        if movie["category"] != '':
            cat_list = movie["category"].split(",")
        else:
            cat_list = []

        for category in cat_list:
            try:
                cat = Category.objects.get(original_name=category)
                categories.append(cat)
            except ObjectDoesNotExist:
                msg = "La Categoria %s no existe" % category
                # print msg
                raise ImporterException(msg)

        try:
            asset = Asset.objects.get(asset_id=movie["asset_id"])
            try:
                m = Movie.objects.get(asset=asset)
            except ObjectDoesNotExist:
                msg = "No existe una movie asociada al asset ID %s" % movie["asset_id"]
                raise ImporterException(msg)
        except ObjectDoesNotExist:
            a = Asset()
            a.asset_id = movie["asset_id"]
            a.asset_type = "movie"
            a.save()

            try:
                i = Image.objects.get(name=movie["asset_id"])
            except ObjectDoesNotExist:
                i          = Image()
                i.name     = movie["asset_id"]
                i.portrait = movie["image_portrait"]
                i.big      = movie["image_big"]
                i.save()

            m                 = Movie()
            m.asset           = a
            m.image           = i
            m.original_title  = movie["original_title"]
            m.channel         = channel
            m.year            = int(movie["year"])
            m.cast            = movie["cast"]
            m.directors       = movie["directors"]
            m.runtime         = int(movie["runtime"])
            m.display_runtime = str(datetime.timedelta(seconds=m.runtime))[:4]
            m.thumbnails      = check_thumbnail(a.asset_id)
            m.save()

            for girl in girls:
                m.girls.add(girl)

            for category in categories:
                #print category.
                m.category.add(category)
        try:
            metadata = MovieMetadata.objects.get(movie=m, language=lang)
        except ObjectDoesNotExist:
            metadata = MovieMetadata()
            metadata.movie = m
            metadata.language = lang
            metadata.title = movie["title"]
            metadata.summary_short = movie["summary_short"].replace("<p>", "").replace("</p>", "").rstrip()
            metadata.summary_long = movie["summary_long"].replace("<p>", "").replace("</p>", "").rstrip()
            metadata.subtitle = chech_subtitle(m.asset.asset_id, lang.code)
            metadata.save()


def enqueue_girl(girl, lang = ''):
    if lang == '':
        metadata_list = GirlMetadata.objects.filter(girl=girl)
        for metadata in metadata_list:
            q = PublishQueue()
            q.item_id       = girl.asset.asset_id
            print metadata.language.code
            q.item_lang     = metadata.language
            q.item_type     = 'AS'
            q.endpoint      = "http://www.zolechamedia.net:8000"
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
        q.endpoint = "http://www.zolechamedia.net:8000"
        q.schedule_date = timezone.now()
        q.save()



#import_girl('girl.json.pt')
#import_category('category.json')
try:
    import_movie('movie.json.short')
except ImporterException as e:
    print e.value
"""
girls_list = Girl.objects.all()
for girl in girls_list:
    try:
        #enqueue_girl(girl, 'pt')
        #enqueue_girl(girl)
    except EnqueuerException as err:
        print err.value
"""
#asset = Asset.obje
#girl = Girl.objects.get(asset=)



import django
import os
from django.core.exceptions import *
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dam.settings")
django.setup()
from cawas.models import *
from datetime import datetime


class SerializerException(Exception):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)


def block_serializer(block_name):
    ret = []
    try:
        block = Block.objects.get(name=block_name)
    except ObjectDoesNotExist:
        msg = "Block with name %s does not exist" % block_name
        raise SerializerException(msg)

    ret.append(block.toDict())

    return ret


def category_serializer(cat_name):
    ret = []
    try:
        category = Category.objects.get(name=cat_name)
    except ObjectDoesNotExist:
        msg = "Category with name %s does not exist" % cat_name
        raise SerializerException(msg)

    ret.append(category.toDict())

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


def asset_serializer(asset_id):
    ret = []

    try:
        asset = Asset.objects.get(asset_id=asset_id)
    except ObjectDoesNotExist:
        msg = "Asset with ID %s does not exist" % asset_id
        raise SerializerException(msg)

    if asset.asset_type == "movie":
        asset_list = movie_serializer(asset)
    elif asset.asset_type == "serie":
        asset_list = serie_serializer(asset)
    elif asset.asset_type == "episode":
        asset_list = episode_serializer(asset)
    elif asset.asset_type == "girl":
        asset_list = girl_serializer(asset)
    else:
        msg = "Invalid asset type: %s" % asset.asset_type
        raise SerializerException(msg)

    asset_dict = asset.toDict()

    for ast in asset_list:
        ret.append(dict(ast.items() + asset_dict.items()))

    return ret


def movie_serializer(asset):
    ret = []

    try:
        movie = Movie.objects.get(asset=asset)
    except ObjectDoesNotExist:
        msg = "Movie with asset id %s does not exist" % asset.asset_id
        raise SerializerException(msg)

    movie_dict = movie.toDict()

    metadata_list = MovieMetadata.objects.filter(movie=movie)

    if len(metadata_list) == 0:
        ret.append(movie_dict)
    else:
        for metadata in metadata_list:
            ret.append(dict(movie_dict.items() + metadata.toDict().items()))

    return ret


def serie_serializer(asset):
    ret = []

    try:
        serie = Serie.objects.get(asset=asset)
    except ObjectDoesNotExist:
        msg = "Serie with asset id %s does not exist" % asset.asset_id
        raise SerializerException(msg)

    serie_dict = serie.toDict()

    metadata_list = SerieMetadata.objects.filter(serie=serie)

    if len(metadata_list) == 0:
        ret.append(serie_dict)
    else:
        for metadata in metadata_list:
            ret.append(dict(serie_dict.items() + metadata.toDict().items()))

    return ret


def episode_serializer(asset):
    ret = []

    try:
        episode = Episode.objects.get(asset=asset)
    except ObjectDoesNotExist:
        msg = "Serie with asset id %s does not exist" % asset.asset_id
        raise SerializerException(msg)

    episode_dict = episode.toDict()

    metadata_list = EpisodeMetadata.objects.filter(episode=episode)

    if len(metadata_list) == 0:
        ret.append(episode_dict)
    else:
        for metadata in metadata_list:
            ret.append(dict(episode_dict.items() + metadata.toDict().items()))

    return ret


def girl_serializer(asset):
    ret = []

    try:
        girl = Girl.objects.get(asset=asset)
    except ObjectDoesNotExist:
        msg = "Girl with asset id %s does not exist" % asset.asset_id
        raise SerializerException(msg)

    girl_dict = girl.toDict()

    metadata_list = GirlMetadata.objects.filter(girl=girl)

    if len(metadata_list) == 0:
        ret.append(girl_dict)
    else:
        for metadata in metadata_list:
            ret.append(dict(girl_dict.items() + metadata.toDict().items()))

    return ret




"""
def movie_serializer(movie):
    ret = []

    movie


def asset_serializer(asset):
    ret = []

    asset_dict = asset.toDict()

    if asset.type == 'ep':
        try:
            episode = Episode.objects.get(asset=asset)
        except ObjectDoesNotExist:
            msg = "Episode with house_id %s does not exist" % asset.house_id
            raise SerializerException(msg)
    elif asset.type == 'se':
        try:
            content = Serie.objects.get(asset=asset)
        except ObjectDoesNotExist:
            msg = "Serie with house_id %s does not exist" % asset.house_id
            raise SerializerException(msg)
    elif asset.type == 'mo':
        try:
            content = Movie.objects.get(asset=asset)
        except ObjectDoesNotExist:
            msg = "Movie with house_id %s does not exist" % asset.house_id
            raise SerializerException(msg)
    elif asset.type == 'gi':
        try: content

    asset_dict = dict(asset_dict.items() + content.toDict().items())

    metadata_list = Metadata.objects.filter(asset=asset)

    if len(metadata_list) == 0:
        msg = "Metadata with house_id %s does not exist" % asset.house_id
        raise SerializerException(msg)

    for metadata in metadata_list:
        m = metadata.toDict()
        ret.append(dict(m.items() + asset_dict.items()))

    return ret


def publish_asset(house_id):
    data = []

    try:
        asset = Asset.objects.get(house_id=house_id)
    except ObjectDoesNotExist:
        msg = "Asset with house_id %s does not exist" % house_id
        raise PublisherException(msg) # Excepcion de Publicacion

    try:
        data = asset_serializer(asset)
    except SerializerException as e:
        print e.value

    '''
    for d in data:
        if publicar d ok:
            asset.publish_status = True
            asset.publish_date   = datetime.now()
            asset.save()
            return data
        else:
            raise PublisherException(msg)  # Excepcion de Publicacion
    '''
    return []


def unpublish_asset(house_id):
    try:
        asset = Asset.objects.get(house_id=house_id)
    except ObjectDoesNotExist:
        msg = "Asset with house_id %s does not exist" % house_id
        raise PublisherException(msg)  # Excepcion de Publicacion

    # despublicar data en DynamoFB.
    '''
    if despublicar ok:
        asset.publish_status = False
        asset.save()
    '''



try:
    print asset_to_dict("0024890")
    print asset_to_dict("0024889")
    print asset_to_dict("0052346")
except SerializerException as e:
    print e.value
"""

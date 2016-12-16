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


def slider_serializer(slider_id, lang=''):
    ret = []
    try:
        slider = Slider.objects.get(slider_id=slider_id)
    except:
        msg = "Slider with ID %s does not exist" % slider_id
        raise SerializerException(msg)

    slider_dict = slider.toDict()

    if lang == '':
        metadata_list = SliderMetadata.objects.filter(slider=slider)
    else:
        try:
            language = Language.objects.get(code=lang)
        except ObjectDoesNotExist:
            msg = "Language code %s does not exist for slider ID %s" % (lang, slider_id)
            raise SerializerException(msg)
        metadata_list = SliderMetadata.objects.filter(slider=slider, language=language)

    if len(metadata_list) == 0:
        ret.append(slider_dict)
    else:
        for metadata in metadata_list:
            ret.append(dict(slider_dict.items() + metadata.toDict().items()))

    return ret


def category_serializer(cat_name, lang=''):
    ret = []
    try:
        category = Category.objects.get(name=cat_name)
    except ObjectDoesNotExist:
        msg = "Category with name %s does not exist" % cat_name
        raise SerializerException(msg)

    category_dict = category.toDict()

    if lang == '':
        metadata_list = CategoryMetadata.objects.filter(category=category)
    else:
        try:
            language = Language.objects.get(code=lang)
        except ObjectDoesNotExist:
            msg = "Language code %s does not exist for category %s" % (lang, cat_name)
            raise SerializerException(msg)
        metadata_list = CategoryMetadata.objects.filter(category=category, lang=language)

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


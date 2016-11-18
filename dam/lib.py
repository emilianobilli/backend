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


def asset_serializer(asset):
    ret = []

    asset_dict = asset.toDict()

    if asset.type == 'ep':
        try:
            content = Episode.objects.get(asset=asset)
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
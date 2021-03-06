import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dam.settings")
django.setup()
from django.utils import timezone

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# App Model
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from cawas.models import *

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# System
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from daemon import Daemon
from sys    import exit
from sys    import argv

import logging
import time

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SDK
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from cawas.backend_sdk import *

from lib import *

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Basic Config
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
LOG_FILE = './log/publisher.log'
ERR_FILE = './log/publisher.err'
PID_FILE = './pid/publisher.pid'


class PublisherException(Exception):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)


def publish_movie(asset, lang):
    try:
        movie = Movie.objects.get(asset=asset)
    except ObjectDoesNotExist:
        msg = "Movie with asset ID %s does not exist" % asset.asset_id
        raise PublisherException(msg)
    try:
        metadata = MovieMetadata.objects.get(movie=movie, language=lang)
    except ObjectDoesNotExist:
        msg = "Movie with asset ID %s has not %s metadata" % (asset.asset_id, lang.name)
        raise PublisherException(msg)
    return metadata


def publish_episode(asset, lang):
    try:
        episode = Episode.objects.get(asset=asset)
    except ObjectDoesNotExist:
        msg = "Episode with asset ID %s does not exist" % asset.asset_id
        logging.error(msg)
        raise PublisherException(msg)
    try:
        metadata = EpisodeMetadata.objects.get(episode=episode, language=lang)
    except ObjectDoesNotExist:
        msg = "Episode with asset ID %s has not %s metadata" % (asset.asset_id, lang.name)
        logging.error(msg)
        raise PublisherException(msg)
    return metadata


def publish_serie(asset, lang):
    try:
        serie = Serie.objects.get(asset=asset)
    except ObjectDoesNotExist:
        msg = "Serie with asset ID %s does not exist" % asset.asset_id
        logging.error(msg)
        raise PublisherException(msg)
    try:
        metadata = SerieMetadata.objects.get(serie=serie, language=lang)
    except ObjectDoesNotExist:
        msg = "Serie with asset ID %s has not %s metadata" % (asset.asset_id, lang.name)
        logging.error(msg)
        raise PublisherException(msg)
    metadata.publish_date = timezone.now()
    metadata.save()
    return metadata


def publish_girl(asset, lang):
    try:
        girl = Girl.objects.get(asset=asset)
    except ObjectDoesNotExist:
        msg = "Girl with asset ID %s does not exist" % asset.asset_id
        logging.error(msg)
        raise PublisherException(msg)
    try:
        metadata = GirlMetadata.objects.get(girl=girl, language=lang)
    except ObjectDoesNotExist:
        msg = "Girl with asset ID %s has not %s metadata" % (asset.asset_id, lang.name)
        logging.error(msg)
        raise PublisherException(msg)
    return metadata


def publish_asset(job):
    try:
        asset = Asset.objects.get(asset_id=job.item_id)
    except ObjectDoesNotExist:
        msg = "Asset with ID %s does not exist" % job.item_id
        logging.error(msg)
        raise PublisherException(msg)
    if asset.asset_type == 'movie':
        return publish_movie(asset, job.item_lang)
    elif asset.asset_type == 'episode':
        return publish_episode(asset, job.item_lang)
    elif asset.asset_type == 'serie':
        return publish_serie(asset, job.item_lang)
    elif asset.asset_type == 'girl':
        return publish_girl(asset, job.item_lang)


def publish_slider(job):
    try:
        slider = Slider.objects.get(slider_id=job.item_id)
    except ObjectDoesNotExist:
        msg = "Slider with ID %s does not exist" % job.item_id
        logging.error(msg)
        raise PublisherException(msg)
    return slider


def publish_block(job):
    try:
        block = Block.objects.get(block_id=job.item_id, language=job.item_lang)
    except ObjectDoesNotExist:
        msg = "Block with ID %s and language %s does not exist" % (job.item_id, job.item_lang.name)
        logging.error(msg)
        raise PublisherException(msg)
    return block


def publish_category(job):
    try:
        category = Category.objects.get(category_id=job.item_id)
    except ObjectDoesNotExist:
        msg = "Category with ID %s does not exist" % job.item_id
        logging.error(msg)
        raise PublisherException(msg)
    try:
        metadata = CategoryMetadata.objects.get(category=category, language=job.item_lang)
    except ObjectDoesNotExist:
        msg = "Category with ID %s has not %s metadata" % (job.item_id, job.item_lang.name)
        logging.error(msg)
        raise PublisherException(msg)
    return metadata


def publish_channel(job):
    try:
        channel = Channel.objects.get(name=job.item_id, language=job.item_lang)
    except ObjectDoesNotExist:
        msg = "Channel with ID %s and language %s does not exist" % (job.item_id, job.item_lang.name)
        logging.error(msg)
        raise PublisherException(msg)
    return channel


def publish_items():

    try:
        URLs = {}
        URLs['BL'] = Setting.objects.get(code="backend_block_url").value
        URLs['SL'] = Setting.objects.get(code="backend_slider_url").value
        URLs['AS'] = Setting.objects.get(code="backend_asset_url").value
        URLs['CH'] = Setting.objects.get(code="backend_channel_url").value
        URLs['CA'] = Setting.objects.get(code="backend_category_url").value
        APIKEY = Setting.objects.get(code="backend_api_key").value
        CDN_LANDSCAPE_URL = Setting.objects.get(code="image_cdn_landscape").value
        CDN_LOGO_URL      = Setting.objects.get(code="image_cdn_logo").value
        CDN_SLIDER_VIDEO  = Setting.objects.get(code="slider_video_url").value
    except ObjectDoesNotExist as e:
        msg = 'Error loading settings: %s' % e.message
        logging.error(msg)
        raise PublisherException(msg)

    jobs = PublishQueue.objects.filter(status='Q')

    for job in jobs:
        if job.schedule_date < timezone.now():
            if job.item_type == 'AS':
                try:
                    obj = publish_asset(job)
                except PublisherException as err:
                    job.status = 'E'
                    job.message = err.value
                    job.save()
                try:
                    item = asset_serializer(job.item_id, job.item_lang.code)
                except SerializerException as err:
                    job.status  = 'E'
                    job.message = err.value
                    job.save()

            elif job.item_type == 'BL':
                try:
                    obj = publish_block(job)
                except SerializerException as err:
                    job.status  = 'E'
                    job.message = err.value
                    job.save()
                try:
                    item = block_serializer(job.item_id)
                except SerializerException as err:
                    job.status = 'E'
                    job.message = err.value
                    job.save()

            elif job.item_type == 'SL':
                try:
                    obj = publish_slider(job)
                except PublisherException as err:
                    job.status = 'E'
                    job.message = err.value
                    job.save()
                try:
                    item = slider_serializer(job.item_id)
                    if obj.media_type == 'image':
                        item[0]['media_url'] = "%s%s" % (CDN_LANDSCAPE_URL, item[0]['media_url'])
                    elif obj.media_type == 'video':
                        item[0]['media_url'] = "%s%s" % (CDN_SLIDER_VIDEO, item[0]['media_url'])
                    if 'logo_url' in item[0]:
                        item[0]['logo_url'] = "%s%s" % (CDN_LOGO_URL, item[0]['logo_url'])
                except SerializerException as err:
                    job.status = 'E'
                    job.message = err.value
                    job.save()

            elif job.item_type == 'CA':
                try:
                    obj = publish_category(job)
                except SerializerException as err:
                    job.status = 'E'
                    job.message = err.value
                    job.save()
                try:
                    item = category_serializer(job.item_id, job.item_lang.code)
                except SerializerException as err:
                    job.status = 'E'
                    job.message = err.value
                    job.save()

            elif job.item_type == 'CH':
                try:
                    obj = publish_channel(job)
                except PublisherException as err:
                    job.status = 'E'
                    job.message = err.value
                    job.save()
                try:
                    item = channel_serializer(job.item_id)
                except SerializerException as err:
                    job.status = 'E'
                    job.message = err.value
                    job.save()
            else:
                job.status = 'E'
                job.message = "Job item type not defined"
                job.save()

            if job.status != 'E':
                endpoint = job.publish_zone.backend_url
                ep = ApiBackendResource(endpoint, URLs[str(job.item_type)], APIKEY)
                try:
                    if not obj.activated:
                        item[0]['publish_date'] = timezone.now().strftime('%s')
                        obj.publish_date = timezone.now()
                        obj.publish_status = True
                        obj.activated = True
                    else:
                        item[0]['publish_date'] = obj.publish_date.strftime('%s')
                    ep.add(item[0])
                    job.status = 'D'
                    job.save()
                    print item
                    logging.info('publish_item(): Published item: %s' % item)
                except ApiBackendException as err:
                    job.status = 'E'
                    job.message = err.value
                    job.save()
                    logging.error('publish_item(): %s' % err.value)
                obj.queue_status = job.status
                obj.save()

def publisher_main():

    logging.basicConfig(format   = '%(asctime)s - publisher_daemon.py -[%(levelname)s]: %(message)s',
                        filename = LOG_FILE,
                        level    = logging.INFO)

    while True:
        try:
            publish_items()
        except ApiBackendException as err:
            print err.value
            exit(2)
        except PublisherException as err:
            print err.value
            exit(2)
        time.sleep(30)


class DaemonMain(Daemon):
    def run(self):
        try:
            publisher_main()
        except KeyboardInterrupt:
            exit()


if __name__ == "__main__":
    daemon = DaemonMain(PID_FILE, stdout=LOG_FILE, stderr=ERR_FILE)

    if len(argv) == 2:
        if 'start'     == argv[1]:
            daemon.start()
        elif 'stop'    == argv[1]:
            daemon.stop()
        elif 'restart' == argv[1]:
            daemon.restart()
        elif 'run'     == argv[1]:
            daemon.run()
        elif 'status'  == argv[1]:
            daemon.status()
        else:
            print "Unknown command"
            exit(2)
        exit(0)
    else:
        print "usage: %s start|stop|restart|run" % argv[0]
        exit(2)
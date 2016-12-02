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
from backend_sdk import *
from lib import *

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Basic Config
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
LOG_FILE = './log/publisher.log'
ERR_FILE = './log/publisher.err'
PID_FILE = './pid/publisher.pid'

URLs = {'API':'http://www.zolechamedia.net:80002', 'BL':'/v1/blocks/', 'SL':'/v1/sliders/'}


def publish_items():

    jobs = PublishQueue.objects.filter(status='Q')

    for job in jobs:
        if job.schedule_date < timezone.now():
            if job.item_type == 'AS':
                try:
                    obj = Asset.objects.get(asset_id=job.item_id)
                except ObjectDoesNotExist:
                    job.status = 'E'
                    job.message = "Asset with ID %s does not exist" % job.item_id
                    job.save()
                try:
                    item = asset_serializer(job.item_id, job.item_lang)
                except SerializerException as err:
                    job.status  = 'E'
                    job.message = err.value
                    job.save()

            elif job.item_type == 'BL':
                try:
                    obj = Block.objects.get(block_id=job.item_id)
                except ObjectDoesNotExist:
                    job.status = 'E'
                    job.message = "Block with ID %s does not exist" % job.item_id
                    job.save()
                try:
                    item = block_serializer(job.item_id)
                except SerializerException as err:
                    job.status = 'E'
                    job.message = err.value
                    job.save()

            elif job.item_type == 'SL':
                try:
                    obj = Slider.objects.get(slider_id=job.item_id)
                except ObjectDoesNotExist:
                    job.status = 'E'
                    job.message = "Slider with ID %s does not exist" % job.item_id
                    job.save()
                try:
                    item = slider_serializer(job.item_id, job.item_lang)
                except SerializerException as err:
                    job.status = 'E'
                    job.message = err.value
                    job.save()

            elif job.item_type == 'CA':
                try:
                    obj = Category.objects.get(category_id=job.item_id)
                except ObjectDoesNotExist:
                    job.status = 'E'
                    job.message = "Category with ID %s does not exist" % job.item_id
                    job.save()
                try:
                    item = category_serializer(job.item_id, job.item_lang)
                except SerializerException as err:
                    job.status = 'E'
                    job.message = err.value
                    job.save()

            elif job.item_type == 'CH':
                try:
                    obj = Channel.objects.get(name=job.item_id)
                except ObjectDoesNotExist:
                    job.status = 'E'
                    job.message = "Channel with name %s does not exist" % job.item_id
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
                ep = ApiBackendResource(job.endpoint, URLs[str(job.item_type)])
                try:
                    ep.add(item[0])
                    job.status = 'D'
                    job.save()
                    obj.publish_date = timezone.now()
                    obj.publish_status = True
                    obj.save()
                except ApiBackendException as err:
                    job.status = 'E'
                    job.message = err.value
                    job.save()


def publisher_main():

    logging.basicConfig(format   = '%(asctime)s - publisher_daemon.py -[%(levelname)s]: %(message)s',
                        filename = LOG_FILE,
                        level    = logging.INFO)

    while True:
        try:
            publish_items()
        except ApiBackendException as err:
            print err.value


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
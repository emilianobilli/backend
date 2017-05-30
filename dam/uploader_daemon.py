import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dam.settings")
django.setup()

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
import os
import time

import logging

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SDK
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from lib import *

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# S3 Library
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from s3 import *


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Basic Config
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
LOG_FILE = './log/image_daemon.log'
ERR_FILE = './log/image_daemon.err'
PID_FILE = './pid/image_daemon.pid'


class UploaderException(Exception):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)


def upload_images():

    try:
        PORTRAIT_PATH = Setting.objects.get(code="s3_images_portrait").value
        LANDSCAPE_PATH = Setting.objects.get(code="s3_images_landscape").value
    except ObjectDoesNotExist as e:
        msg = 'Error loading settings: %s' % e.message
        logging.error(msg)
        raise UploaderException(msg)


    jobs = ImageQueue.objects.filter(status='Q').order_by('priority')

    for job in jobs:
        if job.schedule_date < timezone.now():
            s3 = S3Upload(job.publish_zone.s3_aws_access_key, job.publish_zone.s3_aws_secret_key)

            if job.image.portrait.name != '':
                try:
                    img = job.image.portrait.name
                    print img
                    if os.path.isfile(img):
                        src_path = os.path.dirname(img)
                        filename = os.path.basename(img)
                        dest_path = PORTRAIT_PATH
                        job.status = 'U'
                        job.save()
                        s3.upload(src_path, filename, job.publish_zone.s3_bucket, dest_path)
                        logging.info("File %s/%s uploaded successfully" % (src_path, filename))
                    else:
                        job.status = 'E'
                        msg = "File does not exist: %s/%s" % (src_path, filename)
                        job.message = msg
                        job.save()
                        logging.error('upload_images(): %s' % msg)
                except S3UploadException as err:
                    job.status = 'E'
                    job.message = str(err)
                    job.save()
                    logging.error('upload_images(): %s' % str(err))

            if job.image.landscape.name != '' and job.status != 'E':
                try:
                    img = job.image.landscape.name
                    if os.path.isfile(img):
                        src_path = os.path.dirname(img)
                        filename = os.path.basename(img)
                        dest_path = LANDSCAPE_PATH
                        job.status = 'U'
                        job.save()
                        s3.upload(src_path, filename, job.publish_zone.s3_bucket, dest_path)
                        logging.info("File %s/%s uploaded successfully" % (src_path, filename))
                    else:
                        job.status = 'E'
                        msg = "File does not exist: %s/%s" % (src_path, filename)
                        job.message = msg
                        job.save()
                        logging.error('upload_images(): %s' % msg)
                except S3UploadException as err:
                    job.status = 'E'
                    job.message = str(err)
                    job.save()
                    logging.error('upload_images(): %s' % str(err))

            if job.status != 'E':
                job.status = 'D'
                job.save()


def uploader_main():

    logging.basicConfig(format   = '%(asctime)s - uploader_daemon.py -[%(levelname)s]: %(message)s',
                        filename = LOG_FILE,
                        level    = logging.INFO)
    while True:
        try:
            upload_images()
        except UploaderException as err:
            print err.value
            exit(2)

        time.sleep(30)


class DaemonMain(Daemon):
    def run(self):
        try:
            uploader_main()
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


#upload_images()
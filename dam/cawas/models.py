from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.core.exceptions import *

# Create your models here.
import json
import os
from datetime import datetime

class Setting(models.Model):
    code             = models.CharField(max_length=32, help_text="Codigo del parametro")
    value            = models.CharField(max_length=128, help_text="Valor del parametro")
    value_aux        = models.CharField(max_length=128, blank=True, help_text="Valor adicional del parametro")

    def __unicode__(self):
        return self.code


class Device(models.Model):
    name = models.CharField(max_length=32, help_text="Nombre del tipo de dipositivo")

    def __unicode__(self):
        return self.name

class Contract(models.Model):
    name              = models.CharField(max_length=128, unique=True, help_text="Nombre del contrato")
    start_date        = models.DateTimeField()
    end_date          = models.DateTimeField()
    description       = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.name

class FatherAsset(models.Model):
    contract          = models.ForeignKey(Contract)
    asset_id          = models.CharField(max_length=8)
    arrival_date      = models.DateTimeField()
    duration          = models.IntegerField(default=90)

    def __unicode__(self):
        return self.asset_id


class PublishZone(models.Model):
    name              = models.CharField(max_length=128, help_text="Nombre de la zona")
    backend_url       = models.CharField(max_length=512, help_text="URL de publicacion del backend")
    backend_key       = models.CharField(max_length=128, help_text="API key del backend")
    s3_bucket         = models.CharField(max_length=128, help_text="S3 Bucket name")
    s3_aws_secret_key = models.CharField(max_length=128, help_text="S3 AWS Secret Key")
    s3_aws_access_key = models.CharField(max_length=128, help_text="S3 AWS Access Key")
    enabled           = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length= 20, help_text="Lenguage")
    code = models.CharField(max_length=2, help_text="Lenguage code")

    def __unicode__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=20, help_text="Country name")
    code = models.CharField(max_length=2, help_text="Country code")

    def __unicode__(self):
        return self.name


class PublishQueue(models.Model):
    STATUS = (
        ('Q', 'Queued'),
        ('D', 'Done'),
        ('E', 'Error')
    )

    TYPE = (
        ('BL', 'Block'),
        ('AS', 'Asset'),
        ('SL', 'Slider'),
        ('CA', 'Category'),
        ('CH', 'Channel'),
    )

    item_id       = models.CharField(max_length=8, help_text="ID del item")
    item_lang     = models.ForeignKey(Language)
    item_type     = models.CharField(max_length=2, choices=TYPE, default='', help_text='Tipo de item')
    creation_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    publish_zone  = models.ForeignKey(PublishZone)
    status        = models.CharField(max_length=1, choices=STATUS, default='Q', help_text='Job Status')
    schedule_date = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    message       = models.CharField(max_length=510, blank=True, help_text="Error or Warning message")

    def __unicode__(self):
        return "%s:%s" % (self.item_id, self.item_lang)


class Image(models.Model):
    name      = models.CharField(max_length=128, unique=True, help_text="Nombre de la imagen")
    portrait  = models.FileField(help_text="Portrait image", null=True, blank=True)
    landscape = models.FileField(help_text="Landscape image", null=True, blank=True)

    def __unicode__(self):
        return self.name


class ImageQueue(models.Model):
    STATUS = (
        ('Q', 'Queued'),
        ('U', 'Uploading'),
        ('D', 'Done'),
        ('E', 'Error')
    )

    image         = models.ForeignKey(Image)
    publish_zone  = models.ForeignKey(PublishZone)
    creation_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    status        = models.CharField(max_length=1, choices=STATUS, default='Q', help_text='Job Status')
    schedule_date = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    priority      = models.IntegerField(default=5, help_text="Prioridad. Menor valor, mayor prioridad")
    message       = models.CharField(max_length=510, blank=True, help_text="Error or Warning message")

    def __unicode__(self):
        return self.image.name


class Tag(models.Model):
    tag_id   = models.CharField(max_length=128, unique=True, help_text="Nombre del tag")
    name     = models.CharField(max_length=128, help_text="Nombre del tag")

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Tag, self).save(*args, **kwargs)
        if self.tag_id == '':

            id = str(self.id)

            while len(id) < 5:
                id = "0" + id

            self.tag_id = "T%s" % (id)
        metadata = TagMetadata.objects.filter(tag=self)
        for m in metadata:
            m.modification_date = timezone.now()
            m.save()
        super(Tag, self).save(*args, **kwargs)


class TagMetadata(models.Model):
    tag               = models.ForeignKey(Tag)
    language          = models.ForeignKey(Language)
    name              = models.CharField(max_length=128, help_text="Nombre del tag traducido")
    modification_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('tag', 'language',)

    def __unicode__(self):
        return ('%s:%s') % (self.tag.tag_id, self.language)


class Category(models.Model):
    category_id   = models.CharField(max_length=8, unique=True, help_text="ID de la Categoria")
    original_name = models.CharField(max_length=128, help_text="Nombre de la categoria")
    image         = models.ForeignKey(Image, blank=True, null=True)
    order         = models.IntegerField(unique=True, blank=True, null=True, help_text="Orden de la categoria")

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        if self.category_id == '':

            id = str(self.id)

            while len(id) < 5:
                id = "0" + id

            self.category_id = "C%s" % (id)
        metadata = CategoryMetadata.objects.filter(category=self)
        for m in metadata:
            m.modification_date = timezone.now()
            m.save()
        super(Category, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.original_name

    def toDict(self):
        dict = {}

        if self.order is not None:
            dict["order"] = self.order
        if self.image is not None:
            if self.image.portrait.name != '':
                dict["image_portrait"] = os.path.basename(self.image.portrait.name)
            if self.image.landscape.name != '':
                dict["image_landscape"] = os.path.basename(self.image.landscape.name)

        return dict


class CategoryMetadata(models.Model):
    category          = models.ForeignKey(Category)
    language          = models.ForeignKey(Language)
    name              = models.CharField(max_length=128, help_text="Nombre de la categoria")
    modification_date = models.DateTimeField(auto_now=True)
    publish_date      = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    publish_status    = models.BooleanField(default=False)
    activated         = models.BooleanField(default=False)
    queue_status      = models.CharField(max_length=1, default='', blank=True, help_text="Status del item en PublishQueue")

    class Meta:
        unique_together = ('category', 'language',)

    def __unicode__(self):
        return ('%s:%s') % (self.category.category_id, self.language)

    def toDict(self):
        dict = {}

        dict["lang"] = self.language.code
        dict["category_name"] = self.name

        return dict


class Channel(models.Model):
    name              = models.CharField(max_length=128, unique=True, help_text="Nombre del canal")
    logo              = models.FileField(help_text="Logo image", null=True, blank=True)
    modification_date = models.DateTimeField(auto_now=True)
    publish_date      = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    publish_status    = models.BooleanField(default=False)
    activated         = models.BooleanField(default=False)
    queue_status      = models.CharField(max_length=1, default='', help_text="Status del item en PublishQueue")

    def __unicode__(self):
        return self.name

    def toDict(self):
        dict = {}

        dict["channel_name"] = self.name
        if self.logo is not None:
            dict["logo_url"] = self.logo

        return dict


class Asset(models.Model):
    TYPE = (
        ("movie", "Movie"),
        ("serie", "Serie"),
        ("episode", "Episode"),
        ("girl", "Girl"),
        ("unknown", "Unknown")
    )


    asset_id          = models.CharField(max_length=8, unique=True, help_text="ID del Asset")
    asset_type        = models.CharField(max_length=10, choices=TYPE, blank=True, null=True, help_text="Tipo de Asset")
    creation_date     = models.DateTimeField(auto_now=False, auto_now_add=True)
    target_country    = models.ManyToManyField(Country, blank=True)

    def save(self, *args, **kwargs):
        super(Asset, self).save(*args, **kwargs)
        if self.asset_type == "girl" or self.asset_type == "serie":

            if self.asset_id == '':
                id = str(self.id)

                while len(id) < 5:
                    id = "0" + id

                if self.asset_type == "girl":
                    self.asset_id = "G%s" % id
                elif self.asset_type == "serie":
                    self.asset_id = "S%s" % id


                super(Asset, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.asset_id

    def toDict(self):
        dict = {}

        tc_list = []
        for tc in self.target_country.all():
            tc_list.append(tc.code)
        if len(tc_list) > 0:
            dict["target_country"] = tc_list

        dict["asset_id"]     = self.asset_id
        if self.asset_type == 'girl':
            dict["asset_type"] = 'girl'
        else:
            dict["asset_type"] = 'show'

        return dict


class Slider(models.Model):
    TYPE = (
        ("image", "Image"),
        ("video", "Video")
    )
    slider_id         = models.CharField(max_length=8, unique=True, help_text="ID del Slider")
    media_type        = models.CharField(max_length=10, choices=TYPE, help_text="Tipo de Slider")
    image             = models.ForeignKey(Image, blank=True, null=True)
    asset             = models.ForeignKey(Asset, blank=True, null=True)
    linked_url        = models.CharField(max_length=256, blank=True, help_text="Link del slider a URL")
    target_device     = models.ForeignKey(Device)
    language          = models.ForeignKey(Language)
    target_country    = models.ManyToManyField(Country, blank=True)
    text              = models.CharField(max_length=256, blank=True, help_text="Texto asociado al Slider")
    publish_date      = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    publish_status    = models.BooleanField(default=False)
    activated         = models.BooleanField(default=False)
    queue_status      = models.CharField(max_length=1, default='', help_text="Status del item en PublishQueue")


    def save(self, *args, **kwargs):
        super(Slider, self).save(*args, **kwargs)
        if self.slider_id == '':
            id = str(self.id)
            while len(id) < 5:
                id = "0" + id
            self.slider_id = "L%s" % (id)
        super(Slider, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.slider_id

    def toDict(self):
        dict = {}

        tc_list = []
        for tc in self.target_country.all():
            tc_list.append(tc.code)
        if len(tc_list) > 0:
            dict["target_country"] = tc_list

        dict["slider_id"]  = self.slider_id
        dict["media_type"] = self.media_type
        if self.image is not None:
            if self.image.landscape.name != '':
                dict["media_url"] = os.path.basename(self.image.landscape.name)
        if self.asset is not None:
            dict["linked_asset_id"]   = self.asset.asset_id
            dict["linked_asset_type"] = self.asset.asset_type
        elif self.linked_url != '':
            dict["linked_url"] = self.linked_url
        dict["target"] = self.target_device.name
        dict["lang"]   = self.language.code
        dict["text"]   = self.text

        return dict


class Girl(models.Model):
    TYPE = (
        ("pornstar", "Pornstar"),
        ("playmate", "Playmate")
    )
    asset             = models.ForeignKey(Asset)
    name              = models.CharField(max_length=128, unique=True, help_text="Nombre de la actriz")
    type              = models.CharField(max_length=20, choices=TYPE, help_text="Tipo de actriz")
    image             = models.ForeignKey(Image, blank=True, null=True)
    birth_date        = models.DateField(blank=True, null=True,   help_text="Fecha de nacimiento")
    height            = models.IntegerField(blank=True, null=True, help_text="Altura en cm")
    weight            = models.IntegerField(blank=True, null=True, help_text="Peso en KG")

    def __unicode__(self):
        return self.asset.asset_id

    def save(self, *args, **kwargs):
        metadata = GirlMetadata.objects.filter(girl=self)
        for m in metadata:
            m.modification_date = timezone.now()
            m.save()
        super(Girl, self).save(*args, **kwargs)

    def toDict(self):
        dict = {}

        dict["name"]             = self.name
        dict["class"]            = self.type
        if self.image is not None:
            if self.image.portrait.name != '':
                dict["image_portrait"] = os.path.basename(self.image.portrait.name)
            if self.image.landscape.name != '':
                dict["image_landscape"] = os.path.basename(self.image.landscape.name)
        if self.birth_date is not None:
            dict["birth_date"] = self.birth_date.strftime("%Y-%m-%d")
        if self.height is not None:
            dict["height"] = "%d cm" % self.height
        if self.weight is not None:
            dict["weight"] = "%d kg" % self.weight

        return dict


class GirlMetadata(models.Model):
    girl              = models.ForeignKey(Girl)
    language          = models.ForeignKey(Language)
    description       = models.CharField(max_length=4096, blank=True, help_text="Descripcion de la actriz")
    nationality       = models.CharField(max_length=128, blank=True, help_text="Nacionalidad de la aztriz")
    modification_date = models.DateTimeField(auto_now=True)
    publish_date      = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    publish_status    = models.BooleanField(default=False)
    activated         = models.BooleanField(default=False)
    queue_status      = models.CharField(max_length=1, default='', help_text="Status del item en PublishQueue")

    class Meta:
        unique_together = ('girl', 'language',)

    def __unicode__(self):
        return ('%s:%s') % (self.girl.asset.asset_id, self.language)

    def toDict(self):
        dict = {}

        dict["lang"]         = self.language.code
        dict["summary_long"] = self.description
        dict["nationality"]  = self.nationality

        return dict


class Serie(models.Model):
    asset           = models.ForeignKey(Asset)
    original_title  = models.CharField(max_length=128, help_text="Titulo original")
    channel         = models.ForeignKey(Channel, null=True)
    year            = models.IntegerField(default=2000, help_text="Fecha de produccion")
    girls           = models.ManyToManyField(Girl)
    cast            = models.CharField(max_length=1024, blank=True, help_text="Listado de actores separados por coma")
    directors       = models.CharField(max_length=1024, blank=True, help_text="Listado de directores separados por coma")
    image           = models.ForeignKey(Image, blank=True, null=True)
    category        = models.ManyToManyField(Category)

    def __unicode__(self):
        return self.asset.asset_id

    def save(self, *args, **kwargs):
        metadata = SerieMetadata.objects.filter(serie=self)
        for m in metadata:
            m.modification_date = timezone.now()
            m.save()
        super(Serie, self).save(*args, **kwargs)

    # Convierte la serie en un diccionario
    def toDict(self):
        dict = {}

        dict["show_type"] = "serie"
        if self.channel is not None:
            dict["channel"] = self.channel.name
        dict["year"] = self.year
        if self.cast != '':
            dict["cast"] = self.cast
        if self.directors != '':
            dict["directors"] = self.directors
        if self.image is not None:
            if self.image.portrait.name != '':
                dict["image_portrait"] = os.path.basename(self.image.portrait.name)
            if self.image.landscape.name != '':
                dict["image_landscape"] = os.path.basename(self.image.landscape.name)

        return dict


class SerieMetadata(models.Model):
    serie             = models.ForeignKey(Serie)
    language          = models.ForeignKey(Language)
    title             = models.CharField(max_length=128, help_text="Titulo en el idioma correspondiente")
    summary_short     = models.CharField(max_length=2048, blank=True, help_text="Descripcion corta")
    summary_long      = models.CharField(max_length=4096, blank=True, help_text="Descripcion larga")
    modification_date = models.DateTimeField(auto_now=True)
    publish_date      = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    publish_status    = models.BooleanField(default=False)
    activated         = models.BooleanField(default=False)
    queue_status      = models.CharField(max_length=1, default='', blank=True, help_text="Status del item en PublishQueue")

    class Meta:
        unique_together = ('serie', 'language',)

    def __unicode__(self):
        return ('%s:%s') % (self.serie.asset_id, self.language)

    # Convierte la metadata en un diccionario
    def toDict(self):
        dict = {}

        categories = []
        for cat in self.serie.category.all():
            try:
                cat_metadata = CategoryMetadata.objects.get(category=cat, language=self.language)
                categories.append(cat_metadata.name)
            except ObjectDoesNotExist:
                pass

        dict["lang"]           = self.language.code
        dict["title"]          = self.title
        if self.summary_short != '':
            dict["summary_short"]  = self.summary_short
        if self.summary_long != '':
            dict["summary_long"]   = self.summary_long
        if len(categories) > 0:
            dict["categories"]     = categories

        episodes    = Episode.objects.filter(serie=self.serie)
        ep_metadata = EpisodeMetadata.objects.filter(episode__in=episodes, activated=True, language=self.language)
        seasons = []
        for em in ep_metadata:
            if str(em.episode.season) not in seasons:
                seasons.append(str(em.episode.season))
        dict["available_seasons"] = seasons
        dict["seasons"]  = len(seasons)
        dict["episodes"] = len(ep_metadata)

        return dict


class Episode(models.Model):
    asset           = models.ForeignKey(Asset)
    father_asset    = models.ForeignKey(FatherAsset, default=6)
    original_title  = models.CharField(max_length=128, help_text="Titulo original")
    channel         = models.ForeignKey(Channel)
    year            = models.IntegerField(default=2000, help_text="Fecha de produccion")
    girls           = models.ManyToManyField(Girl)
    cast            = models.CharField(max_length=1024, blank=True, help_text="Listado de actores separados por coma")
    directors       = models.CharField(max_length=1024, blank=True, help_text="Listado de directores separados por coma")
    image           = models.ForeignKey(Image, blank=True, null=True)
    runtime         = models.IntegerField(default=0, help_text="Duracion expresada en segundos")
    display_runtime = models.CharField(default="00:00:00", max_length=8, help_text="Duracion expresada en HH:MM:SS")
    serie           = models.ForeignKey(Serie)
    chapter         = models.IntegerField(default=0, help_text="Numero de capitulo")
    season          = models.IntegerField(default=0, help_text="Numero de temporada")
    thumbnails      = models.BooleanField(default=False)
    category        = models.ManyToManyField(Category)

    def __unicode__(self):
        return self.asset.asset_id

    def save(self, *args, **kwargs):
        metadata = EpisodeMetadata.objects.filter(episode=self)
        for m in metadata:
            m.modification_date = timezone.now()
            m.save()
        super(Episode, self).save(*args, **kwargs)

    # Convierte el episode en un diccionario
    def toDict(self):
        dict = {}

        dict["show_type"]       = "episode"
        if self.channel is not None:
            dict["channel"]         = self.channel.name
        dict["year"]            = self.year
        if self.cast != '':
            dict["cast"]            = self.cast
        if self.directors != '':
            dict["directors"]       = self.directors
        if self.image is not None:
            if self.image.portrait.name != '':
                dict["image_portrait"] = os.path.basename(self.image.portrait.name)
            if self.image.landscape.name != '':
                dict["image_landscape"] = os.path.basename(self.image.landscape.name)
        if self.display_runtime != '':
            hours, minutes, seconds = self.display_runtime.split(':')
            dict["runtime"] = int(seconds) + (int(minutes) * 60) + (int(hours) * 3600)
            min_sum = int(minutes) + (int(hours) * 60)
            if min_sum < 10:
                min_sum = "0%d" % min_sum
            dict["display_runtime"] = "%s:%s" % (min_sum, seconds)
        else:
            dict["runtime"] = 0
            dict["display_runtime"] = "00:00"
        if self.chapter > 0:
            dict["episode"]         = self.chapter
        if self.season > 0:
            dict["season"]          = self.season
        dict["thumbnails"]      = self.thumbnails
        dict["serie_id"]        = self.serie.asset.asset_id

        return dict


class EpisodeMetadata(models.Model):
    episode           = models.ForeignKey(Episode)
    language          = models.ForeignKey(Language)
    title             = models.CharField(max_length=128, help_text="Titulo en el idioma correspondiente")
    summary_short     = models.CharField(max_length=2048, blank=True, help_text="Descripcion corta")
    summary_long      = models.CharField(max_length=4096, blank=True, help_text="Descripcion larga")
    subtitle          = models.BooleanField(default=False )
    modification_date = models.DateTimeField(auto_now=True)
    publish_date      = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    publish_status    = models.BooleanField(default=False)
    activated         = models.BooleanField(default=False)
    queue_status      = models.CharField(max_length=1, default='', blank=True, help_text="Status del item en PublishQueue")

    class Meta:
        unique_together = ('episode', 'language',)

    def __unicode__(self):
        return ('%s:%s') % (self.episode.asset_id, self.language)

    # Convierte la metadata en un diccionario
    def toDict(self):
        dict = {}

        categories = []
        for cat in self.episode.category.all():
            try:
                cat_metadata = CategoryMetadata.objects.get(category=cat, language=self.language)
                categories.append(cat_metadata.name)
            except ObjectDoesNotExist:
                pass

        dict["lang"]           = self.language.code
        """
        if self.episode.season < 10:
            season = "0%d" % self.episode.season
        else:
            season = "%d" % self.episode.season
        if self.episode.chapter < 10:
            episode = "0%d" % self.episode.chapter
        else:
            episode = "%d" % self.episode.chapter
        dict["title"]          = "%s S%sE%s" % (self.title, season, episode)
        """
        dict["title"]          = self.title
        if self.summary_short != '':
            dict["summary_short"]  = self.summary_short
        if self.summary_long != '':
            dict["summary_long"]   = self.summary_long
        dict["subtitle"]       = self.subtitle
        if len(categories) > 0:
            dict["categories"] = categories

        return dict


class Movie(models.Model):
    asset           = models.ForeignKey(Asset)
    father_asset    = models.ForeignKey(FatherAsset,default=6)
    original_title  = models.CharField(max_length=128, help_text="Titulo original")
    channel         = models.ForeignKey(Channel)
    year            = models.IntegerField(default=2000, help_text="Fecha de produccion",blank=True, null=True)
    girls           = models.ManyToManyField(Girl)
    cast            = models.CharField(max_length=1024, blank=True, help_text="Listado de actores separados por coma")
    directors       = models.CharField(max_length=1024, blank=True, help_text="Listado de directores separados por coma")
    image           = models.ForeignKey(Image, blank=True, null=True)
    runtime         = models.IntegerField(default=0, help_text="Duracion expresada en segundos")
    display_runtime = models.CharField(default="00:00:00", max_length=8, help_text="Duracion expresada en HH:MM:SS")
    thumbnails      = models.BooleanField(default=False)
    category        = models.ManyToManyField(Category)

    def __unicode__(self):
        return self.asset.asset_id

    def save(self, *args, **kwargs):
        metadata = MovieMetadata.objects.filter(movie=self)
        for m in metadata:
            m.modification_date = timezone.now()
            m.save()
        super(Movie, self).save(*args, **kwargs)

    # Convierte la movie en un diccionario
    def toDict(self):
        dict = {}

        dict["show_type"] = "movie"
        if self.channel is not None:
            dict["channel"] = self.channel.name
        dict["year"] = self.year
        if self.cast != '':
            dict["cast"] = self.cast
        if self.directors != '':
            dict["directors"] = self.directors
        if self.image is not None:
            if self.image.portrait.name != '':
                dict["image_portrait"] = os.path.basename(self.image.portrait.name)
            if self.image.landscape.name != '':
                dict["image_landscape"] = os.path.basename(self.image.landscape.name)
        if self.display_runtime != '':
            hours, minutes, seconds = self.display_runtime.split(':')
            dict["runtime"] = int(seconds) + (int(minutes) * 60) + (int(hours) * 3600)
            min_sum = int(minutes) + (int(hours) * 60)
            if min_sum < 10:
                min_sum = "0%d" % min_sum
            dict["display_runtime"] = "%s:%s" % (min_sum, seconds)
        else:
            dict["runtime"] = 0
            dict["display_runtime"] = "00:00"
        dict["thumbnails"]      = self.thumbnails

        return dict


class MovieMetadata(models.Model):
    movie             = models.ForeignKey(Movie)
    language          = models.ForeignKey(Language)
    title             = models.CharField(max_length=128, help_text="Titulo en el idioma correspondiente")
    summary_short     = models.CharField(max_length=2048, blank=True, help_text="Descripcion corta")
    summary_long      = models.CharField(max_length=4096, blank=True, help_text="Descripcion larga")
    subtitle          = models.BooleanField(default=False)
    modification_date = models.DateTimeField(auto_now=True)
    publish_date      = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    publish_status    = models.BooleanField(default=False)
    activated         = models.BooleanField(default=False)
    queue_status      = models.CharField(max_length=1, default='', blank=True, help_text="Status del item en PublishQueue")

    class Meta:
        unique_together = ('movie', 'language',)

    def __unicode__(self):
        return ('%s:%s') % (self.movie.asset_id, self.language)

    # Convierte la metadata en un diccionario
    def toDict(self):
        dict = {}

        categories = []
        for cat in self.movie.category.all():
            try:
                cat_metadata = CategoryMetadata.objects.get(category=cat, language=self.language)
                categories.append(cat_metadata.name)
            except ObjectDoesNotExist:
                pass

        dict["lang"]           = self.language.code
        dict["title"]          = self.title
        if self.summary_short != '':
            dict["summary_short"]  = self.summary_short
        if self.summary_long != '':
            dict["summary_long"]   = self.summary_long
        dict["subtitle"]       = self.subtitle
        if len(categories) > 0:
            dict["categories"]     = categories

        return dict


class CableOperator(models.Model):
    cableoperator_id = models.CharField(max_length=8, unique=True, help_text="ID del Cableoperador")
    name             = models.CharField(max_length=128, help_text="Nombre del Cableoperador")
    image            = models.ForeignKey(Image, blank=True, null=True)
    phone            = models.CharField(max_length=128, blank=True, null=True, help_text="Telefono del Cableoperador")
    site             = models.CharField(max_length=128, blank=True, null=True, help_text="Sitio Web")
    country          = models.ForeignKey(Country)
    publish_date     = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    activated        = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(CableOperator, self).save(*args, **kwargs)
        if self.cableoperator_id == '':
            id = str(self.id)
            while len(id) < 5:
                id = "0" + id

            self.cableoperator_id = "I%s" % (id)
        super(CableOperator, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.cableoperator_id

    def toDict(self):
        dict = {}

        dict["co_id"] = self.cableoperator_id
        dict["co_name"] = self.name
        if self.image is not None:
            if self.image.landscape.name != '':
                dict["co_media_url"] = os.path.basename(self.image.landscape.name)
            dict["co_phone"] = self.phone
            dict["co_site"] = self.site
            dict["co_country"] = self.country.code
        return dict



class Block(models.Model):
    block_id          = models.CharField(max_length=8, unique=True, help_text="ID del Bloque")
    name              = models.CharField(max_length=128, help_text="Nombre del bloque")
    language          = models.ForeignKey(Language)
    channel           = models.ForeignKey(Channel, blank=True, null=True)
    assets            = models.ManyToManyField(Asset, blank=True)
    target_device     = models.ForeignKey(Device)
    target_country    = models.ManyToManyField(Country, blank=True)
    order             = models.IntegerField(help_text="Orden del bloque")
    modification_date = models.DateTimeField(auto_now=True)
    publish_date      = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    publish_status    = models.BooleanField(default=False)
    activated         = models.BooleanField(default=False)
    queue_status      = models.CharField(max_length=1, default='', blank=True, help_text="Status del item en PublishQueue")

    def save(self, *args, **kwargs):
        super(Block, self).save(*args, **kwargs)
        if self.block_id == '':

            id = str(self.id)

            while len(id) < 5:
                id = "0" + id

            self.block_id = "B%s" % (id)
        super(Block, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.block_id

    def toDict(self):
        dict = {}

        tc_list = []
        for tc in self.target_country.all():
            tc_list.append(tc.code)
        if len(tc_list) > 0:
            dict["target_country"] = tc_list

        dict["block_id"]      = self.block_id
        dict["block_name"]    = self.name
        dict["lang"]          = self.language.code
        dict["target"] = self.target_device.name
        if self.channel is not None:
            dict["channel"] = self.channel.name
        if self.order is not None:
            dict["order"] = self.order

        return dict


class VideoLog(models.Model):
    asset  = models.ForeignKey(Asset)
    tag    = models.ForeignKey(Tag)
    tc_in  = models.IntegerField(help_text="TC IN")
    tc_out = models.IntegerField(help_text="TC OUT")

    def __unicode__(self):
        return ('%s:%s') % (self.asset.asset_id, self.tag.name)


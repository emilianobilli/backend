from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Setting(models.Model):
    TYPE = (
        ("bl", "Block"),
        ("as", "Asset"),
        ("ca", "Category"),
        ("ch", "Channel")
    )

    name             = models.CharField(max_length=128, help_text="Nombre del Setting")
    type             = models.CharField(max_length=2, choices=TYPE, help_text="Tipo de Configuracion")
    publish_settings = models.TextField(max_length=2048, blank=True, help_text="Configuracion de publicacion")
    enabled          = models.BooleanField(default=False)


class Image(models.Model):
    name      = models.CharField(max_length=128, help_text="Nombre de la imagen")
    portrait  = models.FileField(help_text="Portrait image", null=True, blank=True)
    landscape = models.FileField(help_text="Landscape image", null=True, blank=True)

    def __unicode__(self):
        return self.name


class Category(models.Model):
    name     = models.CharField(max_length=128, help_text="Nombre de la categoria")
    language = models.CharField(max_length=2, choices=(("es","es"),("pt","pt")), help_text="Lenguage de la metadata")
    image    = models.ForeignKey(Image, blank=True, null=True)

    def __unicode__(self):
        return self.name


class Channel(models.Model):
    name = models.CharField(max_length=128, help_text="Nombre del canal")
    logo = models.FileField(help_text="Logo image", null=True, blank=True)

    def __unicode__(self):
        return self.name


class Asset(models.Model):
    TYPE = (
        ("ep","Episode"),
        ("se","Serie"),
        ("mo","Movie")
    )

    house_id        = models.CharField(max_length=8, unique=True, help_text="Asset House ID")
    original_title  = models.CharField(max_length=128, help_text="Titulo original")
    type            = models.CharField(max_length=2, choices=TYPE, help_text="Tipo de Asset")
    channel         = models.ForeignKey(Channel)
    year            = models.IntegerField(default=2000, help_text="Fecha de produccion")
    cast            = models.CharField(max_length=1024, blank=True, help_text="Listado de actores separados por coma")
    directors       = models.CharField(max_length=1024, blank=True, help_text="Listado de directores separados por coma")
    image           = models.ForeignKey(Image, blank=True, null=True)
    creation_date   = models.DateTimeField(auto_now=False, auto_now_add=True)
    publish_date    = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    publish_status  = models.BooleanField(default=False)


    def __unicode__(self):
        return self.house_id

    # Convierte el asset en un diccionario
    def toDict(self):
        dict = {}

        cast      = self.cast.replace(", ", ",").split(",")
        directors = self.directors.replace(", ", ",").split(",")


        dict["house_id"]      = self.house_id
        dict["show_type"]     = self.type
        dict["channel"]       = self.channel.name
        dict["year"]          = self.year
        dict["cast"]          = cast
        dict["directors"]     = directors

        return dict


class Serie(models.Model):
    asset           = models.ForeignKey(Asset)
    seasons         = models.IntegerField(default=0, help_text="Cantidad de temporadas")
    episodes        = models.IntegerField(default=0, help_text="Cantidad de episodios")

    def __unicode__(self):
        return self.asset.house_id

    # Convierte la serie en un diccionario
    def toDict(self):
        dict = {}

        dict["seasons"]  = self.seasons
        dict["episodes"] = self.episodes

        return dict


class Episode(models.Model):
    asset           = models.ForeignKey(Asset)
    runtime         = models.IntegerField(default=0, help_text="Duracion expresada en segundos")
    display_runtime = models.CharField(max_length=5, default="00:00", help_text="Duracion expresada en HH:MM")
    serie           = models.ForeignKey(Serie)
    chapter         = models.IntegerField(default=0, help_text="Numero de capitulo")
    season          = models.IntegerField(default=0, help_text="Numero de temporada")
    thumbnails      = models.BooleanField(default=False)

    def __unicode__(self):
        return self.asset.house_id

    # Convierte el episode en un diccionario
    def toDict(self):
        dict = {}

        dict["runtime"]         = self.runtime
        dict["display_runtime"] = self.display_runtime
        dict["chapter"]         = self.chapter
        dict["season"]          = self.season
        dict["thumbnails"]      = self.thumbnails
        dict["serie"]           = self.serie.asset.house_id

        return dict


class Movie(models.Model):
    asset           = models.ForeignKey(Asset)
    runtime         = models.IntegerField(default=0, help_text="Duracion expresada en segundos")
    display_runtime = models.CharField(default="00:00", max_length=5, help_text="Duracion expresada en HH:MM")
    thumbnails      = models.BooleanField(default=False)

    def __unicode__(self):
        return self.asset.house_id

    # Convierte la movie en un diccionario
    def toDict(self):
        dict = {}

        dict["runtime"]         = self.runtime
        dict["display_runtime"] = self.display_runtime
        dict["thumbnails"]      = self.thumbnails

        return dict


class Metadata(models.Model):
    asset          = models.ForeignKey(Asset)
    language       = models.CharField(max_length=2, choices=(("es","es"),("pt","pt")), help_text="Lenguage de la metadata")
    title          = models.CharField(max_length=128, help_text="Titulo en el idioma correspondiente")
    summary_short  = models.CharField(max_length=256, blank=True, help_text="Descripcion corta")
    summary_medium = models.CharField(max_length=1024, blank=True, help_text="Descripcion mediana")
    summary_long   = models.CharField(max_length=4096, blank=True, help_text="Descripcion larga")
    category       = models.ManyToManyField(Category)
    subtitle       = models.BooleanField(default=False)

    def __unicode__(self):
        return ('%s:%s') % (self.asset.house_id, self.language)

    # Convierte la metadata en un diccionario
    def toDict(self):
        dict = {}
        categories = []

        for cat in self.category.all():
            categories.append(cat.name)

        dict["language"]       = self.language
        dict["title"]          = self.title
        dict["summary_short"]  = self.summary_short
        dict["summary_medium"] = self.summary_medium
        dict["summary_long"]   = self.summary_long
        dict["categories"]     = categories
        dict["subtitle"]       = self.subtitle

        return dict


class Block(models.Model):
    name     = models.CharField(max_length=128, help_text="Nombre del bloque")
    language = models.CharField(max_length=2, choices=(("es","es"),("pt","pt")), help_text="Lenguage del bloque")
    assets   = models.ManyToManyField(Asset)

    def __unicode__(self):
        return self.name
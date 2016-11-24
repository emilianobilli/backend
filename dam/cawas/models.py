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
    name      = models.CharField(max_length=128, unique=True, help_text="Nombre de la imagen")
    portrait  = models.FileField(help_text="Portrait image", null=True, blank=True)
    landscape = models.FileField(help_text="Landscape image", null=True, blank=True)
    big       = models.FileField(help_text="Big image", null=True, blank=True)

    def __unicode__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=128, unique=True, help_text="Nombre del tag")
    language = models.CharField(max_length=2, choices=(("es", "es"), ("pt", "pt")), help_text="Lenguage de la metadata")

    class Meta:
        unique_together = ('name', 'language',)

    def __unicode__(self):
        return self.name


class Category(models.Model):
    name     = models.CharField(max_length=128, help_text="Nombre de la categoria")
    language = models.CharField(max_length=2, choices=(("es","es"),("pt","pt")), help_text="Lenguage de la metadata")
    image    = models.ForeignKey(Image, blank=True, null=True)

    class Meta:
        unique_together = ('name', 'language',)

    def __unicode__(self):
        return self.name


class Channel(models.Model):
    name = models.CharField(max_length=128, unique=True, help_text="Nombre del canal")
    logo = models.FileField(help_text="Logo image", null=True, blank=True)

    def __unicode__(self):
        return self.name


class Asset(models.Model):
    TYPE = (
        ("mo", "Movie"),
        ("se", "Serie"),
        ("ep", "Episode"),
        ("gi", "Girl")
    )

    asset_id       = models.CharField(max_length=8, unique=True, help_text="ID del Asset")
    asset_type     = models.CharField(max_length=2, choices=TYPE, blank=True, null=True, help_text="Tipo de Asset")
    creation_date  = models.DateTimeField(auto_now=False, auto_now_add=True)
    publish_date   = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    publish_status = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(Asset, self).save(*args, **kwargs)
        if self.asset_type == "girl" or self.asset_type == "serie":

            if self.asset_id == '':
                id = str(self.id)

                while len(id) < 6:
                    id = "0" + id

                if self.asset_type == "girl":
                    self.asset_id = "GL%s" % id
                elif self.asset_type == "serie":
                    self.asset_id = "SE%s" % id

                super(Asset, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.asset_id

    def toDict(self):
        dict = {}

        dict["asset_id"]     = self.asset_id
        dict["asset_type"]   = self.asset_type
        dict["publish_date"] = self.publish_date


class Block(models.Model):
    block_id = models.CharField(max_length=8, unique=True, help_text="ID del Bloque")
    name     = models.CharField(max_length=128, help_text="Nombre del bloque")
    language = models.CharField(max_length=2, choices=(("es","es"),("pt","pt")), help_text="Lenguage del bloque")
    channel  = models.ForeignKey(Channel)
    assets   = models.ManyToManyField(Asset)

    def save(self, *args, **kwargs):
        super(Block, self).save(*args, **kwargs)
        if self.block_id == '':

            id = str(self.id)

            while len(id) < 4:
                id = "0" + id

            self.block_id = "BK%s%s" % (self.language.upper(), id)
        super(Block, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.block_id


class Slider(models.Model):
    TYPE = (
        ("im", "Image"),
        ("vi", "Video")
    )

    slider_id  = models.CharField(max_length=8, unique=True, help_text="ID del Slider")
    media_type = models.CharField(max_length=2, choices=TYPE, help_text="Tipo de Slider")
    media_url  = models.CharField(max_length=256, help_text="Media url")
    asset      = models.ForeignKey(Asset)

    def save(self, *args, **kwargs):
        super(Slider, self).save(*args, **kwargs)
        if self.slider_id == '':

            id = str(self.id)

            while len(id) < 6:
                id = "0" + id

            self.slider_id = "SL%s" % (self.id)
        super(Slider, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.slider_id

    def toDict(self):
        dict = {}

        dict["slider_id"]         = self.slider_id
        dict["media_type"]        = self.media_type
        dict["linked_asset_id"]   = self.asset.asset_id
        dict["linked_asset_type"] = self.asset.asset_type

        return dict


class SliderMetadata(models.Model):
    slider   = models.ForeignKey(Slider)
    language = models.CharField(max_length=2, choices=(("es","es"),("pt","pt")), help_text="Lenguage del Slider")
    text     = models.CharField(max_length=256, blank=True, help_text="Texto asociado al Slider")

    class Meta:
        unique_together = ('slider', 'language',)

    def __unicode__(self):
        return ('%s:%s') % (self.slider.slider_id, self.language)


class Girl(models.Model):
    TYPE = (
        ("po", "Pornstar"),
        ("pl", "Playmate")
    )

    asset       = models.ForeignKey(Asset)
    name        = models.CharField(max_length=128, unique=True, help_text="Nombre de la actriz")
    type        = models.CharField(max_length=2, choices=TYPE, help_text="Tipo de actriz")
    image       = models.ForeignKey(Image, blank=True, null=True)
    birth_date  = models.DateField(blank=True, null=True, help_text="Fecha de nacimiento")
    height      = models.IntegerField(blank=True, null=True, help_text="Altura en cm")
    weight      = models.IntegerField(blank=True, null=True, help_text="Peso en KG")

    def __unicode__(self):
        return self.asset.asset_id

    def toDict(self):
        dict = {}

        dict["name"]            = self.name
        dict["type"]            = self.type
        dict["image_portrait"]  = self.image.portrait
        dict["image_landscape"] = self.image.landscape
        dict["image_big"]       = self.image.big
        dict["birth_date"]      = self.birth_date
        dict["height"]          = self.height
        dict["weight"]          = self.weight

        return dict


class GirlMetadata(models.Model):
    girl        = models.ForeignKey(Girl)
    language    = models.CharField(max_length=2, choices=(("es", "es"), ("pt", "pt")), help_text="Lenguage de la metadata")
    description = models.CharField(max_length=256, blank=True, help_text="Descripcion de la actriz")
    nationality = models.CharField(max_length=128, blank=True, help_text="Nacionalidad de la aztriz")

    class Meta:
        unique_together = ('girl', 'language',)

    def __unicode__(self):
        return ('%s:%s') % (self.girl.asset.asset_id, self.language)

    def toDict(self):
        dict = {}

        dict["language"]    = self.language
        dict["description"] = self.description
        dict["nationality"] = self.nationality

        return dict


class Serie(models.Model):
    asset           = models.ForeignKey(Asset)
    original_title  = models.CharField(max_length=128, help_text="Titulo original")
    channel         = models.ForeignKey(Channel)
    year            = models.IntegerField(default=2000, help_text="Fecha de produccion")
    girls           = models.ManyToManyField(Girl)
    cast            = models.CharField(max_length=1024, blank=True, help_text="Listado de actores separados por coma")
    directors       = models.CharField(max_length=1024, blank=True, help_text="Listado de directores separados por coma")
    image           = models.ForeignKey(Image, blank=True, null=True)
    seasons         = models.IntegerField(default=0, help_text="Cantidad de temporadas")
    episodes        = models.IntegerField(default=0, help_text="Cantidad de episodios")

    def __unicode__(self):
        return self.asset.asset_id

    # Convierte la serie en un diccionario
    def toDict(self):
        dict = {}

        cast = self.cast.replace(", ", ",").split(",")
        directors = self.directors.replace(", ", ",").split(",")

        dict["show_type"]       = "serie"
        dict["channel"]         = self.channel.name
        dict["year"]            = self.year
        dict["cast"]            = cast
        dict["directors"]       = directors
        dict["image_portrait"]  = self.image.portrait
        dict["image_landscape"] = self.image.landscape
        dict["image_big"]       = self.image.big
        dict["seasons"]         = self.seasons
        dict["episodes"]        = self.episodes

        return dict


class SerieMetadata(models.Model):
    serie          = models.ForeignKey(Serie)
    language       = models.CharField(max_length=2, choices=(("es","es"),("pt","pt")), help_text="Lenguage de la metadata")
    title          = models.CharField(max_length=128, help_text="Titulo en el idioma correspondiente")
    summary_short  = models.CharField(max_length=256, blank=True, help_text="Descripcion corta")
    summary_medium = models.CharField(max_length=1024, blank=True, help_text="Descripcion mediana")
    summary_long   = models.CharField(max_length=4096, blank=True, help_text="Descripcion larga")
    category       = models.ManyToManyField(Category)
    subtitle       = models.BooleanField(default=False)

    class Meta:
        unique_together = ('serie', 'language',)

    def __unicode__(self):
        return ('%s:%s') % (self.serie.asset_id, self.language)

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


class Episode(models.Model):
    asset           = models.ForeignKey(Asset)
    original_title  = models.CharField(max_length=128, help_text="Titulo original")
    channel         = models.ForeignKey(Channel)
    year            = models.IntegerField(default=2000, help_text="Fecha de produccion")
    girls           = models.ManyToManyField(Girl)
    cast            = models.CharField(max_length=1024, blank=True, help_text="Listado de actores separados por coma")
    directors       = models.CharField(max_length=1024, blank=True, help_text="Listado de directores separados por coma")
    image           = models.ForeignKey(Image, blank=True, null=True)
    runtime         = models.IntegerField(default=0, help_text="Duracion expresada en segundos")
    display_runtime = models.CharField(max_length=5, default="00:00", help_text="Duracion expresada en HH:MM")
    serie           = models.ForeignKey(Serie)
    chapter         = models.IntegerField(default=0, help_text="Numero de capitulo")
    season          = models.IntegerField(default=0, help_text="Numero de temporada")
    thumbnails      = models.BooleanField(default=False)

    def __unicode__(self):
        return self.asset.asset_id

    # Convierte el episode en un diccionario
    def toDict(self):
        dict = {}

        cast = self.cast.replace(", ", ",").split(",")
        directors = self.directors.replace(", ", ",").split(",")

        dict["show_type"]       = "episode"
        dict["channel"]         = self.channel.name
        dict["year"]            = self.year
        dict["cast"]            = cast
        dict["directors"]       = directors
        dict["image_portrait"]  = self.image.portrait
        dict["image_landscape"] = self.image.landscape
        dict["image_big"]       = self.image.big
        dict["runtime"]         = self.runtime
        dict["display_runtime"] = self.display_runtime
        dict["chapter"]         = self.chapter
        dict["season"]          = self.season
        dict["thumbnails"]      = self.thumbnails
        dict["serie"]           = self.serie.asset.asset_id

        return dict


class EpisodeMetadata(models.Model):
    episode        = models.ForeignKey(Episode)
    language       = models.CharField(max_length=2, choices=(("es","es"),("pt","pt")), help_text="Lenguage de la metadata")
    title          = models.CharField(max_length=128, help_text="Titulo en el idioma correspondiente")
    summary_short  = models.CharField(max_length=256, blank=True, help_text="Descripcion corta")
    summary_medium = models.CharField(max_length=1024, blank=True, help_text="Descripcion mediana")
    summary_long   = models.CharField(max_length=4096, blank=True, help_text="Descripcion larga")
    category       = models.ManyToManyField(Category)
    subtitle       = models.BooleanField(default=False)

    class Meta:
        unique_together = ('episode', 'language',)

    def __unicode__(self):
        return ('%s:%s') % (self.episode.asset_id, self.language)

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


class Movie(models.Model):
    asset           = models.ForeignKey(Asset)
    original_title  = models.CharField(max_length=128, help_text="Titulo original")
    channel         = models.ForeignKey(Channel)
    year            = models.IntegerField(default=2000, help_text="Fecha de produccion")
    girls           = models.ManyToManyField(Girl)
    cast            = models.CharField(max_length=1024, blank=True, help_text="Listado de actores separados por coma")
    directors       = models.CharField(max_length=1024, blank=True, help_text="Listado de directores separados por coma")
    image           = models.ForeignKey(Image, blank=True, null=True)
    runtime         = models.IntegerField(default=0, help_text="Duracion expresada en segundos")
    display_runtime = models.CharField(default="00:00", max_length=5, help_text="Duracion expresada en HH:MM")
    thumbnails      = models.BooleanField(default=False)

    def __unicode__(self):
        return self.asset.asset_id

    # Convierte la movie en un diccionario
    def toDict(self):
        dict = {}

        cast = self.cast.replace(", ", ",").split(",")
        directors = self.directors.replace(", ", ",").split(",")

        dict["show_type"]       = "movie"
        dict["channel"]         = self.channel.name
        dict["year"]            = self.year
        dict["cast"]            = cast
        dict["directors"]       = directors
        dict["image_portrait"]  = self.image.portrait
        dict["image_landscape"] = self.image.landscape
        dict["image_big"]       = self.image.big
        dict["runtime"]         = self.runtime
        dict["display_runtime"] = self.display_runtime
        dict["thumbnails"]      = self.thumbnails

        return dict


class MovieMetadata(models.Model):
    movie          = models.ForeignKey(Movie)
    language       = models.CharField(max_length=2, choices=(("es","es"),("pt","pt")), help_text="Lenguage de la metadata")
    title          = models.CharField(max_length=128, help_text="Titulo en el idioma correspondiente")
    summary_short  = models.CharField(max_length=256, blank=True, help_text="Descripcion corta")
    summary_medium = models.CharField(max_length=1024, blank=True, help_text="Descripcion mediana")
    summary_long   = models.CharField(max_length=4096, blank=True, help_text="Descripcion larga")
    category       = models.ManyToManyField(Category)
    subtitle       = models.BooleanField(default=False)

    class Meta:
        unique_together = ('movie', 'language',)

    def __unicode__(self):
        return ('%s:%s') % (self.movie.asset_id, self.language)

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

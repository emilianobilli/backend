from django.contrib import admin
import models

# Register your models here.

@admin.register(models.Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['name', 'enabled']

@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'portrait', 'landscape']

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'language', 'image']

@admin.register(models.Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'logo']

@admin.register(models.Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['house_id', 'original_title', 'type', 'publish_date', 'publish_status']

@admin.register(models.Serie)
class SerieAdmin(admin.ModelAdmin):
    list_display = ['asset', 'seasons', 'episodes']

@admin.register(models.Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ['asset', 'serie', 'chapter', 'season']

@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['asset']

@admin.register(models.Metadata)
class MetadataAdmin(admin.ModelAdmin):
    list_display = ['asset', 'title', 'language']

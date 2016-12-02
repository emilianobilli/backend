from django.contrib import admin
import models

# Register your models here.

@admin.register(models.Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['name', 'enabled']

@admin.register(models.PublishQueue)
class PublishQueueAdmin(admin.ModelAdmin):
    list_display = ['item_id', 'item_type', 'status', 'schedule_date', 'message']

@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'portrait', 'landscape']

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'name']


@admin.register(models.CategoryMetadata)
class CategoryMetadataAdmin(admin.ModelAdmin):
    list_display = ['category', 'language', 'name']


@admin.register(models.Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'logo']


@admin.register(models.Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_id', 'asset_type', 'creation_date', 'publish_date', 'publish_status']


@admin.register(models.Girl)
class GirlAdmin(admin.ModelAdmin):
    list_display = ['asset', 'name', 'type' ]


@admin.register(models.GirlMetadata)
class GirlMetadataAdmin(admin.ModelAdmin):
    list_display = ['girl', 'language']


@admin.register(models.Serie)
class SerieAdmin(admin.ModelAdmin):
    list_display = ['asset', 'original_title', ]


@admin.register(models.SerieMetadata)
class SerieMetadataAdmin(admin.ModelAdmin):
    list_display = ['serie', 'title', 'language']


@admin.register(models.Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ['asset', 'original_title', 'serie', 'chapter', 'season']


@admin.register(models.EpisodeMetadata)
class EpisodeMetadataAdmin(admin.ModelAdmin):
    list_display = ['episode', 'title', 'language']


@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['asset', 'original_title']


@admin.register(models.MovieMetadata)
class MovieMetadataAdmin(admin.ModelAdmin):
    list_display = ['movie', 'title', 'language']


@admin.register(models.Block)
class BlockAdmin(admin.ModelAdmin):
    readonly_fields = ('block_id',)
    list_display = ['block_id', 'name', 'language']


@admin.register(models.Slider)
class SliderAdmin(admin.ModelAdmin):
    readonly_fields = ('slider_id',)
    list_display = ['slider_id', 'media_type']


@admin.register(models.SliderMetadata)
class SliderMetadataAdmin(admin.ModelAdmin):
    list_display = ['slider', 'language']
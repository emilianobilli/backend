from django.contrib import admin
import models

# Register your models here.


@admin.register(models.Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['code', 'value', 'value_aux']


@admin.register(models.Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


@admin.register(models.Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


@admin.register(models.PublishQueue)
class PublishQueueAdmin(admin.ModelAdmin):
    list_display = ['item_id', 'item_type', 'status', 'schedule_date', 'message']
    search_fields = ['item_id']


@admin.register(models.PublishZone)
class PublishZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'enabled']


@admin.register(models.ImageQueue)
class ImageQueueAdmin(admin.ModelAdmin):
    list_display = ['image', 'status', 'schedule_date', 'message']
    search_fields = ['image__name']


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'portrait', 'landscape']
    search_fields = ['name']


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'original_name']


@admin.register(models.CategoryMetadata)
class CategoryMetadataAdmin(admin.ModelAdmin):
    list_display = ['category', 'language', 'name']
    search_fields = ['category__category_id']

@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['tag_id', 'name']


@admin.register(models.TagMetadata)
class TagMetadataAdmin(admin.ModelAdmin):
    list_display = ['tag', 'language', 'name']


@admin.register(models.Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'logo']


@admin.register(models.CableOperator)
class CableOperatorAdmin(admin.ModelAdmin):
    readonly_fields = ('cableoperator_id',)
    list_display = ['cableoperator_id', 'name', 'country']


@admin.register(models.Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_id', 'asset_type', 'creation_date']
    search_fields = ['asset_id']


@admin.register(models.Girl)
class GirlAdmin(admin.ModelAdmin):
    list_display = ['asset', 'name', 'type' ]
    search_fields = ['asset__asset_id', 'name']


@admin.register(models.GirlMetadata)
class GirlMetadataAdmin(admin.ModelAdmin):
    list_display = ['girl', 'language', 'modification_date']
    search_fields = ['girl__asset__asset_id']


@admin.register(models.Serie)
class SerieAdmin(admin.ModelAdmin):
    list_display = ['asset', 'original_title', ]
    search_fields = ['asset__asset_id', 'original_title']


@admin.register(models.SerieMetadata)
class SerieMetadataAdmin(admin.ModelAdmin):
    list_display = ['serie', 'title', 'language']
    search_fields = ['serie__asset__asset_id']


@admin.register(models.Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ['asset', 'original_title', 'serie', 'chapter', 'season']
    search_fields = ['asset__asset_id', 'original_title']


@admin.register(models.EpisodeMetadata)
class EpisodeMetadataAdmin(admin.ModelAdmin):
    list_display = ['episode', 'title', 'language']
    search_fields = ['episode__asset__asset_id']


@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['asset', 'original_title']
    search_fields = ['asset__asset_id', 'original_title']


@admin.register(models.MovieMetadata)
class MovieMetadataAdmin(admin.ModelAdmin):
    list_display = ['movie', 'title', 'language']
    search_fields = ['movie__asset__asset_id']


@admin.register(models.Block)
class BlockAdmin(admin.ModelAdmin):
    readonly_fields = ('block_id',)
    list_display = ['block_id', 'name', 'language']


@admin.register(models.Slider)
class SliderAdmin(admin.ModelAdmin):
    readonly_fields = ('slider_id',)
    list_display = ['slider_id', 'media_type', 'language']


@admin.register(models.Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(models.VideoLog)
class VideoLogAdmin(admin.ModelAdmin):
    list_display = ['asset', 'tag', 'tc_in', 'tc_out']

@admin.register(models.Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(models.FatherAsset)
class FatherAssetAdmin(admin.ModelAdmin):
    list_display = ['id','asset_id']


from django.conf.urls import url

from . import views
from django.contrib.auth.views import logout


urlpatterns = [
    url(r'^login/$', views.login_view, name='login_view'),
    url(r'^logout/$', views.logout_view, name='logout_view'),
    url(r'^$', views.menu_view, name='menu_view'),
    #url(r'^mantenimiento$', views.matenimiento_view, name='mantenimiento_view'),

    url(r'^movies/add/$', views.add_movies_view, name='add_movie'),
    url(r'^movies/edit/(?P<asset_id>\w*)/$', views.edit_movies_view, name='edit_movie'),
    url(r'^movies/list/$', views.list_movies_view, name='list_movies'),
    url(r'^movies/unpublish/(?P<id>\d*)/$', views.unpublish_movies_view, name='unpublish_movie'),
    url(r'^movies/publish/(?P<id>\d*)/$', views.publish_movies_view, name='publish_movie'),

    url(r'^girls/add/$', views.add_girls_view, name='add_girls'),
    url(r'^girls/edit/(?P<asset_id>\w*)/$', views.edit_girls_view, name='edit_girls'),
    url(r'^girls/list/$', views.list_girls_view, name='list_girls'),
    url(r'^girls/unpublish/(?P<id>\w*)$', views.unpublish_girls_view, name='unpublish_girls'),
    url(r'^girls/publish/(?P<id>\w*)$', views.publish_girls_view, name='publish_girls'),

    url(r'^categories/add/$', views.add_category_view, name='add_categories'),
    url(r'^categories/edit/(?P<category_id>\w*)/$', views.edit_category_view, name='edit_categories'),
    url(r'^categories/list/$', views.list_categories_view, name='list_categories'),
    url(r'^categories/unpublish/(?P<id>\w*)$', views.unpublish_categories_view, name='unpublish_categories'),
    url(r'^categories/publish/(?P<id>\w*)$', views.publish_categories_view, name='publish_categories'),

    url(r'^series/add/$', views.add_series_view, name='add_series'),
    url(r'^series/edit/(?P<asset_id>\w*)/$', views.edit_series_view, name='edit_series'),
    url(r'^series/list/$', views.list_series_view, name='list_series'),
    url(r'^series/unpublish/(?P<id>\w*)$', views.unpublish_series_view, name='unpublish_series'),
    url(r'^series/publish/(?P<id>\w*)$', views.publish_series_view, name='publish_series'),

    url(r'^blocks/add/$', views.add_blocks_view, name='add_blocks'),
    url(r'^blocks/edit/(?P<block_id>\w*)/$', views.edit_blocks_view, name='edit_episodes'),
    url(r'^blocks/list/$', views.list_blocks_view, name='list_blocks'),
    url(r'^blocks/unpublish/(?P<id>\w*)$', views.unpublish_blocks_view, name='unpublish_blocks'),
    url(r'^blocks/publish/(?P<id>\w*)$', views.publish_blocks_view, name='publish_blocks'),


    url(r'^episodes/add/$', views.add_episodes_view, name='add_blocks'),
    url(r'^episodes/edit/(?P<episode_id>\w+?)/$', views.edit_episodes_view, name='edit_episodes'),
    #url(r'^episodes/edit/(?P<episode_id>\w+?)/$', views.edit_episodes_view)
    url(r'^episodes/list/$', views.list_episodes_view, name='list_episodes'),
    #url(r'^episodes/list/(?P<episode_id>\w*)$', views.list_episodes_view, name='list_episodes'),
    url(r'^episodes/unpublish/(?P<id>\w*)$', views.unpublish_episodes_view, name='unpublish_episodes'),
    url(r'^episodes/publish/(?P<id>\w*)$', views.publish_episodes_view, name='publish_episodes'),

    url(r'^sliders/add/$', views.add_sliders_view, name='add_sliders'),
    url(r'^sliders/edit/(?P<slider_id>\w+?)/$', views.edit_sliders_view, name='edit_sliders'),
    url(r'^sliders/list/$', views.list_sliders_view, name='list_sliders'),
    url(r'^sliders/unpublish/(?P<id>\w*)$', views.unpublish_sliders_view, name='unpublish_sliders'),
    url(r'^sliders/publish/(?P<id>\w*)$', views.publish_sliders_view, name='publish_sliders'),

    #<#POST Json CAWAS>
    #url(r'^add_movie_json/$', views.add_movies_view, name='add_movie_json'),
    #url(r'^edit_movie_json/$', views.edit_movies_view, name='edit_movie_json'),
    #url(r'^add_girl_json/$', views.add_girls_view, name='add_girl_json'),
    #url(r'^edit_girl_json/$', views.edit_girls_view, name='edit_girl_json'),
    #url(r'^add_category_json/$', views.add_category_view, name='add_category_json'),
    #url(r'^edit_category_json/$', views.edit_category_view, name='edit_category_json'),
    #url(r'^add_serie_json/$', views.add_serie_view, name='add_serie_json'),
    #url(r'^edit_serie_json/$', views.edit_serie_view, name='edit_serie_json'),
    #url(r'^add_block_json/$', views.add_block_view, name='add_block_json'),
    url(r'^api/add_asset/$', views.add_asset_view, name='api_add_asset')
    #</ POST Json CAWAS>



]
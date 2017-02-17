from django.conf.urls import url

from . import views
from django.contrib.auth.views import logout


urlpatterns = [
    url(r'^login/$', views.login_view, name='login_view'),
    url(r'^logout/$', views.logout_view, name='logout_view'),
    url(r'^$', views.menu_view, name='menu_view'),
    #url(r'^movies/$', views.index_movies_view, name='index_movies'),
    #url(r'^movies/(?P<opcion>\d)/(?P<cat>\d)$', views.index_movies_view, name='index_movies_2'),
    #url(r'^movies/add/$', views.add_movies_view, name='add_movies'),
    #url(r'^girls/add/$', views.add_girls_view, name='add_girls'),
    url(r'^movies/add/$', views.add_movies_view, name='add_movie'),
    url(r'^movies/edit/(?P<asset_id>\d*)/$', views.edit_movies_view, name='edit_movie'),

    #<#POST Json CAWAS>
    #url(r'^add_movie_json/$', views.add_movies_view, name='add_movie_json'),
    url(r'^edit_movie_json/$', views.edit_movies_view, name='edit_movie_json'),
    url(r'^add_girl_json/$', views.add_girl_view, name='add_girl_json'),
    url(r'^edit_girl_json/$', views.edit_girl_view, name='edit_girl_json'),
    url(r'^add_category_json/$', views.add_category_view, name='add_category_json'),
    url(r'^edit_category_json/$', views.edit_category_view, name='edit_category_json'),
    url(r'^add_serie_json/$', views.add_serie_view, name='add_serie_json'),
    url(r'^edit_serie_json/$', views.edit_serie_view, name='edit_serie_json'),
    url(r'^add_block_json/$', views.add_block_view, name='add_block_json'),
    url(r'^api/add_asset/$', views.add_asset_view, name='api_add_asset')

    #</ POST Json CAWAS>



]
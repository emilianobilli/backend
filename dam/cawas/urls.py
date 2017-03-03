from django.conf.urls import url

from . import views
from django.contrib.auth.views import logout


urlpatterns = [
    url(r'^login/$', views.login_view, name='login_view'),
    url(r'^logout/$', views.logout_view, name='logout_view'),
    url(r'^$', views.menu_view, name='menu_view'),
    url(r'^movies/add/$', views.add_movies_view, name='add_movie'),
    url(r'^movies/edit/(?P<asset_id>\d*)/$', views.edit_movies_view, name='edit_movie'),
    url(r'^girls/add/$', views.add_girls_view, name='add_girls'),
    url(r'^girls/edit/(?P<asset_id>\w*)/$', views.edit_girls_view, name='edit_girls'),
    url(r'^categories/add/$', views.add_category_view, name='add_categories'),
    url(r'^categories/edit/(?P<asset_id>\d*)/$', views.edit_category_view, name='edit_categories'),
    url(r'^series/add/$', views.add_series_view, name='add_series'),
    url(r'^series/edit/(?P<asset_id>\w*)/$', views.edit_series_view, name='edit_series'),
    #<#POST Json CAWAS>
    url(r'^add_movie_json/$', views.add_movies_view, name='add_movie_json'),
    url(r'^edit_movie_json/$', views.edit_movies_view, name='edit_movie_json'),
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
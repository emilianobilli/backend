from django.conf.urls import url

from . import views
from django.contrib.auth.views import logout

#<QUITAR ESTO>
from .views import current_datetime
from django.conf.urls import *
from .views import current_datetime, hours_ahead

#</ QUITAR ESTO>

urlpatterns = [
    url(r'^login/$', views.login_view, name='login_view'),
    url(r'^logout/$', views.logout_view, name='logout_view'),
    url(r'^inicio/$', views.menu_view, name='menu_view'),
    url(r'^movies/$', views.index_movies_view, name='index_movies'),
    url(r'^movies/(?P<opcion>\d)/(?P<cat>\d)$', views.index_movies_view, name='index_movies_2'),
    #url(r'^movies/add/$', views.add_movies_view, name='add_movies'),
    #url(r'^girls/add/$', views.add_girls_view, name='add_girls'),

    #< QUITAR ESTO>
    url(r'^pruebas/$', views.pruebas, name='pruebas'),
    url(r'^time/$', current_datetime),
    url(r'^time/plus/(\d{1,2})/$', hours_ahead),
    #</ QUITAR ESTO>

    #<#POST Json CAWAS>
    url(r'^add_movie_json/$', views.add_movies_view, name='add_movie_json'),
    url(r'^edit_movie_json/$', views.edit_movies_view, name='edit_movie_json'),
    url(r'^add_girl_json/$', views.add_girl_view, name='add_girl_json'),
    url(r'^edit_girl_json/$', views.edit_girl_view, name='edit_girl_json'),
    url(r'^add_category_json/$', views.add_category_view, name='add_category_json'),
    url(r'^edit_category_json/$', views.edit_category_view, name='edit_category_json'),
    url(r'^add_serie_json/$', views.add_serie_view, name='add_serie_json'),
    url(r'^edit_serie_json/$', views.edit_serie_view, name='edit_serie_json'),
    url(r'^add_block_json/$', views.add_block_view, name='add_block_json')
    #url(r'^edit_block_json/$', views.edit_block_view, name='edit_block_json')
    #</ POST Json CAWAS>



]
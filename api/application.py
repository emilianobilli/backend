#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import redirect
from flask import Response
from flask_cors import CORS, cross_origin
from backend import Backend
from backend import Components
from Auth    import Auth
from json   import dumps 
from json   import loads
import os
##
# Keys
##
import jwt
from keys   import MA
from keys   import CAWAS
from keys   import MA_SIGNATURE
from keys   import APP_QUERY
from keys   import GATRA
from time   import time
application = Flask(__name__)

backend = Backend({"languages": ['es','pt',"br"], 
                    "girls":
                        {"database": {
                            "table": "Girls",
                            "pk": "lang",
			    "index_sk": "human_id",
			    "index_name": "lang-human_id-index",
                            "sk": "asset_id",
                            "schema": {
                                    "lang": "S",
                                    "human_id": "S",
				    "asset_id": "S",
                                    "name": "S",
                                    "image_portrait": "S",
                                    "image_landscape": "S",
                                    "views": "N",
                                    "ranking": "N",
                                    "asset_type": "S",
                                    "blocks": "SS",
                                    "publish_date": "N",
                                    "class": "S",
                                    "summary_long": "S",
                                    "nationality": "S",
                                    "birth_date": "S",
                                    "height": "S",
                                    "weight": "S",
                                    "enabled": "N",
                            },
                         }},
                        "shows":
                        {"database": {
                            "table": "Girls",
                            "pk": "lang",
                            "sk": "asset_id",
			    "index_sk": "human_id",
			    "index_name": "lang-human_id-index",
                            "schema": {
                                    "lang": "S",
                                    "asset_id": "S",
                                    "title": "S",
                                    "human_id": "S",
                                    "name": "S",
				    "summary_short": "S",
                                    "display_runtime": "S",
                                    "runtime": "N",
                                    "seasons": "N",
                                    "episodes": "N",
                                    "season": "N",
                                    "episode": "N",
                                    "categories": "SS",
                                    "target_country": "SS",
                                    "year": "N",
                                    "image_portrait": "S",
                                    "image_landscape": "S",
                                    "views": "N",
                                    "ranking": "N",
                                    "show_type": "S",
                                    "asset_type": "S",
                                    "blocks": "SS",
                                    "freeview": "N",
                                    "channel": "S",
                                    "serie_id": "S",
                                    "available_seasons": "SS",
                                    "girls_id": "SS",
                                    "girls_name": "SS",
                                    "girls_display": "SS",
                                    "publish_date": "N",
                                    "summary_long": "S",
				    "serie_human_id": "S",
                                    "cast":"S",
                                    "directors":"S",
                                    "enabled": "N",
                                    "thumbnails": "S",
                                    "subtitle": "S",
                            },
                         }},
                        "ranking": {'table_name': 'Ranking', 'commit_index': 'lala'},
                        "views" : {'table_name': 'Views', 'commit_index':'lala'},
                        "asset_type": {'database': {'table': 'AssetType', 'pk': 'asset_id', 'schema': {'asset_id': 'S', 'asset_type':'S', 'asset_human_id':'S','human_id':'S'}}},
                        "vote": {'database': {'table': 'Vote', 'pk': 'asset_id', 'sk':'username', 'schema': {'asset_id': 'S', 'username':'S', 'voted':'N'}}},
			"resume": {"domain": {"id_field": "asset_user", "filter_query": "", "schema": ["asset_user", "asset_id", "username", "episode", "season", "progress", "seekto", "country", "timestamp"], "return_fields": ["asset_user", "asset_id", "username", "episode", "season", "progress", "seekto", "timestamp", "country"], "name": "resume"}},
                        "search_domain": {u'es' : {"domain": {
                                                        "id_field": "asset_id",
                                                        "filter_query" : '',
                                                        "schema": ["channel","asset_id","human_id", "summary_short","display_runtime","seasons","season","episode","episodes","categories","show_type","year","serie_id","girls_id","name", "image_big", "image_landscape", "image_portrait", "views", "ranking", "asset_type", "blocks", "publish_date", "class", "summary_long", "nationality", "target_country"],
                                                        "return_fields": ["publish_date","asset_id","human_id" ,"name", "title", "ranking", "views","display_runtime", "summary_short" ,"summary_long","categories", "image_landscape", "image_portrait", "channel", "show_type","asset_type", "year", "seasons", "class","episodes", "episode", "serie_id", "season"],
                                                        "name" : "es-hotgodomain",
                                                        }
                                                 },
					  u'br' : {"domain": {
                                                        "id_field": "asset_id",
                                                        "filter_query" : '',
                                                        "schema": ["channel","asset_id","human_id", "name", "summary_short","display_runtime","seasons","season","episode","episodes","categories","show_type","year","serie_id","girls_id", "image_big", "image_landscape", "image_portrait", "views", "ranking", "asset_type", "blocks", "publish_date", "class", "summary_long", "nationality", "target_country"],
                                                        "return_fields": ["publish_date","asset_id","human_id" ,"name", "title", "ranking", "views","display_runtime", "summary_short" ,"summary_long","categories", "image_landscape", "image_portrait", "channel", "show_type","asset_type", "year", "seasons", "class","episodes", "episode", "serie_id", "season"],
                                                        "name" : "br-hotgodomain",
                                                        }
                                                 },
                                          u'pt' : {"domain": {
                                                        "id_field": "asset_id",
                                                        "filter_query" : '',
                                                        "schema": ["channel","asset_id","human_id", "summary_short","display_runtime","seasons","season","episode","episodes","categories","show_type","year","serie_id","girls_id","name", "image_big", "image_landscape", "image_portrait", "views", "ranking", "asset_type", "blocks", "publish_date", "class", "summary_long", "nationality", "target_country"],
                                                        "return_fields": ["asset_id", "human_id","name", "title", "ranking", "views","display_runtime", "summary_short" ,"categories", "image_landscape", "image_portrait", "channel", "show_type","asset_type", "year", "seasons", "class","episodes", "episode", "serie_id"],
                                                        "name" : "pthotgodomain",
                                                        }
                                                 }
                                         }
                    })



components = Components({
                "co": {
                    "database": {
                        "table": "Cop",
                        "pk": "lang",
                        "sk": "co_id",
                        "schema": {
                            "lang": "S",
                            "co_id": "S",
                            "co_name": "S",
                            "co_media_url": "S",
                            "image_filename": "S",
                            "co_phone": "S",
                            "co_site":  "S",
                            "co_country": "S"
                        },
                    }
                },
                "channels": {
                    "database": {
                        "table": "Channels",
                        "pk": "lang",
                        "sk": "channel_name",
                        "schema": {
                            "lang": "S",
                            "channel_name": "S"
                        },
                    }
                },
                "categories": {
                    "database": {
                        "table": "Categories",
                        "pk": "lang",
                        "sk": "category_name",
                        "schema": {
                            "lang": "S",
                            "category_name": "S",
                            "image_portrait": "S",
                            "image_landscape": "S",
                            "order": "N"
                        },
                    }
                },
                "sliders": {
                    "database": {
                        "table": "Sliders",
                        "pk": "lang",
                        "sk": "slider_id",
                        "schema": {
                            "lang": "S",
                            "slider_id": "S",
                            "media_url": "S",
			    "logo_url": "S",
                            "target_country": "SS",
                            "media_type": "S",
                            "linked_asset_id": "S",
                            "linked_human_id": "S",
			    "linked_asset_type": "S",
                            "target": "S",
			    "linked_url": "S",
			    "text": "S"
                        },
                    }
                },
                "blocks": {
                    "database": {
                        "table": "Blocks",
                        "pk": "lang",
                        "sk": "block_id",
                        "schema": {
                            "lang": "S",
                            "block_id": "S",
                            "block_name": "S",
                            "target_country": "SS",
                            "order": "N",
			    "type": "S",
			    "query": "S",
                            "channel": "S",
                            "target": "S",
                        },
                    }
                },
                "cams" : {
		    "database": {
			"table": "Cams",
			"pk": "lang",
			"schema": {
			    "lang": "S",
			    "cam_id": "S",
			    "date": "N",
			    "image_url": "S",
			    "url": "S",
			    "name": "S"
			}
		    }
		}
            })

#
# Faltan agregar campos 
# {u'username': u'AR_dibox_000100000004', u'apikey_ttl': u'2017-03-18T14:30:11.838Z', u'country': u'AR', u'source_ip': u'::1', u'idp': u'dibox', u'access': u'full', u'user_agent': u'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

 
authorization = Auth({
                "database":
                    { "table" : "Auth",
                        "pk":   "apikey",
                        "schema": {
                            "apikey": "S",
                            "enabled": "N",
                            "expiration": "N",
                        "username": "S"
                        }
                    }
                })

@application.route('/v1/cams/', methods=['GET'])
@application.route('/v1/cams', methods=['GET'])
@cross_origin()
def cams():
    args = {}
    now  = int(time())
    cam_duration = 40*60
    cam_start = 10*60

    items = []

    for k in request.args.keys():
        args[k] = request.args.get(k)
    ret = components.query_cams(args)
    for item in ret['body']['items']:
	if int(item['date']) + cam_duration > now:
	    if int(item['date']) - cam_start < now:
		item['url'] = 'https://www.hotgo.tv/cams/show'
	    items.append(item)
    ret['body']['count'] = len(items)
    ret['body']['items'] = items
    ret['body']['now'] = now
	    

    return Response(response=dumps(ret['body']), status=ret['status'])

#------------------------------------------------------------------------------------------------------------------------
#       Pages Components: Channels, Categories, Sliders, Blocks
#------------------------------------------------------------------------------------------------------------------------
@application.route('/v1/categories/', methods=['GET', 'POST'])
@application.route('/v1/categories',  methods=['GET', 'POST'])
@cross_origin()
def urlCategories():
    if request.method == 'GET':
        args = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = components.query_categories(args)
        return Response(response=dumps(ret['body']), status=ret['status'])
    elif request.method == 'POST':
        if 'X-PRIVATE-APIKEY' in request.headers:
            private_key = request.headers.get('X-PRIVATE-APIKEY')
            if private_key == CAWAS:
                body = loads(request.data)
                if body['action'] == 'add':
                    ret  = components.add_category(body['item'])
                elif body['action'] == 'del':
                    ret  = components.del_category(body['item'])
            else:
                ret['status'] = 401
                ret['body']   = {'status': 'failure', 'message': 'Unauthorized'}
        else:
            ret['status'] = 422
            ret['body']   = {'status': 'failure', 'message': 'Missing Header'}

        return Response(response=dumps(ret['body']), status=ret['status'])

@application.route('/v1/co/', methods=['GET','POST'])
@application.route('/v1/co', methods=['GET','POST'])
@cross_origin()
def urlCop():
    if request.method == 'GET':
        args = {}
        args['lang'] = 'none'   # Hardcoding
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = components.query_co(args)
        return Response(response=dumps(ret['body']), status=ret['status'])
    elif request.method == 'POST':
        if 'X-PRIVATE-APIKEY' in request.headers:
            private_key = request.headers.get('X-PRIVATE-APIKEY')
            if private_key == CAWAS:
                body = loads(request.data)
                if body['action'] == 'add':
                    body['item']['lang'] = 'none'
                    ret  = components.add_co(body['item'])
                elif body['action'] == 'del':
                    body['item']['lang'] = 'none'
                    ret  = components.del_co(body['item'])
            else:
                ret['status'] = 401
                ret['body']   = {'status': 'failure', 'message': 'Unauthorized'}
        else:
            ret['status'] = 422
            ret['body']   = {'status': 'failure', 'message': 'Missing Header'}

        return Response(response=dumps(ret['body']), status=ret['status'])

@application.route('/v1/sliders/',    methods=['GET', 'POST'])
@application.route('/v1/sliders',     methods=['GET', 'POST'])
@cross_origin()
def urlSliders():
    if request.method == 'GET':
        args = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = components.query_sliders(args)
        return Response(response=dumps(ret['body']), status=ret['status'])
    elif request.method == 'POST':
        if 'X-PRIVATE-APIKEY' in request.headers:
            private_key = request.headers.get('X-PRIVATE-APIKEY')
            if private_key == CAWAS:
                body = loads(request.data)
                if body['action'] == 'add':
		    if 'linked_asset_id' in body['item']:
			asset_type = backend.asset_type.get({'asset_id':body['item']['linked_asset_id']})
			if 'asset_human_id' in asset_type['item']:
			    body['item']['linked_human_id'] = loads(asset_type['item']['asset_human_id'])[body['item']['lang']]
                	    ret  = components.add_slider(body['item'])
			else:
			    ret = {}
			    ret['status'] = 422
        		    ret['body']   = {'status': 'failure', 'message': 'No asset/human_id in Asset_Type'}
		    else:
			asset_type = {}
			ret  = components.add_slider(body['item'])
		    
                elif body['action'] == 'del':
                    ret  = components.del_slider(body['item'])
            else:
		ret = {}
                ret['status'] = 401
                ret['body']   = {'status': 'failure', 'message': 'Unauthorized'}
        else:
	    ret = {}	
            ret['status'] = 422
            ret['body']   = {'status': 'failure', 'message': 'Missing Header'}

        return Response(response=dumps(ret['body']), status=ret['status'])

@application.route('/v1/human_id/<string:asset_id>/', methods=['GET'])
@application.route('/v1/human_id/<string:asset_id>', methods=['GET'])
def getHumanId(asset_id):
    return Response(response=dumps(backend.asset_type.get({'asset_id':asset_id})))


@application.route('/v1/block/<string:block_id>/', methods=['GET'])
@application.route('/v1/block/<string:block_id>', methods=['GET'])
@cross_origin()
def urlGetBlock(block_id):
    args = {}
    for k in request.args.keys():
        args[k] = request.args.get(k)
    if 'lang' not in args:
	ret = {}
	ret['status'] = 422
        ret['body']   = {'status': 'failure', 'message': 'Mandatory Parameter is Missing'}
    else:
	ret = components.get_block({'lang': args['lang'],'block_id':block_id})

    return Response(response=dumps(ret['body']), status=ret['status'])


@application.route('/v1/private/tags/', methods=['POST'])
@application.route('/v1/private/tags', methods=['GET'])
@cross_origin()
def tagsAdd():
    ret = {}
    #if 'X-PRIVATE-APIKEY' in request.headers:
    private_key = request.headers.get('X-PRIVATE-APIKEY')
    body = loads(request.data)
    with open('tags.info', 'wt') as f:
        f.write(request.data)
 
    print("################################################")
    print("BODY:, ", body)
    print("################################################")
    if 'action' in body and body['action'] == 'add':
        ret = backend.add_tag(body['item'])    
	print("**************************************************************",ret)
    else:
        ret['status'] = 422
        ret['body']   = {'status': 'failure', 'message': 'Missing Header'}


    return Response(response=dumps(ret['body']), status=ret['status'])

@application.route('/v1/blocks/',     methods=['GET', 'POST'])
@application.route('/v1/blocks',      methods=['GET', 'POST'])
@cross_origin()
def urlBlocks():
    if request.method == 'GET':
        args = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = components.query_blocks(args)
        return Response(response=dumps(ret['body']), status=ret['status'])
    elif request.method == 'POST':
        if 'X-PRIVATE-APIKEY' in request.headers:
            private_key = request.headers.get('X-PRIVATE-APIKEY')
            if private_key == CAWAS:
                body = loads(request.data)
                if body['action'] == 'add':
                    ret  = components.add_block(body['item'])
                elif body['action'] == 'del':
                    ret  = components.del_block(body['item'])
            else:
                ret['status'] = 401
                ret['body']   = {'status': 'failure', 'message': 'Unauthorized'}
        else:
            ret['status'] = 422
            ret['body']   = {'status': 'failure', 'message': 'Missing Header'}


        return Response(response=dumps(ret['body']), status=ret['status'])


@application.route('/v1/channels/',     methods=['GET', 'POST'])
@application.route('/v1/channels',      methods=['GET', 'POST'])
@cross_origin()
def urlChannels():
    if request.method == 'GET':
        args = {}
        args['lang'] = 'none'   # Hardcoding
        ret = components.query_channels(args)
        return Response(response=dumps(ret['body']), status=ret['status'])
    elif request.method == 'POST':
        if 'X-PRIVATE-APIKEY' in request.headers:
            private_key = request.headers.get('X-PRIVATE-APIKEY')
            if private_key == CAWAS:
                body = loads(request.data)
                if body['action'] == 'add':
                    body['item']['lang'] = 'none'
                    ret  = components.add_channel(body['item'])
                elif body['action'] == 'del':
                    body['item']['lang'] = 'none'
                    ret  = components.del_channel(body['item'])
            else:
                ret['status'] = 401
                ret['body']   = {'status': 'failure', 'message': 'Unauthorized'}
        else:
            ret['status'] = 422
            ret['body']   = {'status': 'failure', 'message': 'Missing Header'}


        return Response(response=dumps(ret['body']), status=ret['status'])


#------------------------------------------------------------------------------------------------------------------------
#       Assets: Shows (Movies, Series) and Girls
#------------------------------------------------------------------------------------------------------------------------
@application.route('/v1/search/', methods=['GET'])
@application.route('/v1/search',  methods=['GET'])
@cross_origin()
def urlSearch():
    args = {}
    for k in request.args.keys():
        args[k] = request.args.get(k)
    ret  = backend.search(args)


    return Response(response=dumps(ret['body']), status=ret['status'])

@application.route('/v1/suggest/<string:asset_id>/', methods=['GET'])
@application.route('/v1/suggest/<string:asset_id>',  methods=['GET'])
@cross_origin()
def urlSuggest(asset_id):
    if request.method == 'GET':
        args = {}
        args['asset_id'] = asset_id
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = backend.suggest(args)
	
	if ret['status'] == 200:
	    if 'X-API-KEY' in request.headers and backend.resume is not None:
		x_api_key = request.headers.get('X-API-KEY')
    		ret_auth  = authorization.check_api_key(x_api_key)
    		if ret_auth['status'] == 200:
        	    username = ret_auth['body']['username']
        	    resume_list =  backend.query_resume(username)
		    #{'status': 200, 'body': 
		    #	{
		    #	   'count': 1, 
		    #	   'items': [{u'asset_id': u'018123', u'username': u'UN_hotgo_npajoni', u'asset_user': u'018123_UN_hotgo_npajoni', u'seekto': u'15.0', u'progress': u'12'}], 
		    #	   'total': 1
		    #   }
		    #}
		    #
		    if resume_list['body']['count'] > 0:
			for asset in resume_list['body']['items']:
			    i = 0
			    while i < ret['body']['count']:
				if asset['asset_id'] == ret['body']['items'][i]['asset_id']:
				    ret['body']['items'][i]['viewed'] = {}
				    if 'progress' in asset:
					ret['body']['items'][i]['viewed']['progress'] = asset['progress']
				    if 'seekto' in asset:
					ret['body']['items'][i]['viewed']['seekto'] = asset['seekto']
				    if 'season' in asset:
					ret['body']['items'][i]['viewed']['season'] = asset['season']
				    if 'episode' in asset:
					ret['body']['items'][i]['viewed']['episode'] = asset['episode']
				i = i + 1


        return Response(response=dumps(ret['body']), status=ret['status'])

@application.route('/v1/episodes/', methods=['GET'])
@application.route('/v1/episodes',  methods=['GET'])
@cross_origin()
def urlEpisode():
    if request.method == 'GET':
        args  = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = backend.query_episode(args)

	if ret['status'] == 200:
	    if 'X-API-KEY' in request.headers and backend.resume is not None:
		x_api_key = request.headers.get('X-API-KEY')
    		ret_auth  = authorization.check_api_key(x_api_key)
    		if ret_auth['status'] == 200:
        	    username = ret_auth['body']['username']
        	    resume_list =  backend.query_resume(username)
		    #{'status': 200, 'body': 
		    #	{
		    #	   'count': 1, 
		    #	   'items': [{u'asset_id': u'018123', u'username': u'UN_hotgo_npajoni', u'asset_user': u'018123_UN_hotgo_npajoni', u'seekto': u'15.0', u'progress': u'12'}], 
		    #	   'total': 1
		    #   }
		    #}
		    #
		    if resume_list['body']['count'] > 0:
			for asset in resume_list['body']['items']:
			    i = 0
			    while i < ret['body']['count']:
				if asset['asset_id'] == ret['body']['items'][i]['asset_id']:
				    ret['body']['items'][i]['viewed'] = {}
				    if 'progress' in asset:
					ret['body']['items'][i]['viewed']['progress'] = asset['progress']
				    if 'seekto' in asset:
					ret['body']['items'][i]['viewed']['seekto'] = asset['seekto']
				    if 'season' in asset:
					ret['body']['items'][i]['viewed']['season'] = asset['season']
				    if 'episode' in asset:
					ret['body']['items'][i]['viewed']['episode'] = asset['episode']
				i = i + 1

	for item in ret['body']['items']:
	    if not 'title' in item and 'name' in item:
		item['title'] = item['name']
        return Response(response=dumps(ret['body']), status=ret['status'])


@application.route('/v1/trends/', methods=['GET'])
@application.route('/v1/trends', methods=['GET'])
@cross_origin()
def urlTrends():
    if request.method == 'GET':
	args = {}
	for k in request.args.keys():
	    args[k] = request.args.get(k)
	ret = backend.query_trends(args)

	return Response(response=dumps(ret['body']), status=ret['status'])

#@application.route('/v1/episodes/<string:asset_id>/', methods=['GET'])
@application.route('/v1/shows/', methods=['GET'])
@application.route('/v1/shows',  methods=['GET'])
@cross_origin()
def urlShow():
    if request.method == 'GET':
        args  = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
	if 'mode' in args:
	    if args['mode'] == 'full':
		ret = backend.query_show_full(args)
	    elif args['mode'] == 'half':
		ret = backend.query_show_half(args)
	    else:
		ret = {}
		ret['body']   = {'status': 'failure', 'message': 'Invalid Argument: mode=%s' % args['mode']}
        	ret['status'] = 422
	else:
    	    ret = backend.query_show_full(args)

	if ret['status'] == 200:
	    if 'X-API-KEY' in request.headers and backend.resume is not None:
		x_api_key = request.headers.get('X-API-KEY')
    		ret_auth  = authorization.check_api_key(x_api_key)
    		if ret_auth['status'] == 200:
        	    username = ret_auth['body']['username']
        	    resume_list =  backend.query_resume(username)
		    #{'status': 200, 'body': 
		    #	{
		    #	   'count': 1, 
		    #	   'items': [{u'asset_id': u'018123', u'username': u'UN_hotgo_npajoni', u'asset_user': u'018123_UN_hotgo_npajoni', u'seekto': u'15.0', u'progress': u'12'}], 
		    #	   'total': 1
		    #   }
		    #}
		    if resume_list['body']['count'] > 0:
			for asset in resume_list['body']['items']:
			    i = 0
			    while i < ret['body']['count']:
				if asset['asset_id'] == ret['body']['items'][i]['asset_id']:
				    ret['body']['items'][i]['viewed'] = {}
				    if 'progress' in asset:
					ret['body']['items'][i]['viewed']['progress'] = asset['progress']
				    if 'seekto' in asset:
					ret['body']['items'][i]['viewed']['seekto'] = asset['seekto']
				    if 'season' in asset:
					ret['body']['items'][i]['viewed']['season'] = asset['season']
				    if 'episode' in asset:
					ret['body']['items'][i]['viewed']['episode'] = asset['episode']
				i = i + 1

	    i = 0
	    for asset in ret['body']['items']:
		if 'show_type' in asset and asset['show_type'] == 'serie' and 'lang' in args:
		    serie = backend.get_show({'asset_id': asset['asset_id'], 'lang': args['lang'] }, None, False)
		    if 'body' in serie and 'item' in serie['body'] and 'available_seasons' in serie['body']['item']:
			ret['body']['items'][i]['available_seasons'] = serie['body']['item']['available_seasons']
                i = i + 1
        return Response(response=dumps(ret['body']), status=ret['status'])


@application.route('/v1/vote/', methods=['POST'])
@application.route('/v1/vote',  methods=['POST'])
@cross_origin()
def urlVote():
    if request.method == 'POST':
        ret = {}
	try:
    	    data = loads(request.data)
	except Exception as e:
	    ret['body']   = {'status': 'failure', 'message': 'Invalid Argument: %s' % str(e)}
            ret['status'] = 422
	    return Response(response=dumps(ret['body']), status=ret['status'])

    	if 'asset_id' in data:
            if 'voted' in data:
                asset_id = data['asset_id']
                voted    = data['voted']
            
                if 'X-API-KEY' in request.headers:
                    x_api_key = request.headers.get('X-API-KEY')
                    ret       = authorization.check_api_key(x_api_key)
                    if ret['status'] == 200:
                        username = ret['body']['username']
                        ret = backend.doVote(data['asset_id'], username, data['voted'])
                else:
                    ret['body']     = {'status': 'failure', 'message': 'Missing header'}
                    ret['status']   = 401
            else:
                ret['body']   = {'status': 'failure', 'message': 'Invalid Argument'}
                ret['status'] = 422
        else:
            ret['body']   = {'status': 'failure', 'message': 'Invalid Argument'}
            ret['status'] = 422

        return Response(response=dumps(ret['body']), status=ret['status'])

@application.route('/v1/shows/<string:asset_id>/', methods=['GET'])
@application.route('/v1/shows/<string:asset_id>',  methods=['GET'])
@cross_origin()
def urlGetShow(asset_id):
    ret  = {}
    args = {}
    args['asset_id'] = asset_id
    for k in request.args.keys():
        args[k] = request.args.get(k)

    if 'video' in args:
	if args['video'] == 'false':
	    video = False
	else:
	    video = True
    else:
	video = True
    
    if video:
	if 'X-API-KEY' in request.headers:
	    x_api_key = request.headers.get('X-API-KEY')
    	    ret       = authorization.check_api_key(x_api_key)
    	    if ret['status'] == 200:
        	username = ret['body']['username']
        	ret      = backend.get_show(args, username)
	else:
	    if 'IDP-X-API-KEY' in request.headers and 'TOOLBOX-USER-TOKEN' in request.headers:
		ret = backend.get_show(args, None,True, False,request.headers['IDP-X-API-KEY'],request.headers['TOOLBOX-USER-TOKEN'] )
	    else:
		ret['body']     = {'status': 'failure', 'message': 'Missing header'}
    		ret['status']   = 401

    else:
	ret = backend.get_show(args, None,False)
    return Response(response=dumps(ret['body']), status=ret['status'])


@application.route('/v1/shows_hid/<string:human_id>/', methods=['GET'])
@application.route('/v1/shows_hid/<string:human_id>',  methods=['GET'])
@cross_origin()
def urlGetShowByHumanId(human_id):
    ret = {}
    args = {}
    args['human_id'] = human_id
    for k in request.args.keys():
        args[k] = request.args.get(k)

    if 'video' in args:
	if args['video'] == 'false':
	    video = False
	else:
	    video = True
    else:
	video = True
    
    if video:
	if 'X-API-KEY' in request.headers:
	    x_api_key = request.headers.get('X-API-KEY')
    	    ret       = authorization.check_api_key(x_api_key)
    	    if ret['status'] == 200:
		print ret
        	username = ret['body']['username']
        	ret      = backend.get_show_by_human_id(args, username)
	else:
	    if 'IDP-X-API-KEY' in request.headers and 'TOOLBOX-USER-TOKEN' in request.headers:
		ret = backend.get_show_by_human_id(args, None,True, False,request.headers['IDP-X-API-KEY'],request.headers['TOOLBOX-USER-TOKEN'] )
	    else:
		ret['body']     = {'status': 'failure', 'message': 'Missing header'}
    		ret['status']   = 401

    else:
	ret = backend.get_show_by_human_id(args, None,False)
        
    return Response(response=dumps(ret['body']), status=ret['status'])


@application.route('/v1/girls/', methods=['GET'])
@application.route('/v1/girls',  methods=['GET'])
@cross_origin()
def urlGirl():
    if request.method == 'GET':
        args  = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = backend.query_girl(args)
        return Response(response=dumps(ret['body']), status=ret['status'])

@application.route('/v1/girls/<string:asset_id>/', methods=['GET'])
@application.route('/v1/girls/<string:asset_id>',  methods=['GET'])
@cross_origin()
def urlGetGirl(asset_id):
    args = {}
    args['asset_id'] = asset_id
    for k in request.args.keys():
        args[k] = request.args.get(k)
    ret = backend.get_girl(args)
    return Response(response=dumps(ret['body']), status=ret['status'])


@application.route('/v1/girls_hid/<string:human_id>/', methods=['GET'])
@application.route('/v1/girls_hid/<string:human_id>',  methods=['GET'])
@cross_origin()
def urlGetGirlByHumanId(human_id):
    args = {}
    args['human_id'] = human_id
    for k in request.args.keys():
        args[k] = request.args.get(k)
    ret = backend.get_girl_by_human_id(args)
    return Response(response=dumps(ret['body']), status=ret['status'])


@application.route('/v1/assets/<string:block_id>/', methods=['GET'])
@application.route('/v1/assets/<string:block_id>',  methods=['GET'])
@cross_origin()
def urlAssetBlock(block_id):
    args = {}
    args['blocks'] = block_id
    for k in request.args.keys():
        args[k] = request.args.get(k)
    ret = backend.query_block(args)
    return Response(response=dumps(ret['body']), status=ret['status'])

#--------------------------------------------------------------------------------------------
# Private Methods
#--------------------------------------------------------------------------------------------
@application.route('/v1/private/authorize/', methods=['POST'])
@cross_origin()
def urlAuthorize():
    #
    # Falta mecanismo de validacion
    if 'X-MA-API-KEY' in request.headers:
        ma_api_key = request.headers.get('X-MA-API-KEY')
        if MA != ma_api_key:
            ret = {}
            ret['status'] = 401
            ret['body']   = {'status': 'failure', 'message': 'Invalid api key'}
            return Response(response=dumps(ret['body']), status=ret['status'])
    else:
        ret = {}
        ret['status'] = 401
        ret['body']   = {'status': 'failure', 'message': 'Missing Header'}
        return Response(response=dumps(ret['body']), status=ret['status']) 

    try:
        user_data = loads(request.data)
    except Exception as e:
        ret = {}
        ret['status'] = 422
        ret['body']   = {'status': 'failure', 'message': 'Invalid body format, we expect a JSON %s' % str(e)}
        return Response(response=dumps(ret['body']), status=ret['status'])

    try:
        ret = authorization.authorize(user_data)
    except Exception as e:
        ret = {}
        ret['status'] = 500
        ret['body']   = {'status': 'failure', 'message': str(e)}

    return Response(response=dumps(ret['body']), status=ret['status'])


@application.route('/v1/private/resume/', methods=['POST'])
@cross_origin()
def urlResume():
    if request.method == 'POST':
        if 'X-PRIVATE-APIKEY' in request.headers:
            private_key = request.headers.get('X-PRIVATE-APIKEY')
            if private_key == GATRA:
                body = loads(request.data)
		if 'asset_user' in body and 'asset_id' in body and 'username' in body:
		    ret_show = backend.get_show({'lang':'es', 'asset_id': body['asset_id']}, None,False)
		    if ret_show['body']['item']['show_type'] == 'episode':
			serie = {}
			serie['username']  = body['username']
			serie['timestamp'] = body['timestamp']
			serie['country'] = body['country']
			serie['asset_id'] = ret_show['body']['item']['serie_id']
			serie['asset_user'] = serie['asset_id'] + '_' + serie['username']
			serie['episode'] = ret_show['body']['item']['episode']
			serie['season'] = ret_show['body']['item']['season']
			backend.add_resume(serie)
                    ret  = backend.add_resume(body)
            else:
                ret = {}
                ret['status'] = 401
                ret['body']   = {'status': 'failure', 'message': 'Unauthorized'}
        else:
            ret = {}
            ret['status'] = 422
            ret['body']   = {'status': 'failure', 'message': 'Missing Header'}

    return Response(response=dumps(ret['body']), status=ret['status'])

@application.route('/v1/private/assets/', methods=['POST'])
@cross_origin()
def urlAsset():
    if request.method == 'POST':
        if 'X-PRIVATE-APIKEY' in request.headers:
            private_key = request.headers.get('X-PRIVATE-APIKEY')
            if private_key == CAWAS:
                body = loads(request.data)
                if body['action']   == 'add':
                    ret  = backend.add_asset(body['item'])
                elif body['action'] == 'del':
                    ret  = backend.disable_asset(body['item'])
                elif body['action'] == 'update':
                    ret  = backend.update_asset(body['item'])
            else:
                ret = {}
                ret['status'] = 401
                ret['body']   = {'status': 'failure', 'message': 'Unauthorized'}
        else:
            ret = {}
            ret['status'] = 422
            ret['body']   = {'status': 'failure', 'message': 'Missing Header'}

        
        return Response(response=dumps(ret['body']), status=ret['status'])


@application.route('/v1/prices/', methods=['POST', 'GET'])
@cross_origin()
def urlPrices():
    if request.method == 'POST':
    	body = loads(request.data)
	a = body['item']
	f = open("prices.json", 'wt')
	f.write(dumps(a))
	f.close()
        return Response(response=201, status={})

    ret = {}
    ret['status'] = 200
    f = open('prices.json')
    ret['body']   = loads(f.read())
    f.close()
    return Response(response=dumps(ret['body']), status=ret['status'])

    
#--------------------------------------------------------------------------------------------
# Updates
#--------------------------------------------------------------------------------------------

@application.route('/v1/private/addview/<string:asset_id>', methods=['PUT'])
def urlAddView(asset_id):
    ret = backend.add_view(asset_id)
    return Response(response=dumps(ret['body']), status=ret['status'])

@application.route('/v1/private/updateview/<string:asset_id>', methods=['GET'])
def urlUpdateView(asset_id):
    ret = backend.update_view(asset_id)
    return Response(response=dumps(ret['body']), status=ret['status'])

@application.route('/v1/private/updateranking/<string:asset_id>', methods=['GET'])
def urlUpdateRanking(asset_id):
    ret = backend.update_ranking(asset_id)
    return Response(response=dumps(ret['body']), status=ret['status'])

#--------------------------------------------------------------------------------------------
# JWT Validator
#--------------------------------------------------------------------------------------------
@application.route('/v1/private/jwt/<string:token>/', methods=['GET'])
@application.route('/v1/private/jwt/<string:token>', methods=['GET'])
def validate_jwt(token):
    ret = {}
    try:
        ret['status'] = 200
        majwt         = jwt.decode(token, MA_SIGNATURE)
        if majwt['akey'] != '':
            valid,ttl     = authorization.check_api_key_nohttp(majwt['akey'])
            if valid:
                majwt['ttl']  = ttl
                ret['body']     = majwt
            else:
                ret['status'] = 401
                ret['body']   = {'status': 'failed', 'message': 'expired'}
        else:
            ret['body'] = majwt
    except Exception as e:
        ret['status'] = 401
        ret['body']   = {'status': 'failed', 'message': str(e)}
    return Response(response=dumps(ret['body']), status=ret['status'])

@application.route('/v1/app/android/version/', methods=['GET'])
@application.route('/v1/app/android/version', methods=['GET'])
def app_android_version():
    ret = {}
    try:
        if 'X-APP-QUERY' in request.headers:
            private_key = request.headers['X-APP-QUERY']
            if private_key == APP_QUERY or True:
                ret['status'] = 200
                f = open('android_app_ver.json')
                ret['body']   = f.read()
                f.close()
            else:
                ret['status'] = 401
                ret['body']   = dumps({'status': 'failed', 'message':'Unauthorized'})
        else:
            ret['status'] = 401
            ret['body']   = dumps({'status': 'failed', 'message':'Unauthorized'})

    except Exception as e:
        ret['status'] = 401
        ret['body']   = dumps({'status': 'failed', 'message': str(e)})
    return Response(response=ret['body'], status=ret['status'])

#--------------------------------------------------------------------------------------------
# Ester Egg
#--------------------------------------------------------------------------------------------
@application.route('/v1/private/author/easteregg/8===D/', methods=['GET'])
def ea():
    with open('./ea') as f:
        html = f.read()
    return Response(response=html, status=200)


@application.route('/v1/footer/<string:country>/', methods=['GET'])
@application.route('/v1/footer/<string:country>', methods=['GET'])
@cross_origin()
def footer(country):
    path = 'statics/footer/'
    if os.path.exists(path + country):
        path = path + country
    else:
        path = path + 'default'

    with open(path, 'r') as f:
        footer = f.read()
        ret = {'footer': footer}

    return Response(response=dumps(ret), status=200) 



if __name__ == "__main__":
    application.run("0.0.0.0", 8000)
#    application.run()

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
##
# Keys
##
import jwt
from keys   import MA
from keys   import CAWAS
from keys   import MA_SIGNATURE

application = Flask(__name__)


backend = Backend({"languages": ['es','pt'], 
                    "girls":
                        {"database": {
                            "table": "Girls",
                            "pk": "lang",
                            "sk": "asset_id",
                            "schema": {
                                    "lang": "S",
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
                            "schema": {
                                    "lang": "S",
                                    "asset_id": "S",
                                    "title": "S",
                                    "summary_short": "S",
                                    "display_runtime": "S",
                                    "runtime": "N",
                                    "seasons": "N",
                                    "episodes": "N",
                                    "season": "N",
                                    "episode": "N",
                                    "categories": "SS",
                                    "year": "N",
                                    "image_portrait": "S",
                                    "image_landscape": "S",
                                    "views": "N",
                                    "ranking": "N",
                                    "show_type": "S",
                                    "asset_type": "S",
                                    "blocks": "SS",
                                    "channel": "S",
                                    "serie_id": "S",
                                    "available_seasons": "SS",
                                    "girls_id": "SS",
                                    "girls_name": "SS",
                                    "girls_display": "SS",
                                    "publish_date": "N",
                                    "summary_long": "S",
                                    "cast":"S",
                                    "directors":"S",
                                    "enabled": "N",
                                    "thumbnails": "S",
                                    "subtitle": "S",
                            },
                         }},
                        "ranking": {'table_name': 'Ranking', 'commit_index': 'lala'},
                        "views" : {'table_name': 'Views', 'commit_index':'lala'},
                        "asset_type": {'database': {'table': 'AssetType', 'pk': 'asset_id', 'schema': {'asset_id': 'S', 'asset_type':'S'}}},
                        "vote": {'database': {'table': 'Vote', 'pk': 'asset_id', 'sk':'username', 'schema': {'asset_id': 'S', 'username':'S', 'voted':'N'}}},
                        "search_domain": {'es' : {"domain": {
                                                        "id_field": "asset_id",
                                                        "filter_query" : '',
                                                        "schema": ["channel","asset_id", "title","summary_short","display_runtime","seasons","season","episode","episodes","categories","show_type","year","serie_id","girls_id","name", "image_big", "image_landscape", "image_portrait", "views", "ranking", "asset_type", "blocks", "publish_date", "class", "summary_long", "nationality"],
                                                        "return_fields": ["asset_id", "name", "title", "ranking", "views","display_runtime", "summary_short" ,"categories", "image_landscape", "image_portrait", "channel", "show_type","asset_type", "year", "seasons", "class","episodes", "episode", "serie_id"],
                                                        "name" : "eshotgodomain",
                                                        }
                                                 },
                                          'pt' : {"domain": {
                                                        "id_field": "asset_id",
                                                        "filter_query" : '',
                                                        "schema": ["channel","asset_id", "title","summary_short","display_runtime","seasons","season","episode","episodes","categories","show_type","year","serie_id","girls_id","name", "image_big", "image_landscape", "image_portrait", "views", "ranking", "asset_type", "blocks", "publish_date", "class", "summary_long", "nationality"],
                                                        "return_fields": ["asset_id", "name", "title", "ranking", "views","display_runtime", "summary_short" ,"categories", "image_landscape", "image_portrait", "channel", "show_type","asset_type", "year", "seasons", "class","episodes", "episode", "serie_id"],
                                                        "name" : "pthotgodomain",
                                                        }
                                                 }
                                         }
                    })



components = Components({
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
                            "media_type": "S",
                            "linked_asset_id": "S",
                            "linked_asset_type": "S",
                            "target": "S"
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
                            "order": "N",
                            "channel": "S",
                            "target": "S",
                        },
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
                    ret  = components.add_slider(body['item'])
                elif body['action'] == 'del':
                    ret  = components.del_slider(body['item'])
            else:
                ret['status'] = 401
                ret['body']   = {'status': 'failure', 'message': 'Unauthorized'}
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
        ret = backend.query_show(args)
        return Response(response=dumps(ret['body']), status=ret['status'])


@application.route('/v1/vote/', methods=['POST'])
@application.route('/v1/vote',  methods=['POST'])
@cross_origin()
def urlVote():
    if request.method == 'POST':
        ret = {}
        data = loads(request.data)
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
    ret = {}
    if 'X-API-KEY' in request.headers:
        x_api_key = request.headers.get('X-API-KEY')
        ret       = authorization.check_api_key(x_api_key)
        if ret['status'] == 200:
            args = {}
            args['asset_id'] = asset_id
            for k in request.args.keys():
                args[k] = request.args.get(k)
            username = ret['body']['username']
            ret      = backend.get_show(args, username)
    else:
        ret['body']     = {'status': 'failure', 'message': 'Missing header'}
        ret['status']   = 401

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
                ret[body]     = majwt
            else:
                ret['status'] = 401
                ret['body']   = {'status': 'failed', 'message': 'expired'}
        else:
            ret[body] = majwt
    except Exception as e:
        ret['status'] = 401
        ret['body']   = {'status': 'failed', 'message': str(e)}
    return Response(response=dumps(ret['body']), status=ret['status'])
#--------------------------------------------------------------------------------------------
# Ester Egg
#--------------------------------------------------------------------------------------------
@application.route('/v1/private/author/easteregg/8===D/', methods=['GET'])
def ea():
    with open('./ea') as f:
        html = f.read()
    return Response(response=html, status=200)


if __name__ == "__main__":
    application.run("0.0.0.0", 8000)
#    application.run()
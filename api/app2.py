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

api = Flask(__name__)


backend = Backend({"girls":
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
                                    "girls_id": "SS",
                                    "girls_name": "SS",
                                    "girls_display": "SS",
                                    "publish_date": "N",
                                    "summary_long": "S",
                                    "cast":"S",
                                    "directors":"S",
                                    "enabled": "N",
                            },
                         }},
                        "views" : {'table_name': 'Views', 'commit_index':'lala'},
                        "asset_type": {'database': {'table': 'AssetType', 'pk': 'asset_id', 'schema': {'asset_id': 'S', 'asset_type':'S'}}},
                       "search_domain": {"domain": {
                                        "id_field": "asset_id",
                                        "filter_query" : '',
                                        "schema": ["channel","asset_id", "title","summary_short","display_runtime","seasons","season","episode","episodes","categories","show_type","year","serie_id","girls_id","name", "image_big", "image_landscape", "image_portrait", "views", "ranking", "asset_type", "blocks", "publish_date", "class", "summary_long", "nationality"],
                                        "return_fields": ["asset_id", "name", "title", "ranking", "views","display_runtime", "summary_short" ,"categories", "image_landscape", "image_portrait", "channel", "show_type", "year", "seasons", "class","episodes"],
                                        "name" : "eshotgodomain",
                                    }}
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
                            "linked_asset_type": "S"
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
                            "channel": "S",
                        },
                    }
                }
            })


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

@api.route('/v1/categories/', methods=['GET', 'POST'])
@cross_origin()
def urlCategories():
    if request.method == 'GET':
        args = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = components.query_categories(args)
        return Response(response=dumps(ret['body']), status=ret['status'])
    elif request.method == 'POST':
        body = loads(request.data)
        if body['action'] == 'add':
            ret  = components.add_category(body['item'])
        elif body['action'] == 'del':
            ret  = components.del_category(body['item'])
        return Response(response=dumps(ret['body']), status=ret['status'])

@api.route('/v1/sliders/',    methods=['GET', 'POST'])
@cross_origin()
def urlSliders():
    if request.method == 'GET':
        args = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = components.query_sliders(args)
        return Response(response=dumps(ret['body']), status=ret['status'])
    elif request.method == 'POST':
        body = loads(request.data)
        if body['action'] == 'add':
            ret  = components.add_slider(body['item'])
        elif body['action'] == 'del':
            ret  = components.del_slider(body['item'])
        return Response(response=dumps(ret['body']), status=ret['status'])

@api.route('/v1/blocks/',     methods=['GET', 'POST'])
@cross_origin()
def urlBlocks():
    if request.method == 'GET':
        args = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = components.query_blocks(args)
        return Response(response=dumps(ret['body']), status=ret['status'])
    elif request.method == 'POST':
        body = loads(request.data)
        if body['action'] == 'add':
            ret  = components.add_block(body['item'])
        elif body['action'] == 'del':
            ret  = components.del_block(body['item'])
        return Response(response=dumps(ret['body']), status=ret['status'])


@api.route('/v1/channels/',     methods=['GET', 'POST'])
@cross_origin()
def urlChannels():
    if request.method == 'GET':
        args = {}
        args['lang'] = 'none'   # Hardcoding
        ret = components.query_channels(args)
        return Response(response=dumps(ret['body']), status=ret['status'])
    elif request.method == 'POST':
        body = loads(request.data)
        if body['action'] == 'add':
            body['item']['lang'] = 'none'
            ret  = components.add_channel(body['item'])
        elif body['action'] == 'del':
            body['item']['lang'] = 'none'
            ret  = components.del_channel(body['item'])
        return Response(response=dumps(ret['body']), status=ret['status'])


#------------------------------------------------------------------------------------------------------------------------
#       Assets: Shows (Movies, Series) and Girls
#------------------------------------------------------------------------------------------------------------------------
@api.route('/v1/search/', methods=['GET'])
@cross_origin()
def urlSearch():
    args = {}
    for k in request.args.keys():
        args[k] = request.args.get(k)
    ret  = backend.search(args)
    return Response(response=dumps(ret['body']), status=ret['status'])

@api.route('/v1/suggest/<string:asset_id>', methods=['GET'])
@cross_origin()
def urlSuggest(asset_id):
    if request.method == 'GET':
        args = {}
        args['asset_id'] = asset_id
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = backend.suggest(args)
        return Response(response=dumps(ret['body']), status=ret['status'])

@api.route('/v1/episodes/', methods=['GET'])
@cross_origin()
def urlEpisode():
    if request.method == 'GET':
        args  = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = backend.query_episode(args)
        return Response(response=dumps(ret['body']), status=ret['status'])

#@api.route('/v1/episodes/<string:asset_id>/', methods=['GET'])

@api.route('/v1/shows/', methods=['GET'])
@cross_origin()
def urlShow():
    if request.method == 'GET':
        args  = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = backend.query_show(args)
        return Response(response=dumps(ret['body']), status=ret['status'])


@api.route('/v1/shows/<string:asset_id>/', methods=['GET'])
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
            ret = backend.get_show(args)
    else:
        ret['body']     = {'status': 'failure', 'message': 'Missing header'}
        ret['status']   = 401

    return Response(response=dumps(ret['body']), status=ret['status'])


@api.route('/v1/girls/', methods=['GET'])
@cross_origin()
def urlGirl():
    if request.method == 'GET':
        args  = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = backend.query_girl(args)
        return Response(response=dumps(ret['body']), status=ret['status'])


@api.route('/v1/girls/<string:asset_id>/', methods=['GET'])
@cross_origin()
def urlGetGirl(asset_id):
    args = {}
    args['asset_id'] = asset_id
    for k in request.args.keys():
        args[k] = request.args.get(k)
    ret = backend.get_girl(args)
    return Response(response=dumps(ret['body']), status=ret['status'])

@api.route('/v1/assets/<string:block_id>/', methods=['GET'])
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
@api.route('/v1/private/authorize/', methods=['POST'])
@cross_origin()
def urlAuthorize():
    #
    # Falta mecanismo de validacion
    user_data = loads(request.data)
    ret = authorization.authorize(user_data)
    return Response(response=dumps(ret['body']), status=ret['status'])

@api.route('/v1/private/assets/', methods=['POST'])
@cross_origin()
def urlAsset():
    print request.method
    if request.method == 'POST':
        body = loads(request.data)
        if body['action']   == 'add':
            ret  = backend.add_asset(body['item'])
        elif body['action'] == 'del':
            ret  = backend.disable_asset(body['item'])
        elif body['action'] == 'update':
            ret  = backend.update_asset(body['item'])
        return Response(response=dumps(ret['body']), status=ret['status'])
    
@api.route('/v1/private/addview/<string:asset_id>', methods=['PUT'])
def urlAddView(asset_id):
    ret = backend.add_view(asset_id)
    return Response(response=dumps(ret['body']), status=ret['status'])

@api.route('/v1/private/updateview/<string:asset_id>', methods=['GET'])
def urlUpdateView(asset_id):
    ret = backend.update_view(asset_id)
    return Response(response=dumps(ret['body']), status=ret['status'])
#--------------------------------------------------------------------------------------------
# Hooks
#--------------------------------------------------------------------------------------------
@api.route('/v1/hooks/update_views/', methods=['UPDATE'])
def urlHooksUpdateViews():
    pass


if __name__ == "__main__":
    api.run("0.0.0.0", 8000)
#    api.run()
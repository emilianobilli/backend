from flask import Flask
from flask import request
from flask import redirect
from flask import Response
from flask_cors import CORS, cross_origin
from backend import Backend
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
                                    "image_big": "S",
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
                                    "image_big": "S",
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
                       "search_domain": {"domain": {
                                        "id_field": "asset_id",
                                        "filter_query" : '',
                                        "schema": ["channel","asset_id", "title","summary_short","display_runtime","seasons","season","episode","categories","show_type","year","serie_id","girls_id","name", "image_big", "image_landscape", "image_portrait", "views", "ranking", "asset_type", "blocks", "publish_date", "class", "summary_long", "nationality"],
                                        "return_fields": ["asset_id"],
                                        "name" : "eshotgodomain",
                                    }}
                    })


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
    args = {}
    args['asset_id'] = asset_id
    for k in request.args.keys():
        args[k] = request.args.get(k)
    ret = backend.get_show(args)
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



@api.route('/v1/assets/', methods=['POST'])
@cross_origin()
def urlAsset():
    print request.method
    if request.method == 'POST':
        body = loads(request.data)
        if body['action'] == 'add':
            ret  = backend.add_asset(body['item'])
        elif body['action'] == 'del':
            ret  = backend.disable_asset(body['item'])
        return Response(response=dumps(ret['body']), status=ret['status'])
    




if __name__ == "__main__":
#    api.run("0.0.0.0", 8000)
    api.run()
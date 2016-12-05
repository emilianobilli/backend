from flask import Flask
from flask import request
from flask import redirect
from flask import Response
from flask_cors import CORS, cross_origin
from models import Backend
from json   import dumps 
from json   import loads

api = Flask(__name__)


backend = Backend({ "blocks" : 
                        {"database": {
                            "table": "Blocks",
                            "pk": "lang",
                            "sk": "block_id",
                            "schema": {
                                "lang":  "S",
                                "block_id":  "S",
                                "block_name": "S",
                                "channel":   "S"
                            }
                       }},
                     "sliders":
                        {"database": {
                            "table": "Sliders",
                            "pk": "lang",
                            "sk": "slider_id",
                            "schema": {
                                "lang":  "S",
                                "slider_id":  "S",
                                "media_url":  "S",
                                "media_type": "S",
                                "linked_asset_id": "S",
                                "linked_asset_type": "S",
                                "text" : "S",
                            }
                       }},
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
                                    "weight": "S"
                            }
                         }},
                       "categories":
                          {"database": {
                            "table": "Categories",
                            "pk": "lang",
                            "sk": "name",
                            "schema": {
                                "lang":  "S",
                                "name":  "S",
                                "order":  "N",
                                "image_big" : "S",
                                "image_landscape": "S",
                                "image_portrait": "S"
                            }
                       }},
                       "search_domain": {"domain": {
                                        "id_field": "house_id",
                                        "filter_query" : '',
                                        "schema": [],
                                        "return_fields": [],
                                        "name" : "sdhotgotest",
                                    }}
                    })


'''
channel = dbCollection({"database": {
                            "table": "Channels",
                            "pk": "name",
                    #        "sk": "slider_id",
                            "schema": {
                                "name":  "S",
                                "logo":  "S",
                            }
                       }})


girls    = dbseCollection({,
                         "search" : {
                            "pk": "lang",
                            "value": { 
                                "es": {
                                    "domain": {
                                        "id_field": "asset_id",
                                        "filter_query" : {'asset_type' : 'girl'},
                                        "schema": ["asset_id", "name", "image_big", "image_landscape", "image_portrait", "views", "ranking", "asset_type", "blocks", "publish_date", "class", "summary_long", "nationality"],
                                        "return_fields": [],
                                        "name" : "eshotgodomain",
                                    }
                                }
                            }
                        }})

'''
@api.route('/v1/shows/', methods=['GET'])
def urlShow():
    if request.method == 'GET':
        args  = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = backend.query_show(args)
        return Response(response=dumps(ret['body']), status=ret['status'])

@api.route('/v1/categories/', methods=['GET', 'POST', 'DELETE'])
@cross_origin()
def urlCategory():
    if request.method == 'GET':
        args  = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = backend.query_category(args)
        return Response(response=dumps(ret['body']), status=ret['status'])

    if request.method == 'POST':
        item = loads(request.get_json())
        ret  = backend.add_category(item)
        return Response(response=dumps(ret['body']), status=ret['status'])

    if request.method == 'DELETE':
        item = loads(request.get_json())
        ret  = backend.del_category(item)
        return Response(response=dumps(ret['body']), status=ret['status'])

@api.route('/v1/sliders/', methods=['GET', 'POST', 'DELETE'])
@cross_origin()
def urlSlider():
    if request.method == 'GET':
        args  = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = backend.query_slider(args)
        return Response(response=dumps(ret['body']), status=ret['status'])

    if request.method == 'POST':
        item = loads(request.get_json())
        ret  = backend.add_slider(item)
        return Response(response=dumps(ret['body']), status=ret['status'])

    if request.method == 'DELETE':
        item = loads(request.get_json())
        ret  = backend.del_slider(item)
        return Response(response=dumps(ret['body']), status=ret['status'])


@api.route('/v1/blocks/', methods=['GET', 'POST', 'DELETE'])
@cross_origin()
def urlBlock():
    if request.method == 'GET':
        args  = {}
        for k in request.args.keys():
            args[k] = request.args.get(k)
        ret = backend.query_block(args)
        return Response(response=dumps(ret['body']), status=ret['status'])

    if request.method == 'POST':
        item = loads(request.get_json())
        ret  = backend.add_block(item)
        return Response(response=dumps(ret['body']), status=ret['status'])

    if request.method == 'DELETE':
        item = loads(request.get_json())
        ret  = backend.del_block(item)
        return Response(response=dumps(ret['body']), status=ret['status'])



if __name__ == "__main__":
    api.run("0.0.0.0", 8000)

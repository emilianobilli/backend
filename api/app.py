from flask import Flask
from flask import request
from flask import redirect
from flask import Response
from flask_cors import CORS, cross_origin
from models import smallCollection
from json   import dumps 

api = Flask(__name__)

block = smallCollection({"database": {
                            "table": "Blocks",
                            "pk": "lang",
                            "sk": "block_id",
                            "schema": {
                                "lang":  "S",
                                "block_id":  "S",
                                "block_name": "S",
                                "channel":   "S"
                            }
                        }})


slider = smallCollection({"database": {
                            "table": "Sliders",
                            "pk": "lang",
                            "sk": "slider_id",
                            "schema": {
                                "lang":  "S",
                                "slider_id":  "S",
                                "media_url": "S",
                                "media_type": "S",
                                "linked_asset_id": "S",
                                "linked_asset_type": "S"
                            }
                        }})


@api.route('/v1/blocks/', methods=['GET', 'POST'])
@cross_origin()
def urlBlock():

    if request.method == 'GET':
        qArgs = request.args
        if 'lang' not in qArgs:
            return Response(status='400')

        return Response(response=dumps(block.query(qArgs['lang'])), status=200)

    if request.method == 'POST':

        item = request.get_json()
        ret  = block.add(item)
        if ret['status'] == 'success':
            status = 201
        else:
            status = 200

        return Response(response=dumps(ret), status=status)



if __name__ == "__main__":
    api.run("0.0.0.0", 8000)


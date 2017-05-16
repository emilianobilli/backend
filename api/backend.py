from Collection import dynamodbCollection
from Collection import cloudsearchCollection
from Collection import CollectionException
from Collection import DynamoException
from Collection import CloudSearchException
from Sub        import Subtitle
from views      import Views
from cdnimg     import CdnImg
from random     import randrange
from ranking    import Ranking

import json
import socket
import httplib2
import urlparse


class VideoAuthException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class VideoAuth(object):
    def __init__(self, ep=None, apikey=None):
        self.h      = httplib2.Http()
        self.apikey = apikey
        self.ep     = ep

    def doPost(self, asset_id):
        method = 'POST'
        url    = '%s/checkauth/' % self.ep
        body   = {'house_id': asset_id, 'api_key': self.apikey, 'toolbox_user_token': '' }
        uri    = urlparse.urlparse(url)
        return self.h.request(uri.geturl(),method,json.dumps(body),{'Content-type':'application/json'})

    def get_hls_url(self, asset_id):
        try:
            response,content = self.doPost(asset_id)
        except socket.error as err:
            raise VideoAuthException(err)
        
        if 'status' in response:
            if response['status'] == '200':
                ret = json.loads(content)
                return ret['hls']
            else:
                raise VideoAuthException(content)
        else:
            raise VideoAuthException('Flens')


class Components(object):
    def __init__(self, config):
        if 'channels' in config:
            self.channels   = dynamodbCollection(config['channels'])
        if 'categories' in config:
            self.categories = dynamodbCollection(config['categories'])
        if 'blocks' in config:
            self.blocks     = dynamodbCollection(config['blocks'])
        if 'sliders' in config:
            self.sliders    = dynamodbCollection(config['sliders'])

        self.images    = {}
        self.images['image_landscape'] = CdnImg(['http://cdnimages.zolechamedia.net/','http://cdnimages1.zolechamedia.net/','http://cdnimages2.zolechamedia.net/','http://cdnimages3.zolechamedia.net/','http://cdnimages4.zolechamedia.net/','http://cdnimages5.zolechamedia.net/'], 'landscape/')
        self.images['image_portrait']  = CdnImg(['http://cdnimages.zolechamedia.net/','http://cdnimages1.zolechamedia.net/','http://cdnimages2.zolechamedia.net/','http://cdnimages3.zolechamedia.net/','http://cdnimages4.zolechamedia.net/','http://cdnimages5.zolechamedia.net/'], 'landscape/')


    def __query(self, where, q, qfilter=None):
        try:
            ret    = where.query(q)
            ret    = self.__post_filter(ret, qfilter)
            ret    = self.__add_cdn_images(ret, None)
            status = 200
        except CollectionException as e:
            status = 422
            ret    = {'status': 'failure', 'message': str(e)}
        except DynamoException as e:
            ret    = {'status': 'failure', 'message': str(e)}
            status = 500
        except Exception as e:
            status = 500
            ret    = {'status': 'failure', 'message': str(e)}

        return {'status': status, 'body': ret}

    def __add(self, where, item):
        try:
            ret    = where.add(item)
            status = 201
        except CollectionException as e:
            status = 422
            ret    = {'status': 'failure', 'message': str(e)}
        except DynamoException as e:
            ret    = {'status': 'failure', 'message': str(e)}
            status = 500
        except Exception as e:
            status = 500
            ret    = {'status': 'failure', 'message': str(e)}

        return {'status': status, 'body': ret}


    def __del(self, where, item):
        try:
            ret    = where.delete(item)
        #    print ret
            status = 204
        except CollectionException as e:
            status = 422
            ret    = {'status': 'failure', 'message': str(e)}
        except DynamoException as e:
            ret    = {'status': 'failure', 'message': str(e)}
            status = 500
        except Exception as e:
            status = 500
            ret    = {'status': 'failure', 'message': str(e)}

        return {'status': status, 'body': ret}

    
    def parse_img_arg(self, field, img):
        try:
            i = json.loads(img)
            return i[field]
        except:
            return None
        return None

    def __add_cdn_images(self, response, imgArgs):
        items = response['items']
        ni = []
        for item in items:
            for k in self.images.keys():
                if k in item:
                    item[k] = self.images[k].getUrl(item[k], self.parse_img_arg(k,imgArgs))
            ni.append(item)
        response['items'] = ni
        return response

    def __post_filter(self, response, qfilter=None):
        #
        # Revisar este codigo
        # 
        if qfilter is None:
            return response

        ret = {}
        ret['items'] = []
        n            = 0
        key   = qfilter.keys()[0]
        value = qfilter[key]
        for item in response['items']:
            if key in item:
                if item[key] == value:
                    ret['items'].append(item)
                    n = n + 1
        ret['count'] = n
        return ret

    '''
        Add Methods for Slider, Block and Category
    '''
    def add_slider(self, Item={}):
        return self.__add(self.sliders, Item)

    def add_channel(self, Item={}):
        return self.__add(self.channels, Item)

    def add_block(self, Item={}):
        return self.__add(self.blocks, Item)

    def add_category(self, Item={}):
        return self.__add(self.categories, Item)

    '''
        Del Methods for Slider, Block and Category
    '''
    def del_block(self, Item={}):
        return self.__del(self.blocks, Item)

    def del_channel(self, Item={}):
        return self.__del(self.channels, Item)

    def del_category(self, Item={}):
        return self.__del(self.categories, Item)

    def del_slider(self, Item={}):
        return self.__del(self.sliders, Item)

    '''
        Query Methods for Slider, Block and Category
    '''
    def query_blocks(self, arg):
        if 'target' in arg:
            qfilter = {}
            qfilter['target'] = arg['target']
            return self.__query(self.blocks, arg, qfilter)
        else:
            return self.__query(self.blocks,arg)

    def query_sliders(self, arg):
        if 'target' in arg:
            qfiller = {}
            qfilter['target'] = arg['target']
            return self.__query(self.sliders,arg, qfilter)
        else:
            return self.__query(self.sliders,arg)

    def query_categories(self, arg):
        return self.__query(self.categories,arg)

    def query_channels(self, arg):
        return self.__query(self.channels, arg)

class Backend(object):
    def __init__(self, config):

        if 'languages' in config:
            self.lang       = config['languages']
        else:
            return None # Ojo con el error

        if 'shows' in config:
            self.shows      = dynamodbCollection(config['shows'])

        if 'girls' in config:
            self.girls      = dynamodbCollection(config['girls'])

        if 'search_domain' in config:
            self.domain     = {}
            for lang in self.lang:
                try:
                    self.domain[lang]  = cloudsearchCollection(config['search_domain'][lang])
                except:
                    return None # Ojo con el error

        if 'views' in config:
            self.views      = Views(config['views']['table_name'],config['views']['commit_index'])
        else:
            self.views      = None

        if 'ranking' in config:
            self.ranking    = Ranking(config['ranking']['table_name'],config['ranking']['commit_index'])

        if 'asset_type' in config:
            self.asset_type = dynamodbCollection(config['asset_type'])

        if 'vote' in config:
            self.vote       = dynamodbCollection(config['vote'])

        self.videoauth = VideoAuth("https://videoauth.zolechamedia.net/video/", "7a407d4ae99b7c1a1655daddf218ef05")
        self.subtitle  = Subtitle("http://videoauth.zolechamedia.net/subtitle")

        self.images    = {}
        self.images['image_landscape'] = CdnImg(['http://cdnimages.zolechamedia.net/','http://cdnimages1.zolechamedia.net/','http://cdnimages2.zolechamedia.net/','http://cdnimages3.zolechamedia.net/','http://cdnimages4.zolechamedia.net/','http://cdnimages5.zolechamedia.net/'], 'landscape/')
        self.images['image_portrait']  = CdnImg(['http://cdnimages.zolechamedia.net/','http://cdnimages1.zolechamedia.net/','http://cdnimages2.zolechamedia.net/','http://cdnimages3.zolechamedia.net/','http://cdnimages4.zolechamedia.net/','http://cdnimages5.zolechamedia.net/'], 'portrait/')


    def del_asset():     # borra asset
        pass

    def get_show(self, args, username):

        if 'lang' not in args or 'asset_id' not in args:
            status = 422
            ret    = {'status': 'failure', 'message': 'Mandatory argument not found'}
        else:
            item = {}
            item['lang']     = args['lang']
            item['asset_id'] = args['asset_id']
            asset_id         = None
            try:
                asset = self.shows.get(item)
                if asset['item'] != {} and asset['item']['enabled'] == "1":
                    if asset['item']['show_type'] == 'movie' or asset['item']['show_type'] == 'episode':
                        asset['item']['video'] = self.videoauth.get_hls_url(asset['item']['asset_id'])
                        asset_id = asset['item']['asset_id']
                    
                    if 'img' in args:
                        img = args['img']
                    else:
                        img = None

                    for k in self.images.keys():
                        if k in asset['item']:
                            asset['item'][k] = self.images[k].getUrl(asset['item'][k], self.parse_img_arg(k,img))

                    if asset_id is not None and self.views is not None:
                        self.views.add_view(asset_id)

                    n = int(asset['item']['ranking'])
                    if n > 0:
                        asset['item']['ranking'] = str(round(float(n)/25,2))

                    #
                    # Busca el voto del usuario
                    #
                    q = {}
                    q['asset_id'] = args['asset_id']
                    q['username'] = username
                    vote = self.vote.get(q)
                    if vote['item'] != {}:
                        asset['item']['voted'] = vote['item']['voted']

                    status = 200
                else:
                    asset['item'] = {} 
                    status = 404
                ret    = asset

            except CollectionException as e:
                status = 422
                ret    = {'status': 'failure', 'message': str(e)}
            except DynamoException as e:
                ret    = {'status': 'failure', 'message': str(e)}
                status = 500
            except VideoAuthException as e:
                ret    = {'status': 'failure', 'message': str(e)}
                status = 500
            except Exception as e:
                ret    = {'status': 'failure', 'message': str(e)}
                status = 500

        return {'status': status, 'body': ret}


    def parse_img_arg(self, field, img):
        try:
            i = json.loads(img)
            return i[field]
        except:
            return None
        return None

    def get_girl(self, args):
        if 'lang' not in args or 'asset_id' not in args:
            status = 422
            ret    = {'status': 'failure', 'message': 'Mandatory argument not found'}
        else:
            item = {}
            item['lang']     = args['lang']
            item['asset_id'] = args['asset_id']
            asset_id         = None
            try:
                asset = self.girls.get(item)
                if asset['item'] != {} and asset['item']['enabled'] == "1":
                    asset_id = asset['item']['asset_id']
                    status   = 200
                    n = int(asset['item']['ranking'])
                    if n > 0:
                        asset['item']['ranking'] = str(round(float(n)/25,2))
                    if 'img' in args:
                        img = args['img']
                    else:
                        img = None

                    for k in self.images.keys():
                        if k in asset['item']:
                            asset['item'][k] = self.images[k].getUrl(asset['item'][k], self.parse_img_arg(k,img))
            
                else:
                    asset['item'] = {} 
                    status = 404
    
                if asset_id is not None and self.views is not None:
                    self.views.add_view(asset_id)

                ret    = asset

            except CollectionException as e:
                status = 422
                ret    = {'status': 'failure', 'message': str(e)}
            except DynamoException as e:
                ret    = {'status': 'failure', 'message': str(e)}
                status = 500
            except VideoAuthException as e:
                ret    = {'status': 'failure', 'message': str(e)}
                status = 500
            except Exception as e:
                ret    = {'status': 'failure', 'message': str(e)}
                status = 500

        return {'status': status, 'body': ret}

    def get_asset():     # Trae chica, episodio, movie, serie (lang) -> Si es movie o episodio trae el video
        pass

    def add_view(self,asset_id):
        try:
            self.views.add_view(asset_id)
            status = 200
            ret    = {'message': 'OK'}
        except Exception as e:
            status = 500
            ret    = {'status': 'failure', 'message': str(e)}
        return {'status': status, 'body': ret}

    def doVote(self, asset_id, username, voted):
        update = False
        previous_vote = {}
        previous_vote['asset_id'] = asset_id
        previous_vote['username'] = username
        item          = {}
        item['asset_id'] = asset_id
        item['username'] = username

        try:
            ret = self.vote.get(previous_vote)
            if 'Item' in ret and ret['Item'] != {}:
                pvote = int(ret['Item']['voted'])
                update   = True
            else:
                pvote = 0
        except Exception as e:
            pvote = 0

        try:
            # Lo primero que se debe hacer es buscar el voto expedido
            item['voted'] = voted - pvote
            if update:
                self.ranking.update_vote(asset_id, item['voted'])
            else:
                self.ranking.add_vote(asset_id, item['voted'])
    
            ret = self.vote.add(item)
            status = 201


        except DynamoException as e:
            ret    = {'status': 'failure', 'message': str(e)}
            status = 500
        except Exception as e:
            status = 500
            ret    = {'status': 'failure', 'message': str(e)}

        return {'status': status, 'body': ret}


    def update_ranking(self, asset_id):
        lang = ['es'] # OJO QUE ESTA HARDCODEADA LA LISTA DE LENGUAJES
        try:
            asset_type = self.__get_asset_type(asset_id)
            if asset_type is not None:
                item = {}
                item['asset_id']   = asset_id
                item['asset_type'] = asset_type
                ranking = self.ranking.get_ranking(asset_id)
                if ranking != 0:
                    item['ranking']  = ranking
                for l in lang:
                    item['lang']   = l
                    ret            = self.update_asset(item)
                    if ret['status'] != 201:
                        return ret

                self.ranking.set_commited(asset_id)
                status = 200
                ret    = {'message': 'Asset updated'}
            else:
                status = 422
                ret    = {'status': 'failure', 'message': 'Invalid Asset Type'}

        except Exception as e:
            status = 500
            ret    = {'status': 'failure', 'message': str(e) }
        
        return {'status': status, 'body': ret}

    def update_view(self,asset_id):
        lang = ['es'] # OJO QUE ESTA HARDCODEADA LA LISTA DE LENGUAJES
        try:
            asset_type = self.__get_asset_type(asset_id)
            if asset_type is not None:
                item = {}
                item['asset_id']   = asset_id
                item['asset_type'] = asset_type
                views = self.views.get_views(asset_id)
                if views != 0:
                    item['views']  = views
                for l in lang:
                    item['lang']   = l
                    ret            = self.update_asset(item)
                    if ret['status'] != 201:
                        return ret

                self.views.set_commited(asset_id)
                status = 200
                ret    = {'message': 'Asset updated'}
            else:
                status = 422
                ret    = {'status': 'failure', 'message': 'Invalid Asset Type'}

        except Exception as e:
            status = 500
            ret    = {'status': 'failure', 'message': str(e) }
        
        return {'status': status, 'body': ret}

    def _load_valid_fq_from_args(self, args, qArgs):
        '''
            En base a los argumentos validos arma el Set de query 
            con los argumentos recibidos
            args: Received Arguments
            qArgs: Valid Arguments
        '''
        fset = []
        for q in qArgs:
            if q in args:
                if ',' in args[q] and (not args[q].startswith('[') and not args[q].startswith('{')) and len(args[q].split(',')) > 1:
                    values = args[q].split(',')
                    for v in values:
                        fset.append({q:v})
                else:    
                    fset.append({q:args[q]})
        return fset


    def __add_cdn_images(self, response, imgArgs):
        items = response['items']
        ni = []
        for item in items:
            for k in self.images.keys():
                if k in item:
                    item[k] = self.images[k].getUrl(item[k], self.parse_img_arg(k,imgArgs))
            ni.append(item)
        response['items'] = ni
        return response

    def __modify_ranking(self, response):
        items = response['items']
        ni = []
        for item in items:
            n = int(item['ranking'])
            if n > 0:
                item['ranking'] = str(round(float(n)/25,2))
            ni.append(item)
        response['items'] = ni
        return response

    def __cloudsearch_query(self, lang, fqset, exclude, start, size, sort, img):
        '''
            Hace el query definitivo a Cloud Search cuando se 
            solicita un listado.
            Retorna un diccionatio con los valores para ser mapeados
            en una respuesta http
        '''
        try:
            if lang in self.lang:
                ret    = self.domain[lang].query(fqset,exclude,start,size, sort)
                ret    = self.__modify_ranking(ret)
                ret    = self.__add_cdn_images(ret, img)
                status = 200
            else:
                ret = {'status': 'failure', 'messaage': 'Invalid language %s' % lang}
                status = 422
        except CollectionException as  e:
            ret    = {'status': 'failure', 'message': str(e)}
            status = 422
        except CloudSearchException as e:
            ret    = {'status': 'failure', 'message': str(e)}
            status = 500
        except Exception, e:
            ret    = {'status': 'failure', 'message': str(e)}
            status = 500

        return {'status': status, 'body': ret}


    def __cloudsearch_search(self, lang, q, exclude, start, size, img):
        '''
            Hace el query definitivo a Cloud Search cuando se 
            solicita un listado.
            Retorna un diccionatio con los valores para ser mapeados
            en una respuesta http
        '''
        try:
            if lang in self.lang:
                ret    = self.domain[lang].search(q,exclude,start,size)
                ret    = self.__modify_ranking(ret)
                ret    = self.__add_cdn_images(ret, img)
                status = 200
            else:
                ret = {'status': 'failure', 'messaage': 'Invalid language %s' % lang}
                status = 422
        except CollectionException as  e:
            ret    = {'status': 'failure', 'message': str(e)}
            status = 422
        except CloudSearchException as e:
            ret    = {'status': 'failure', 'message': str(e)}
            status = 500
        except Exception, e:
            ret    = {'status': 'failure', 'message': str(e)}
            status = 500

        return {'status': status, 'body': ret}

    def _cs_search(self, args, exclude):
        if 'lang' not in args:
            ret    = {'status': 'failure', 'message': 'Mandatory parameter not found (lang)'}
            status = 422
            return {'status': status, 'body': ret}    
        
        if 'q' not in args:
            ret    = {'status': 'failure', 'message': 'Mandatory parameter not found (q)'}
            status = 422
            return {'status': status, 'body': ret}

        lang = args['lang']
        q    = args['q']
        if 'start' in args:
            start = args['start']
        else:
            start = 0
        if 'size' in args:
            size  = args['size']
        else:
            size  = 10

        if 'img' in args:
            img = args['img']
        else:
            img = None

        return self.__cloudsearch_search(lang,q,exclude,start,size,img)


    def _cs_query(self, args, qArgs, fq, exclude):
        '''
            args:  Received Arguments
            qArgs: Valid Arguments
            fq:    Default filter query
            exclude: Negative default filter query
        '''
        if 'lang' in args:
            lang  = args['lang']
            
            fqset = self._load_valid_fq_from_args(args,qArgs)
            if fq is not None:
                fqset.append(fq)
            if 'start' in args:
                start = args['start']
            else:
                start = 0
            if 'size' in args:
                size  = args['size']
            else:
                size  = 10
            if 'sort' in args:
                sort  = args['sort']
            else:
                sort  = None

            if 'img' in args:
                img = args['img']
            else:
                img = None

            return self.__cloudsearch_query(lang, fqset, exclude, start, size, sort,img)
        else:
            ret    = {'status': 'failure', 'message': 'Mandatory parameter not found (lang)'}
            status = 422

        return {'status': status, 'body': ret}
 
        
    def add_asset(self, Item={}):
        inmutable_fields = ['views', 'ranking']
        if not 'asset_type' in Item:
            status = 422
            ret    = {'status': 'failure', 'message': 'Mandatory parameter not found in item(lang)'}

        at = {}
        at['asset_id']   = Item['asset_id']
        at['asset_type'] = Item['asset_type']
        try:
            if Item['asset_type'] == 'girl':
                self.asset_type.add(at) # Ojo con las Excepciones
                return self.__add_asset(self.girls,Item, inmutable_fields)
            if Item['asset_type'] == 'show':
                self.asset_type.add(at) # Ojo con las Excepciones
                if Item['show_type'] == 'movie' or Item['show_type'] == 'episode':
                    #
                    # Se agrega subtitluado para los assets que son de tipo Movie o Episode
                    #
                    if self.subtitle.check(Item['asset_id'], Item['lang']):
                        Item['subtitle'] = self.subtitle.get_subtitle_url(Item['asset_id'], Item['lang'])

                return self.__add_asset(self.shows,Item, inmutable_fields)
            else:
                status = 422
                ret    = {'status': 'failure', 'message': 'Invalid show type: %s' % Item['asset_type']}

        except Exception as e:
            status = 500
            ret    = {'status': 'failure', 'message': str(e)}

        return {'status': status, 'body': ret}

    def disable_asset(self, Item={}):
        if not 'asset_type' in Item:
            status = 422
            ret    = {'status': 'failure', 'message': 'Mandatory parameter not found in item(asset_type)'}
        else:
            if Item['asset_type'] == 'girl':
                return self.__disable_asset(self.girls,Item)
            if Item['asset_type'] == 'show':
                return self.__disable_asset(self.shows,Item)
            else:
                status = 422
                ret    = {'status': 'failure', 'message': 'Invalid asset_type: %s' % Item['asset_type']}

        return {'status': status, 'body': ret}

    def update_asset(self, Item={}):
        if not 'asset_type' in Item:
            asset_type = self.__get_asset_type(Item['asset_id'])
            if asset_type is None:
                status = 422
                ret    = {'status': 'failure', 'message': 'Invalid asset_type: %s' % Item['asset_type']}

        else:
            asset_type = Item['asset_type']

        if asset_type == 'girl':
            return self.__update_asset_field(self.girls, Item)
        elif asset_type == 'show':
            return self.__update_asset_field(self.shows, Item)
        else:
            status = 422
            ret    = {'status': 'failure', 'message': 'Invalid asset_type: %s' % Item['asset_type']}

        return {'status': status, 'body': ret}

    def __get_asset_type(self, asset_id):
        # El asset puede ser una "girl" o un "show"
        at = {}
        at['asset_id'] = asset_id
        try:
            ret = self.asset_type.get(at)
            return ret['item']['asset_type']
        except:
            return None

    def __update_asset_field(self,where,item):
        if 'lang' in item and item['lang'] in self.lang:
            lang = item['lang']
            try:
                doc  = where.get(item)
                Item = doc['item']
                if Item != {}:
                    for k in item.keys():
                        if k != 'lang' or k != 'asset_id':
                            Item[k] = item[k]
                    
                    self.domain[lang].add(Item)
                    ret = where.add(Item)
                    status = 201
                else:
                    status = 404
                    ret    = {'status': 'failure', 'message': 'Item not found %s' % str(Item)}
            except CollectionException as e:
                status = 422
                ret    = {'status': 'failure', 'message': str(e)}
            except DynamoException as e:
                ret    = {'status': 'failure', 'message': str(e)}
                status = 500
            except CloudSearchException as e:
                ret    = {'status': 'failure', 'message': str(e)}
                status = 500    
            except Exception as e:
                ret    = {'status': 'failure', 'message': str(e)}
                status = 500
        else:
            status = 422
            ret    = {'status': 'failure', 'message': 'Mandatory parameter not found in item (lang) or is Incorrect'}

        return {'status': status, 'body': ret}

    def __add_asset(self,where,item,inmutable_fields=[]):
        if 'lang' in item and item['lang'] in self.lang:
            lang = item['lang']
            try:
                doc  = where.get(item)
                Item = doc['item']
                if Item == {}:
                    for k in inmutable_fields:
                        if where.schema[k] == 'N':
                            item[k]   = 0
                else:
                    for k in inmutable_fields:
                        item[k]   = Item[k]

                item['enabled'] = 1

                self.domain[lang].add(item)
                ret = where.add(item)
                status = 201

            except CollectionException as e:
                status = 422
                ret    = {'status': 'failure', 'message': str(e)}
            except DynamoException as e:
                ret    = {'status': 'failure', 'message': str(e)}
                status = 500
            except CloudSearchException as e:
                ret    = {'status': 'failure', 'message': str(e)}
                status = 500    
            except Exception as e:
                ret    = {'status': 'failure', 'message': str(e)}
                status = 500
        else:
            status = 422
            ret    = {'status': 'failure', 'message': 'Mandatory parameter not found in item (lang) or is Incorrect'}

        return {'status': status, 'body': ret}

    def __disable_asset(self,where,item):
        if 'lang' in item and item['lang'] in self.lang:
            lang = item['lang']
            try:
                doc  = where.get(item)
                Item = doc['item']
                if Item == {}:
                    status = 422
                    ret = {'status': 'failure', 'message': 'Unable to find item to delete'}
                else:
                    Item['enabled'] = 0
                    self.domain[lang].delete(item)
                    ret    = where.add(Item)
                    status = 204
            except CollectionException as e:
                status = 422
                ret    = {'status': 'failure', 'message': str(e)}
            except DynamoException as e:
                ret    = {'status': 'failure', 'message': str(e)}
                status = 500
            except Exception as e:
                status = 500
                ret    = {'status': 'failure', 'message': str(e)}
        else:
            status = 422
            ret    = {'status': 'failure', 'message': 'Mandatory parameter not found in item (lang) or is Incorrect'}

        return {'status': status, 'body': ret}


    def __commit_suggest(self,qReply):
        ret = {}
        ret['count'] = 0
        ret['items'] = []
        ret['total'] = 0

        Items = qReply['body']
        if 'count' in Items and Items['count'] > 4:
            rnd =  randrange(0, Items['count'] -4 )
            i = 4
            while i > 0:
                ret['items'].append(Items['items'][rnd+i])
                ret['count'] = ret['count'] + 1
                ret['total'] = ret['total'] + 1
                i = i - 1
        return ret

    def suggest(self, args):
        if 'lang' in args and args['lang'] in self.lang:
            if 'asset_id' in args:
                lang     = args['lang']
                asset_id = args['asset_id']
                asset_type = self.__get_asset_type(asset_id)
                if asset_type is not None:
                    item = {}
                    item['lang']     = lang
                    item['asset_id'] = asset_id
                    if asset_type   == 'girl':
                        ret = self.girls.get(item)
                        if ret['item'] != {}:
                            girl = ret['item']
                            if 'img' in args:
                                qret  = self.query_girl({'lang':lang,'class': girl['class'], 'img': args['img'], 'size': 1000})
                            else:
                                qret  = self.query_girl({'lang':lang,'class': girl['class'], 'size':1000})
                    elif asset_type == 'show':
                        ret = self.shows.get(item)
                        if ret['item'] != {}:
                            show = ret['item']
                            if 'img' in args:
                                qret  = self.query_show({'lang':lang,'channel': show['channel'], 'img': args['img'], 'size':1000})
                            else:
                                qret  = self.query_show({'lang':lang,'channel': show['channel'], 'size': 1000})
                    
                    status = 200
                    ret = self.__commit_suggest(qret)
                else:
                    status = 500
                    ret    = {'status': 'failure', 'message': 'Asset type not found'}
            else:
                status = 422
                ret    = {'status': 'failure', 'message': 'Mandatory parameter not found (asset_id)'}
        else:
            status = 422
            ret    = {'status': 'failure', 'message': 'Mandatory parameter not found in item (lang)'}


        return {'status': status, 'body': ret}


    def query_show(self, args):
        exclude = {'show_type' :'episode'}
        fq      = {'asset_type':'show'}
        qArgs   = ['ranking', 'views', 'show_type', 'channel', 'girls_id', 'year', 'categories']

        return self._cs_query(args,qArgs,fq,exclude)


    def query_girl(self, args):
        fq      = {'asset_type':'girl'}
        qArgs   = ['class', 'ranking', 'views']
        exclude = None

        return self._cs_query(args,qArgs,fq,exclude)

    def query_episode(self, args):
        fq      = {'show_type': 'episode'}
        qArgs   = ['serie_id', 'season']

        if 'serie_id' not in args:
            status = 404
            ret    = {'count': 0, 'items': [], 'total': 0}
            return {'status': status, 'body': ret}

        return self._cs_query(args,qArgs,fq,None)

    def query_block(self, args):
        exclude = {'show_type': 'episode'}
        qArgs   = ['blocks']

        if 'blocks' not in args:
            status = 404
            ret    = {'count': 0, 'items': [], 'total': 0}
            return {'status': status, 'body': ret}

        return self._cs_query(args,qArgs,None,exclude)

    def search(self, args):
        exclude = {'show_type':'episode'}

        return self._cs_search(args,exclude)
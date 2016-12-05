from Collection import dynamodbCollection
from Collection import cloudsearchCollection
from Collection import CollectionException
from Collection import DynamoException
from Collection import CloudSearchException

class Backend(object):
    def __init__(self, config):
        print "Que pasa aca"

        if 'blocks' in config:
            self.blocks     = dynamodbCollection(config['blocks'])

        if 'sliders' in config:
            self.sliders    = dynamodbCollection(config['sliders']) 
    
        if 'girls' in config:
            self.girls      = dynamodbCollection(config['girls'])

        if 'categories' in config:
            self.categories = dynamodbCollection(config['categories'])


        if 'search_domain' in config:
            self.domain = cloudsearchCollection(config['search_domain'])

        self.channels   = None
#        if 'channels' in config:
#            self.channels = dynamodbCollection(config['channels'])


#        self.girls
#        self.shows


    def __cloudsearch_query(self, lang, fqset, exclude, start, size):
        try:
            ret    = self.domain.query(fqset,exclude,start,size)
            status = 200
        except CollectionException as  e:
            ret    = {'status': 'failure', 'message': str(e)}
            status = 422
        except CloudSearchException as e:
            ret    = {'status': 'failure', 'message': str(e)}
            status = 500
        except Exception, e:
            ret    = {'status': 'failure', 'message ---': str(e)}
            status = 500

        return {'status': status, 'body': ret}


    def __query(self, where, q):
        try:
            ret    = where.query(q)
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
            print ret
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

    '''
        Add Methods for Slider, Block and Category
    '''
    def add_slider(self, Item={}):
        return self.__add(self.sliders, Item)

    def add_block(self, Item={}):
        return self.__add(self.blocks, Item)

    def add_category(self, Item={}):
        return self.__add(self.categories, Item)

    '''
        Del Methods for Slider, Block and Category
    '''
    def del_block(self, Item={}):
        return self.__del(self.blocks, Item)

    def del_category(self, Item={}):
        return self.__del(self.categories, Item)

    def del_slider(self, Item={}):
        return self.__del(self.sliders, Item)

    '''
        Query Methods for Slider, Block and Category
    '''
    def query_block(self, arg):
        return self.__query(self.blocks,arg)

    def query_slider(self, arg):
        return self.__query(self.sliders,arg)

    def query_category(self, arg):
        return self.__query(self.categories,arg)


    def _load_valid_fq_from_args(self, args, qArgs):
        '''
            args: Received Arguments
            qArgs: Valid Arguments
        '''
        fset = []
        for q in qArgs:
            if q in args:
                print args[q]
                if ',' in args[q] and (not args[q].startswith('[') and not args[q].startswith('{')) and len(args[q].split(',')) > 1:
                    values = args[q].split(',')
                    for v in values:
                        fset.append({q:v})
                else:    
                    fset.append({q:args[q]})
        return fset
    
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

            return self.__cloudsearch_query(lang, fqset, exclude, start, size)
        else:
            ret    = {'status': 'failure', 'message': 'Mandatory parameter not found (lang)'}
            status = 422

        return {'status': status, 'body': ret}
 
    def query_girl(self, args):
        fq      = {'asset_type':'girl'}
        qArgs   = ['class', 'ranking', 'views']
        exclude = None

        return self._cs_query(args,qArgs,fq,exclude)
    
    def query_show(self, args):
        print args
        exclude = {'show_type' :'episode'}
        fq      = {'asset_type':'show'}
        qArgs   = ['ranking', 'views', 'show_type', 'channel', 'girl', 'year', 'categories', 'category']

        return self._cs_query(args,qArgs,None,None) #fq,exclude)

    def query_asset(self, args):
        exclude = {'show_type':'episode'}
        pass


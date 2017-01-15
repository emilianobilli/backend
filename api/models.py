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

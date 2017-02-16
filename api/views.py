import boto3

class Views(object):
    def __init__(self, table_name, cindex):
        self.client         = boto3.client('dynamodb')
        self.table_name     = table_name
        self.commited_index = cindex

    def _check_ret(self, ret): 
        if 'ResponseMetadata' in ret:
            if 'HTTPStatusCode' in ret['ResponseMetadata']:
                if ret['ResponseMetadata']['HTTPStatusCode'] == 200:
                    return True
        return False

    def add_view(self, asset_id):
        try:
            ret = self.client.update_item(TableName=self.table_name,
                                          Key={'asset_id': {'S': asset_id}},
                                          UpdateExpression="SET asset_views = asset_views + :r, commited = :c",
                                          ExpressionAttributeValues={
                                                    ':r': {'N':'1'},
                                                    ':c': {'S':'0'}
                                          })
            return self._check_ret(ret)
        except Exception as e:
            # Esta exception se puede dar porque el item no existe
            # Voy a ignorar cualquier otro tipo de exception
            item = {'asset_id': {'S': asset_id},
                    'asset_views': {'N': '1'},
                    'commited': {'S': '0'}}
            ret = self.client.put_item(TableName=self.table_name, Item=item)
            return self._check_ret(ret)

    def set_commited(self, asset_id):
        ret = self.client.update_item(TableName=self.table_name,
                                          Key={'asset_id': {'S': asset_id}},
                                          UpdateExpression="SET commited = :c",
                                          ExpressionAttributeValues={
                                                ':c': {'S':'1'}
                                          })
        return self._check_ret(ret)

    def get_views(self, asset_id):
        ret = self.client.get_item(TableName=self.table_name,
                                   Key={'asset_id': {'S': asset_id}})
        if self._check_ret(ret):
            if 'Item' in ret:
                return ret['Item']['asset_views']['N']
        return 0

    def query_uncommited(self):
        assets = []
        ret = self.client.query(TableName=self.table_name,
                                IndexName=self.commited_index,
                                KeyConditionExpression='commited = :val',
                                ExpressionAttributeValues={':val': { 'S':'0'}})
        if self._check_ret(ret):
            if ret['Count'] != 0:
                for item in ret['Items']:
                    assets.append({'asset_id':item['asset_id']['S'], 'asset_views': item['asset_views']['N']})
        return assets


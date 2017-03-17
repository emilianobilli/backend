import boto3

class Ranking(object):
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


    def add_vote(self, asset_id, voted):
        v = voted * 25
        try:
            ret = self.client.update_item(TableName=self.table_name,
                                          Key={'asset_id':{'S': asset_id}},
                                          UpdateExpression="SET ranking = ranking + :r, users = users + :u, commited = :c",
                                          ExpressionAttributeValues={
                                                    ':r': {'N': str(v)},
                                                    ':u': {'N': '1'},
                                                    ':c': {'S': '0'}
                                          })
            return self._check_ret(ret)

        except Exception as e:
            item = {'asset_id': {'S': asset_id},
                    'ranking':  {'N': str(v)},
                    'users':    {'N': '1'},
                    'commited': {'S': '0'}}
            ret  = self.client.put_item(TableName=self.table_name, Item=item)
            return self._check_ret(ret)

    def update_vote(self, asset_id, difference):
        try:
            ret = self.client.update_item(TableName=self.table_name,
                                          Key={'asset_id':{'S':asset_id}},
                                          UpdateExpression="SET ranking = ranking + :d, commited = :c",
                                          ExpressionAttributeValues={
                                                ':d': {'N':str(difference)},
                                                ':c': {'S':'0'}
                                          })
            return self._check_et(ret)
        except Exception as e:
            # Una Flensoneada
            return False 

    def set_commited(self, asset_id):
        ret = self.client.update_item(TableName=self.table_name,
                                          Key={'asset_id': {'S': asset_id}},
                                          UpdateExpression="SET commited = :c",
                                          ExpressionAttributeValues={
                                                ':c': {'S':'1'}
                                          })
        return self._check_ret(ret)

    def get_ranking(self, asset_id):
        ret = self.client.get_item(TableName=self.table_name,
                                   Key={'asset_id': {'S': asset_id}})
        if self._check_ret(ret):
            if 'Item' in ret:
                total = int(ret['Item']['ranking']['N'])
                users = int(ret['Item']['users']['N'])
                return int(total/users)
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
                    assets.append({'asset_id':item['asset_id']['S']})
        return assets


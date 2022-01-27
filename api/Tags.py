# -*- coding: utf-8 -*-
from Collection import cloudsearchCollection
from Collection import CloudSearchException
from time import time

esconfig = {"domain": {
     "id_field": "id",
     "filter_query" : '',
     "schema": ["asset_id","tag", "tag_id", "tc_in","tc_out"],
     "return_fields": ["asset_id","tag", "tag_id", "tc_in","tc_out"],
     "name" : "estags",
     }
}

brconfig = {"domain": {
     "id_field": "id",
     "filter_query" : '',
     "schema": ["asset_id","tag", "tag_id", "tc_in","tc_out"],
     "return_fields": ["asset_id","tag", "tag_id", "tc_in","tc_out"],
     "name" : "brtags",
     }
}

ptconfig = {"domain": {
     "id_field": "id",
     "filter_query" : '',
     "schema": ["asset_id","tag", "tag_id", "tc_in","tc_out"],
     "return_fields": ["asset_id","tag", "tag_id", "tc_in","tc_out"],
     "name" : "pttags",
     }
}

class Tags(object):
    def __init__(self, config):
	self.lang = {}
	for key in config.keys():
	    try:
	    	self.lang[key] = cloudsearchCollection(config[key])
	    except:
		return None

    def parseTagReturn(self, values):
        ret = {}
	if 'items' in values:
	    for item in values['items']:
		if 'tag' in item:
		    if item['tag'] in ret:
			ret[item['tag']].append({'out': item['tc_out'] ,'in': item['tc_in']})
		    else:
                        ret[item['tag']] = [{'out': item['tc_out'] ,'in': item['tc_in']}] 	
	return ret

    def getTags(self, lang, asset):
	if lang in self.lang:
	    ret = self.lang[lang].query([{'asset_id': asset}], None, 0, 100)
	    return self.parseTagReturn(ret)
	return {}


    def addTag(self, lang, asset):
        ret = {}
	if lang in self.lang:
            asset['id'] = str(time())   
            ret = self.lang[lang].add(asset)
	return ret

export_tags = Tags({'es': esconfig, 'br': brconfig, 'pt': ptconfig})
#ret = export_tags.getTags('es', '025012')
#ret = export_tags.addTag('es', {"tag_id":"T00004","tc_in":"2","tc_out":"14","asset_id":"025012"})
#print(ret)
#cs = cloudsearchCollection(config)
#re = cs.query([{'asset_id':'011712'}],None, 0, 100)
#print(re)

#print tags.getTags('es', '011712')

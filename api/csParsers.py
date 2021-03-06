import re


class Structured(object):
    def __init__(self):
        self.q             = None
        self.fq            = []
        self.exclude       = None
        self.size          = None
        self.start         = None
        self.sort          = None
        self.return_fields = []
        
    def fq_add (self, kv={}):
        if len(kv.keys()) > 0:
            self.fq.append(kv)

    def _exclude(self):
	if self.exclude is not None:
	    if type(self.exclude).__name__ == 'dict':
		exclude = self.exclude
                ek = (exclude.keys())[0]     
                ev = self._check_range(exclude[ek])
                if ev is not None:
                    return "(not %s:%s)" % (ek,ev)
                return ''
	    elif type(self.exclude).__name__ == 'list':
		exclude = self.exclude
		ret = []
		for edict in exclude:
		    ek = (edict.keys())[0]
		    ev = self._check_range(edict[ek])
		    if ev is not None:
			ret.append('%s:%s' % (ek,ev))
		if ret is not []:
		    return '(not (or ' + ' '.join(ret) + '))'
	    else:
		return ''
	else:
	    return ''

    def _check_range(self, v=None):
        if (v.startswith('[') or v.startswith('{')) and (v.endswith(']') or v.endswith('}')):
            close  = '\[\d+,\d+\]'
            open_r = '\[\d+,\]'
            open_l = '\[,\d+\]'
            if re.match(close,v):
                return v
            elif re.match(open_r,v):
                return v.replace(']','}')
            elif re.match(open_l,v):
                return v.replace('[','{')
            else:
                return None
        return '\'%s\'' % v

    def _make_q(self, q=[]):
        ret = ''
        if len(q) == 0:
            return self._exclude()
        
        if len(q) > 1:
            ret = ret + '(and '
            for kv in q:
                k = kv.keys()[0]
                v = self._check_range(kv[k])
                if v is not None:    
                    ret = ret + "%s:%s " % (k,v)
            ret = ret[0:len(ret)-1] + '%s)' % (self._exclude())
        else:
            k = (q[0].keys())[0]
            v = self._check_range((q[0])[k])
            if v is not None:
                if self.exclude is not None:
                    ret = "(and %s:%s %s)" % (k,v, self._exclude())
                else:
                    ret = "%s:%s" % (k,v)
            else:
                ret = ''
        return ret

    def _make_union(self, q=[]):
        ret = ''

        if len(q) > 1:
            ret = ret + '(or '
            for kv in q:
                k = kv.keys()[0]
                v = self._check_range(kv[k])
                if v is not None:    
                    ret = ret + "%s:%s " % (k,v)
            ret = ret[0:len(ret)-1] + ')'
        else:
            k = (q[0].keys())[0]
            v = self._check_range((q[0])[k])
            if v is not None:
                    ret = "%s:%s" % (k,v)
            else:
                ret = ''
        return ret
        
    def _make_sort(self):
        if self.sort is not None:
            return '&sort=%s %s' % ((self.sort[1:], 'desc') if self.sort.startswith('-') else (self.sort,'asc'))
        return ''

    def _make_size(self):
        if self.size is not None:
            return '&size=%s' % (int(self.size) if type(self.size).__name__ == 'int' else self.size)
        return ''
    def _make_start(self):
        if self.start is not None:
            return '&start=%s' % (int(self.start) if type(self.start).__name__ == 'int' else self.start)
        return ''
        
    def _make_filter_query(self):
        ret = self._make_q(self.fq)
        return ('&fq=%s' % ret) if ret != '' else ''

    def _make_filter_query_union(self):
	ret = self._make_union(self.fq)
        return ('&fq=%s' % ret) if ret != '' else ''

    def _make_return(self):
        if self.return_fields != []:    
            return '&return=%s' % ','.join(self.return_fields)
        return ''

    def _make_search(self):
        if self.q is not None:
            return "\'" + self.q + "\'"
        else:
            return ''

    def _make_query(self):
        ret = self._make_search()
        return ('q=%s' % ret) if ret != '' else 'q=matchall'
        
    def make(self, union=False):
        return '%s%s%s%s%s%s%s' % (self._make_query(),
                                   self._make_filter_query() if union == False else self._make_filter_query_union(),
                                   self._make_size(),
                                   self._make_start(),
                                   self._make_sort(),
                                   self._make_return(),
                                   '&q.parser=structured')




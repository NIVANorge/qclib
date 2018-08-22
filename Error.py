
import logging


class Error(Exception):
    
    def __init__(self, *args, **kw):
        types = { 'errs': (Exception,), 'logs': (logging.Logger,) }
        sargs = {}
        largs = []
        args  = list(args)
        for k,v in types.items():
            sargs[k] = filter(lambda x: isinstance(x, v), args)
            largs += sargs[k]
        args = filter(lambda x: x not in largs, args)
        
        if not len(args):
            args = [ 'undocumented error' ]
        if (len(args) == 1) and isinstance(args[0], basestring):
            args[0] = args[0].replace('%', '%%')
        args.insert(1, self.__class__.__name__)
        fmt = '%s: ' + args[0]
        msg = fmt % tuple(args[1:])
        msg = self.toPrintable(msg)
        #
        #
        for k,v in kw.items():
            s = v
            if not isinstance(v, str):
                s = str(v)
            s = self.toPrintable(s)
            msg = '[%s=%s] %s' % (k,s,msg)
        
        self.value = "\n".join([ msg ] + map(str, sargs['errs'])) 
        
        for l in sargs['logs']:
            l.error(self.value)
        return
    
    def __str__(self):
        return(self.value)

    def toPrintable(self, s):
        ii  = range(len(s))
        nn  = map(lambda x: ord(s[x]), ii)
        jj  = filter(lambda x: nn[x] not in [9] + range(32,127), ii)
        dd  = dict(map(lambda x: (s[x], '0x%02X' % (nn[x])), jj))
        for k in dd.keys():
            s = s.replace(k, dd[k])
        return(s)

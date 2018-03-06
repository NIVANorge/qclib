"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.Parser
===========================



(C) 23. jun. 2016 Pierre Jaccard
"""

import re
import math
import hashlib

# These are imported for evaluating functions in import conf
import datetime
import numpy as np

from pyTools.Error import Error
from pyTools.Import import str2fun
from pyTools.Conversions import DAY1950

from .netCDF import Generic

class ParserError(Error): pass

class AsciiParser(object):
    
    def __init__(self, fasc, conf, check_file=False):
        self.file  = fasc
        self.conf  = conf
        self.fp    = None
        self.lnum  = 0
        self.line  = None
        self.batch = 0
        self.check = check_file
        self.last_step = None
        #
        # Prepare CONF for faster parsing
        #
        if 'comment' not in self.conf:
            self.conf['comment'] = None
        if ('delimiter' not in self.conf) or (not self.conf['delimiter']):
            self.conf['delimiter'] = None
        if ('decimal' not in self.conf) or (not self.conf['decimal']):
            self.conf['decimal'] = False
        if ('data_expr' not in self.conf) or (not self.conf['data_expr']):
            self.conf['data_expr'] = '^.*$'
        if isinstance(self.conf['data_expr'], basestring):
            self.conf['data_expr'] = re.compile(self.conf['data_expr'])
        if not isinstance(self.conf['columns'], list):
            cols = map(lambda x: x.strip(), self.conf['columns'].split())
            self.conf['columns'] = cols
        if 'ncols' not in self.conf:
            self.conf['ncols'] = len(self.conf['columns'])
        if 'time_expr' not in self.conf:
            self.conf['time_expr'] = ''
        if ('time_step' not in self.conf) or (not self.conf['time_step']):
            self.conf['time_step'] = None   
        else: 
            # change time to seconds    
            self.conf['time_step'] = self.conf.as_float('time_step')   
        for i in range(self.conf['ncols']):
            v = self.conf['columns'][i]
            if ('type' not in self.conf[v]) or (not self.conf[v]['type']):
                self.conf[v]['type'] = lambda x: x 
            elif isinstance(self.conf[v]['type'], basestring):
                self.conf[v]['type'] = str2fun(self.conf[v]['type'], globals())
            if ('test' not in self.conf[v]) or (not self.conf[v]['test']):
                self.conf[v]['test'] = lambda x: True
            elif isinstance(self.conf[v]['test'], basestring):
                self.conf[v]['test'] = str2fun(self.conf[v]['test'], globals())
            if ('ignore' not in self.conf[v]) or (not self.conf[v]['ignore']):
                self.conf[v]['ignore'] = False 
        self.conf['types']  = map(lambda x: self.conf[x]['type'], self.conf['columns'])
        self.conf['tests']  = map(lambda x: self.conf[x]['test'], self.conf['columns'])
        self.conf['ignore'] = map(lambda x: self.conf[x]['ignore'], self.conf['columns'])
        self.conf['t_args'] = filter(lambda x: re.search(r'\b'+x+r'\b', self.conf['time_expr']), self.conf['columns'])
        self.conf['t_func'] = 'lambda ' + ','.join(self.conf['t_args']) + ': ' + self.conf['time_expr']
        self.conf['t_func'] = str2fun(self.conf['t_func'], globals())
        return
    
    def __del__(self):
        self._delete_(self)
        return
       
    @classmethod 
    def _delete_(cls, self):
        if self.fp is not None:
            self.fp.close()
            self.fp = None
        return
    
    def close(self):
        self._delete_(self)
        return
    
    #initialize the loop 
    def __iter__(self):
        self.fp = open(self.file, 'rb')
        self.line  = ''
        self.lnum  = 0
        self.batch = np.uint32((datetime.datetime.now() - DAY1950).total_seconds())
        self.last_step = None #time of the last step 
        return(self)
    
    def next(self):
        data = None
        done = False
        while not done:
            try:
                self.line = self.fp.next()
                self.lnum += 1
                self.line = self.line.strip()
                if not self.line:
                    continue
                if self.conf['comment'] and self.line.startswith(self.conf['comment']):
                    continue
                if not self.conf['data_expr'].search(self.line):
                    continue
                if self.conf['decimal']:
                    self.line = self.line.replace(',', '.')
                words = self.line.split(self.conf['delimiter'])
                if len(words) != self.conf['ncols']:
                    raise ParserError('mismatch number of columns: %-d', len(words))
                data = map(lambda x: self.conf['types'][x](words[x]), range(self.conf['ncols']))
                test = map(lambda x: self.conf['tests'][x](data[x]) , range(self.conf['ncols']))
                flst = filter(lambda x: not x, test)
                if flst:
                    flst = map(lambda x: '%-d' % (x), flst)
                    raise ParserError('failed test of columns %s', ','.join(flst))
                data = dict(map(lambda x: (self.conf['columns'][x], data[x]), range(self.conf['ncols'])))
                args = map(lambda x: data[x], self.conf['t_args'])
                data['time']     = self.conf['t_func'](*args)
                data['time_id']  = data['time'].hour*3600 + data['time'].minute*60 + data['time'].second
                data['batch_id'] = self.batch
                if self.conf['time_step'] is not None: 
                    if self.last_step is None: 
                        self.last_step = data['time']
                    else :
                        if (data['time'] - self.last_step).total_seconds() < self.conf['time_step']: 
                            continue
                        else: 
                            self.last_step = data['time']
                done = True
            except StopIteration:
                self.close()
                raise StopIteration
            except Exception as err:
                raise ParserError(str(err), file=self.file, lnum=self.lnum, line=self.line)
        return(data)
                    
class AveragingWindParser(AsciiParser):

        def __init__(self, *args, **kw):
            super(AveragingWindParser, self).__init__(*args, **kw)
            self.tavg = kw['tavg']
            self.nmin = kw['nmin']
            (wcol, ocol) = self.SensorSplitter()
            self.wind_cols   = wcol
            self.other_cols  = ocol
            self.buffer = []
            self.stack  = []
            return

        def SensorSplitter(self):
            wmap = {}
            iall = range(len(self.conf['columns']))
            olst = iall
            ilst = filter(lambda x: self.conf['columns'][x].startswith('WIND_ID_'), iall)
            if not len(ilst):
                raise ParserError('no WIND_ID columns', conf=self.conf.file)
            for i in ilst:
                wid = self.conf['columns'][i][9:]
                ii  = filter(lambda x: self.conf['columns'].endswith('_' + wid))
                wmap[wid] = ii
                olst = filter(lambda x: x not in ii, olst)
            return(wmap, olst)
            
        def next(self):
            if len(self.stack):
                return(self.stack.pop()) 
            done = False
            while not done:
                r = super(AveragingWindParser, self).next()
                if len(self.buffer) > 0:
                    dt = (r['time'] - self.buffer[0]['time']).total_seconds()
                    if dt > self.tavg:
                        if len(self.buffer) > self.nmin:
                            
                            pass
                        else:
                            self.buffer = self.buffer[1:]
                self.buffer.append(r)
                
                    
        def ship_speed(self):
            if 'GPS_SPEED' in self.conf['columns']:
                pass
            return

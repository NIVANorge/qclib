"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.Operations.Import
===========================



(C) 6. jun. 2016 Pierre Jaccard
"""

import os

from pyTools.Config import ExtendedConfigObj
from pyTools.Error import Error

from ..FolderManagers import PendingFolder
from ..FolderManagers import importRoot
from ..FolderManagers import ImportConfigs
from ..FolderManagers import PoolRoot

from .. import Loggers
from .. import Parser
from ..netCDF import Generic
from .. import Globals
from ..Database import PoolDB
from ..Database import ImportDB

log = Loggers.getLogger(__name__)

class ImportError(Error): pass

class Config(object):
    
    _features_ = ExtendedConfigObj.Features.ALL
    
    def __init__(self, fcfg):
        self.file = fcfg
        self.conf = ExtendedConfigObj.Config(fcfg, features=self._features_)
        return

    def logical(self, *path):
        c = self.conf
        for i in range(len(path)-1):
            k = path[i]
            c = c[k]
        k = path[-1]
        ExtendedConfigObj.WalkProcessors.logical(c, k, self.conf)
        return(c[k])
    
    def evaluate(self, *path):
        c = self.conf
        for i in range(len(path)-1):
            k = path[i]
            c = c[k]
        k0 = path[-1]
        k1 = '@' + k0
        c[k1] = 'lambda x: ' + c[k0] 
        ExtendedConfigObj.WalkProcessors.logical(c, k1, self.conf)
        return(c[k0])
        

class Configs(ImportConfigs):
    
    def __init__(self, provider, ship):
        super(Configs, self).__init__(provider, ship)
        self.configs = []
        return
    
    def load(self, *args):
        try:
            for f in args:
                cfg = Config(f)
                self.configs.append(cfg)
        except Exception as err:
            log.failed(err, config=f)
        return

class LogImporter(object):
    
    def __init__(self, flog, conf, **kw):
        self.file = flog
        self.conf = conf
        self.meta = kw
        return
    
    def checkFile(self):
        error  = None
        count= 0
        if 'parser' in self.conf:
            pname = self.conf['parser']
        else:
            pname = 'AsciiParser'
        cls = getattr(Parser, pname)
        parser = cls(self.file, self.conf)
        try:
            for d in parser:
                count += 1
            if not count:
                raise(Parser.ParserError('found no data in file'))
        except Exception as err:
            error = err
        return(error)

    def importFile(self):
        if 'parser' in self.conf:
            pname = self.conf['parser']
        else:
            pname = 'AsciiParser'
        pool   = PoolRoot()
        cls    = getattr(Parser, pname)
        parser = cls(self.file, self.conf)
        dsrc   = os.path.dirname(self.file)
        meta   = dict(map(lambda x: (x, self.meta[x]), ('provider', 'platform')))
        log.enter('importing data', file=self.file, conf=self.conf.filename)
        try:
            flst = []
            nrec = 0
            for r in parser:
                day = r['time'].strftime(Globals.D_FORMAT_USR)
                meta['day'] = day
                ncb = Generic.netCDF.ncFile(self.meta['provider'], self.meta['platform'], day)
                ncf = os.path.join(dsrc, ncb)
                if ncb not in flst:
                    log.info('new NC file', file=ncf)
                    flst.append(ncb)
                nco = Generic.LogData(ncf, self.conf, **meta)
                nco.addRecord(r)
                nco.close()
                nrec += 1
            log.success(records=nrec)
        except Exception as err:
            log.failed(err, records=nrec)
            raise ImportError(str(err))
        return(flst)

class Importer(object):
    
    def __init__(self, drep):
        self.fm   = drep
        self.flog = os.path.join(drep.path, drep.meta['source_log']) 
        return
    
    @classmethod
    def nextPending(cls):
        log.enter('looking for pending imports')
        try:
            root = importRoot()
            n    = root.nextFolder()
            if n:
                log.success('found pending import folder', path=n.path)
                return(n)
            p = PendingFolder()
            z = p.nextPending('repackaging')
            if not z:
                log.success('no pending imports')
                return
            log.success('found new import', package=z)
        except Exception as err:
            log.failed(err)
            raise(err)
        log.enter('installing new import', package=z)
        try:
            z = os.path.join(p.path, z)
            drep = root.processor(root.name, z, extract_zip_package=True)
            os.unlink(z)
            log.success(path=drep.path)
        except Exception as err:
            log.failed(err)
            raise(err)            
        return(drep)
    
    def selectConf(self):
        info = { 'platform': self.fm.meta['platform'], 'provider': self.fm.meta['provider'], 'log': self.flog }
        log.enter('looking for import configuration', **info)
        try:
            self.configs = Configs(self.fm.meta['provider'], self.fm.meta['platform'])
            flst = self.configs.configFiles()
            self.configs.load(*flst)
            errs = {}
            conf = None
            for cfg in self.configs.configs:
                obj = LogImporter(self.flog, cfg.conf)
                errs[cfg.file] = obj.checkFile()
                if not errs[cfg.file]:
                    conf = cfg.conf
            klst = filter(lambda x: errs[x] is None, errs.keys())
            if len(klst) > 1:
                s = ','.join(klst)
                log.failed('too many configs', log=self.flog, conf=s)
                raise ImportError('too many configs', log=self.flog, conf=s)
            elif (not len(klst)) or (not conf):
                log.failed('no config file', log=self.flog) 
                for k in errs.keys():
                    log.error('Config %s: %s', k, str(errs[k]))
                raise ImportError('no config file', log=self.flog) 
            log.success(config=klst[0])
        except Exception as err:
            log.failed(err, **info)
            raise(err)            
        return(conf)
    
    
    @classmethod
    def execute(cls):
        done  = False
        count = 0
        while not done:
            fm = cls.nextPending()
            if not fm:
                done = True
                continue                
            log.enter('importing data', path=fm.path)
            try:
                obj  = cls(fm)
                db   = ImportDB.ImportDB()
                test = db.is_imported(obj.fm.meta['provider'], obj.fm.meta['platform'], obj.flog)
                db.close()
                if not test:
                    cfg  = obj.selectConf()
                    meta = { 'provider': obj.fm.meta['provider'], 'platform': obj.fm.meta['platform'] }
                    ncg  = '/'.join([''] + cfg['ncgroup'].split('/'))
                    dlog = LogImporter(obj.flog, cfg, **meta)                   
                    flst = dlog.importFile()
                    obj.fm.meta['import']['files'] = flst
                    #
                    atmp = fm.tmpArchive(fm.files())
                    adst = fm.archiveFile(atmp)
                    log.info('working files archived', archive=adst, source=fm.path)
                    #
                    pool = PoolRoot()
                    for f in flst:
                        fnc  = os.path.join(fm.path, f)
                        clst = pool.ncCategories(fnc)
                        if pool.inPool(fnc, *clst):
                            dst = pool.mergeFile(fnc, ncg + '/time')
                        else:
                            dst = pool.addFile(fnc)
                        dst = pool.sortFile(dst, 'time', ncg)
                        grp = ncg.split('/')[-1]
                        stid = getattr(Globals.FileStatus, Globals.FileStatus.NEW_RAW_DATA_   + grp.upper())
                        opid = getattr(Globals.Operations, Globals.Operations.ADD_RAW_DATA_ + grp.upper())
                        db  = PoolDB.PoolDB()
                        db.register_raw_file(dst, stid)
                        db.update_operation(opid)
                        db.close()
                    #
                    db   = ImportDB.ImportDB()
                    db.register_import(obj.fm.meta['provider'], obj.fm.meta['platform'], obj.flog)
                    db.close()
                    count += 1
                else:
                    log.info('file already imported', file=obj.flog)
                #
                fm.rmtree()
                log.success()
            except Exception as err:
                log.failed(err)
                fm.failed()
        return
            

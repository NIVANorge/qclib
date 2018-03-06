"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry.Operations.BaseOperations
===========================



(C) 2. jun. 2016 Pierre Jaccard
"""

import os

from pyTools.Main import LockTimeout

from pyFerry.Database import PoolDB

from ..netCDF import Generic
from ..FolderManagers import processorRoot
from ..FolderManagers import PoolRoot

from .. import Loggers

log = Loggers.getLogger(__name__)

class BaseOperation(object):

    @classmethod
    def execute(cls, name, meth, *args, **kw):
        log.enter('executing operations', operation=name)
        try:
            done = False
            while not done:
                done = meth(*args, **kw)
            log.success('no more pending items')
        except Exception as err:
            log.failed(err)
            raise(err)
        return

class PoolOperation(object):
    
    OPERATION_NAME = None
    TRIGGER_STATUS = None
    RESULT_STATUS  = None
    
    def __init__(self, ncf, workfm):
        self.file  = ncf
        self.ncobj = Generic.netCDF(ncf)
        self.work  = workfm
        self.opid  = workfm['operation']
        return
    
    @classmethod
    def defaults(cls, **kw):
        if 'operation' not in kw:
            kw['operation'] = cls.OPERATION_NAME
        if 'status' not in kw:
            kw['status'] = cls.TRIGGER_STATUS
        if 'next' not in kw:
            kw['next'] = cls.RESULT_STATUS
        return(kw)
    
    @classmethod
    def nextPending(cls, **kw):
        log.enter('looking for pending %s', kw['operation'])
        try:
            root = processorRoot(kw['operation'])
            work = root.nextFolder()
            meta = { 'operation': kw['operation'] }
            if work:
                msg = 'found pending folder'
                meta['path'] = work.path
            else:
                msg = 'no pending folder found'
            log.success(msg, **meta)
        except Exception as err:
            log.failed(err)
            raise(err)
        return(work)
    
    @classmethod
    def todoList(cls, **kw):
#        opname = kw['operation']
#        status = kw['status']
        db     = PoolDB.PoolDB()
#        rlst   = db.todoList(opname, status, **kw)
        rlst   = db.todoList(kw['status'], kw['next'])
        db.close()
        return(rlst)
    
    @classmethod
    def process(cls, ncf, fm, *args):
        assert False, 'this method has to be subclassed'
        return

    @classmethod
    def newPending(cls, **kw):
        if 'skip' not in kw:
            kw['skip'] = []
        log.enter('looking for new candidates', operation=kw['operation'], status=kw['status'])
        try:
            rlst = cls.todoList(**kw)
            log.success('found %-d files', len(rlst), operation=kw['operation'], status=kw['status'])            
        except Exception as err:
            log.failed(err)
            raise(err)
        if not rlst:
            return
        rlst = filter(lambda x: x['file'] not in kw['skip'], rlst)
        log.info('found %-d files after skip', len(rlst), operation=kw['operation'], status=kw['status'])            
        if not len(rlst):
            return(None)
        rec = rlst[0]
        log.enter('preparing new working folder', **rec)
        try:
            meta = {}
            if kw['operation'].endswith('_'):
                meta['nc_group'] = rec['status'].split('_')[-1]
                kw['operation'] += meta['nc_group']
                log.info('operation updated to %s', kw['operation'])
            pool  = PoolRoot()
            clst  = pool.cnames_from_dict(rec)
            cdict = pool.cdict_from_names(*clst)
            root  = processorRoot(kw['operation'])
            work  = root.folder()
            for k in cdict.keys():
                work.meta[k] = cdict[k]
            for k in rec.keys():
                if k not in cdict:
                    work[k] = rec[k]
            pdir = pool.bottom(*clst)
            fsrc = os.path.join(pdir.path, rec['file'])
            work['nc_source'] = fsrc
            work['operation'] = kw['operation']
            if 'nc_group' in meta:
                work['nc_group'] = meta['nc_group']
            work.meta.write()
            log.success('new processor folder', path=work.path, nc_source=fsrc)
        except Exception as err:
            log.failed(err)
            raise(err)            
        return(work)
    
    @classmethod
    def execute(cls, *args, **kw):
        lopts = {}
        if 'lopts' in kw:
            lopts = kw['lopts']
            del kw['lopts']
        skip  = []
        redo  = []
        kw    = cls.defaults(**kw)
        kw0   = dict(kw)
        pool  = PoolRoot()
        done  = False
        count = 0
        while not done:
            kw = dict(kw0)
            kw['skip'] = map(lambda x: x['file'], skip)
            fm = cls.nextPending(**kw)
            if not fm:
                fm = cls.newPending(**kw)
            if not fm:
                done = True
                continue
            r = None
            kw['operation'] = fm['operation']
            kw['status']    = fm['status']
            log.enter('found %s task', kw['operation'], path=fm.path)
            try:
                fsrc = fm['nc_source']                
                fdst = os.path.join(fm.path, os.path.basename(fsrc))
                if os.path.exists(fdst):
                    os.unlink(fdst)
                opts = { 'working_copy': True, 'working_folder': fm.path, 'version': True }
                opts.update(lopts)
                with pool.lock(fsrc, **opts) as ncf:
                    r = cls.process(ncf, fm, *args)
                fm.rmtree()
                log.success()
            except LockTimeout:
                ncbase = fm['file']
                redo.append({ 'file': ncbase, 'opid': kw['operation'], 'stid': kw['status']})        
                fm.rmtree() 
                log.warning('operation cancelled due to lock file', file=ncbase, operation=kw['operation'])       
                log.success('operation cancelled')
            except Exception as err:
                log.failed(err)
                ncbase = fm['file']
                redo.append({ 'file': ncbase, 'opid': kw['operation'], 'stid': kw['status']})        
                fm.failed()
            if r:
                log.info('registering file status', file=fsrc)
                db  = PoolDB.PoolDB()
                if kw['next']:
                    db.update_file_status(fsrc, kw['next'])
                db.close()
            else:
                ncbase = os.path.basename(fsrc)
                redo.append({ 'file': ncbase, 'opid': kw['operation'], 'stid': kw['status']})        
            ncbase = os.path.basename(fsrc)
            skip.append({ 'file': ncbase, 'opid': kw['operation'], 'stid': kw['status']})        
            count += 1
        if count > 0:
            log.info('registering operation')   
            oplst = set(map(lambda x: x['opid'], skip))    
            db  = PoolDB.PoolDB()
            for op in oplst:
                db.update_operation(op)
            db.close()
        for f in redo:
            log.info('renewing file status', file=f)
            db  = PoolDB.PoolDB()
            for r in redo:
                db.update_file_status(r['file'], r['stid'])
            db.close()            
        return

class OpBasedOperation(object):

    OPERATION_NAME = None

    @classmethod
    def process(cls, *args):
        assert False, 'this method has to be subclassed'
        return

    @classmethod
    def todoList(cls, **kw):
        assert False, 'this method has to be subclassed'
        return

    @classmethod
    def execute(cls, *args, **kw):
        kw['operation'] = cls.OPERATION_NAME
        lst  = cls.todoList()
        log.enter('found %-d items for task %s', len(lst), kw['operation'], **kw)
        try:
            for item in lst:
                cls.process(item)
        except LockTimeout:
            log.warning('operation cancelled due to lock file', operation=kw['operation'])       
            log.success('operation cancelled')
        except Exception as err:
            log.failed(err)
        else:
            db  = PoolDB.PoolDB()
            db.update_operation(kw['operation'])
            db.close()
        return
    

        
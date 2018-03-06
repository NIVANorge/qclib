
import os
import re

from pyTools.Compression import zip
from pyTools.Compression import bzip2
from pyTools.Compression import gz


from .. import Loggers

from ..FolderManagers import IncomingRoot
from ..FolderManagers import repackagingRoot
from ..FolderManagers import TMPRoot


log = Loggers.getLogger(__name__)

    
class Incoming(object):
    
    def pending(self):
        done = False
        try:
            # Check for pending repackaging
            rrep = repackagingRoot()
            drep = rrep.nextFolder()
            # Check for new incoming files
            irep = IncomingRoot()
            frep = irep.nextFile()
            # Process
            if drep:
                log.info('found pending repackaging folder', source=drep.name)
                self.repackage(drep)
                rrep.cleanup()
            elif frep:
                log.info('found pending incoming file', source=frep)
                irep.deliverFile(frep)
            else:
                log.info('no new files')
                done = True
        except Exception as err:
            log.failed(err)
            raise(err)
        return(done)
    
    def repackage(self, drep):
        log.enter('repackaging', source=drep.name)
        try:
            o = Repackaging()
            o.process(drep)
            log.success()
        except Exception as err:
            log.failed(err)
            drep.failed()
            #raise(err)
        return
        
        
            
class Repackaging(object):
                            
                            
    def unzip(self, fm):
        flst = fm.files(regex='\.zip$', recursive=True)
        while flst:
            log.info('found %-d zip files', len(flst), zip=len(flst))
            for f in flst:
                f = os.path.join(fm.path, f)
                log.enter('uncompressing file', source=f)
                try:
                    zip.unzip(f, delete=True)
                    log.success()
                except Exception as err:
                    log.failed(err)
                    raise(err)
            flst = fm.files(regex='\.zip$', recursive=True)
        return
        
    def unbzip2(self, fm):
        flst = fm.files(regex='\.txt.bz2$', recursive=True)
        log.info('found %-d bz2 files', len(flst), bz2=len(flst))
        for f in flst:
            f = os.path.join(fm.path, f)
            log.enter('uncompressing file', source=f)
            try:
                bzip2.uncompress(f, True)
                log.success()
            except Exception as err:
                log.failed(err)
                raise(err)
        return
    
    def ungzip(self, fm):
        flst = fm.files(regex='\.txt.gz$', recursive=True)
        log.info('found %-d gz files', len(flst), gz=len(flst))
        for f in flst:
            f = os.path.join(fm.path, f)
            log.enter('uncompressing file', source=f)
            try:
                gz.uncompress(f, True)
                log.success()
            except Exception as err:
                log.failed(err)
                raise(err)
        return
        
    def process(self, fm):
        fm.meta.write()
        self.unzip(fm)
        self.unbzip2(fm)
        self.ungzip(fm)
        # Find TXT files
        flst = fm.files(regex='\.txt$', recursive=True)
        log.info('found %-d txt files', len(flst), txt=len(flst))
        # Find TXT files
        flst = fm.files(regex='\.txt$', recursive=True)
        log.info('found %-d txt files', len(flst), txt=len(flst))
        if len(flst) > 1:
            try:
                for f in flst:
                    f = os.path.join(fm.path, f)
                    assert False, 'run in debugger'
                    self.redistribute(f)
                log.success()
            except Exception as err:
                log.failed(err)
                raise(err)
        elif len(flst) == 1:
            log.enter('delivering file')
            try:
                fm.meta['source_log'] = os.path.basename(flst[0])
                fm.meta.write()
                zipf = fm.tmpArchive(flst, prefix=fm.processor_name)
                pdst = fm.deliverFile(zipf)
                fsrc = os.path.join(fm.path, flst[0])
                os.unlink(fsrc)
                os.unlink(zipf)
                TMPRoot().cleanup()
                log.success(archive=pdst)
            except Exception as err:
                log.failed(err)
                raise(err)
        flst = fm.files(recursive=True)
        log.info('found %-d remaining files', len(flst), mdb=len(flst))
        if len(flst) > 0:
            log.enter('archiving other files')
            try:
                zipf = fm.tmpArchive(flst, prefix='other')
                adst = fm.archiveFile(zipf)
                os.unlink(zipf)
                for f in flst:
                    os.unlink(os.path.join(fm.path, f))
                log.success(archive=adst)
            except Exception as err:
                log.failed(err)
                raise(err)
        return      

    def redistribute(self, f):
        log.enter('redistributing incoming file', file=f, source=self.name)
        try:
            assert False, 'redistribute files: run in debugger'
            log.success()
        except Exception as err:
            log.failed(err)
            raise(err)
        return
      

    
             
            
        
            
        


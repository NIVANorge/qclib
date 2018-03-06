"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry._FolderManagers.FolderManagers
===========================



(C) 31. mai 2016 Pierre Jaccard
"""

import os

import netCDF4

from pyTools import FolderManagers
from pyTools.netCDF import ncOperations

from . import Loggers
from . import ConfigManager 
from . import Globals
from . import Main

TMPFOLDER        = ConfigManager.abspath(ConfigManager.sysconf['folders']['tmp'])
FAILEDFOLDER     = ConfigManager.abspath(ConfigManager.sysconf['folders']['failed'])
ARCHIVEFOLDER    = ConfigManager.abspath(ConfigManager.sysconf['folders']['archives'])
PENDINGFOLDER    = ConfigManager.abspath(ConfigManager.sysconf['folders']['pending'])
PROCESSINGFOLDER = ConfigManager.abspath(ConfigManager.sysconf['folders']['processing'])
INCOMINGFOLDER   = ConfigManager.abspath(ConfigManager.sysconf['folders']['incoming'])
IMPORTCONFROOT   = ConfigManager.abspath(ConfigManager.sysconf['import']['config_root'])
POOLFOLDER       = ConfigManager.abspath(ConfigManager.sysconf['folders']['pool'])
VERSIONFOLDER    = ConfigManager.abspath(ConfigManager.sysconf['folders']['versions'])
LOCKFOLDER       = ConfigManager.abspath(ConfigManager.sysconf['folders']['lock'])

log = Loggers.getLogger(__name__)


class TMPRoot(FolderManagers.TMPRoot):
    
    def __init__(self):
        super(TMPRoot, self).__init__(TMPFOLDER)
        return

class FailedFolder(FolderManagers.FailedFolder):
    
    def __init__(self, name):
        path = os.path.join(FAILEDFOLDER, name)
        super(FailedFolder, self).__init__(path, 'repository')
        return
        
class ArchiveRoot(FolderManagers.CategoryTree):
    
    def __init__(self):
        clst = [ 'archive' ] + list(Globals.CATEGORIES)
        super(ArchiveRoot, self).__init__(ARCHIVEFOLDER, *clst, bottom_class=FolderManagers.VersionFolder)
        return

class VersionRoot(FolderManagers.CategoryTree):
    
    def __init__(self):
        opts = { 'bottom_class': FolderManagers.VersionFolder }
        super(VersionRoot, self).__init__(VERSIONFOLDER, *Globals.CATEGORIES, **opts)
        return
    
    
class PendingFolder(FolderManagers.FolderManager):
    
    def __init__(self):
        super(PendingFolder, self).__init__(PENDINGFOLDER)
        return
   
    def newPackage(self, fsrc, *prefix):
        """
        Install a new file (usually a zipped archive) into the pending folder.
        Prefix keywords should be the name of the processor and its ID source.
        """ 
        prefix = list(prefix)
        base = os.path.basename(fsrc)
        fdst = os.path.join(self.path, '_'.join(prefix + [base]))
        fdst = TMPRoot().copy(fsrc, fdst)
        return(fdst)

    def nextPending(self, prefix):
        regf = '^' + prefix + '.*.zip' 
        flst = self.files(regexf=regf)
        if len(flst):
            return(flst[0])
        return
    

class IncomingRoot(FolderManagers.CategoryTree):
        
    def __init__(self, *args, **kw):
        if args:
            super(IncomingRoot, self).__init__(*args, **kw)
        else:       
            super(IncomingRoot, self).__init__(INCOMINGFOLDER, *Globals.CATEGORIES, bottom_class=FolderManagers.FolderManager)
        return

    def files(self, **opts):
        """
        Return a list of files at the bottom of the category tree, but sort
        them according to basename in reverse order.
        """
        dlst = self.folders(**opts)
        flst = []
        for d in dlst:
            lst = d.files(**opts)
            lst = map(lambda x: os.path.join(d.path, x), lst)
            flst += lst
        blst = map(lambda x: (x, os.path.basename(flst[x])), range(len(flst)))
        blst.sort(lambda x,y: cmp(y[1],x[1]))
        flst = map(lambda x: flst[x[0]], blst)
        return(flst)


    def deliverFile(self, fsrc):
        cmeta = self.cdict_from_path(fsrc)
        log.enter('delivering incoming file', source=fsrc, **cmeta)
        try:
            a    = ArchiveRoot().bottom('incoming', *self.cnames_from_path(fsrc))
            adst = a.newVersion(fsrc)
            log.info('new archive', archive=adst)
            rrep = repackagingRoot()
            drep = rrep.processor(rrep.name, fsrc)
            drep.meta.update(cmeta)
            drep['source_file'] = fsrc
            log.info('new processor', processor=drep.processor_name, source=drep.name)
            os.unlink(fsrc)
            log.success()
        except Exception as err:
            log.failed(err)
            raise(err)
        return
    
class ProcessingFolder(FolderManagers.ProcessingFolder):
    
    def __init__(self, path, *args, **kw):
        if ('metafile' not in kw):
            kw['metafile'] = Globals.FolderMetaFile
        if ('logfile' not in kw):
            kw['logfile'] = Globals.FolderLogFile
        if 'processor_name' not in kw:
            kw['processor_name'] = os.path.basename(os.path.dirname(path))
        super(ProcessingFolder, self).__init__(path, *args, **kw)
        return

    def tmpArchive(self, files, prefix=None):
        log.enter('creating TMP archive', processor=self.processor_name, source=self.name)
        try:
            tmp  = TMPRoot().folder()
            base = self.name + '.zip'
            if prefix:
                base = prefix + '_' + base
            zipf = os.path.join(tmp.path, base)
            zipf = self.zip(zipf, *files, add_meta=True, add_log=True)
            log.success(archive=zipf)
        except Exception as err:
            log.failed(err)
            raise(err)
        return(zipf)

    def archiveFile(self, zipf):
        log.enter('archiving file', archive=zipf, processor=self.processor_name, source=self.name)
        try:
            a    = ArchiveRoot().bottom(self.processor_name, *self.cnames())
            adst = a.newVersion(zipf)
            if 'archive' not in self:
                self['archives'] = {}
            self['archives'][os.path.basename(zipf)] = adst
            log.success('new archive', archive=adst)
        except Exception as err:
            log.failed(err)
            raise(err)
        return(adst)
                
    def deliverFile(self, zipf):
        log.enter('delivering files', archive=zipf, processor=self.processor_name, source=self.name)
        try:
            pdst = PendingFolder().newPackage(zipf)
            if 'deliveries' not in self:
                self['deliveries'] = {}
            self['deliveries'][os.path.basename(zipf)] = pdst
            log.success('new pending package', package=pdst)
        except Exception as err:
            log.failed(err)
            raise(err)
        return(pdst)
                    
    def cnames(self):
        """
        Generate base category names form META information
        """  
        c = map(lambda x: self.meta[x], Globals.CATEGORIES)
        return(c)

    def failed(self):
        froot = FailedFolder(self.processor_name)
        super(ProcessingFolder, self).failed(froot)
        return
        
class ProcessingRoot(FolderManagers.ProcessingTree):
    
    def __init__(self, name, **kw):
        if 'bottom_class' not in kw:
            kw['bottom_class'] = ProcessingFolder
        path = os.path.join(PROCESSINGFOLDER, name)
        super(ProcessingRoot, self).__init__(path, **kw)
        return

def processorRoot(name):
    root = ProcessingRoot(name)
    return(root)
        
def repackagingRoot():
    return(processorRoot('repackaging'))

def importRoot():
    return(processorRoot('import'))
            
class ImportConfigs(FolderManagers.FolderManager):
    
    def __init__(self, provider, ship):
        path = os.path.join(IMPORTCONFROOT, provider, ship)
        super(ImportConfigs, self).__init__(path)
        return
    
    def configFiles(self):
        flst = self.files(regexf='\.ini$')
        flst = map(lambda x: os.path.join(self.path, x), flst)
        return(flst)
 
class PoolLock(FolderManagers.PoolLock):
    
    def __init__(self, *args, **kw):
        super(PoolLock, self).__init__(LOCKFOLDER, PoolRoot(), *args, **kw)
        return

class PoolRoot(FolderManagers.PoolRoot): 
    
    def __init__(self):
        opts = {
                'bottom_class'  : PoolFolder,
                'temp_folder'   : TMPRoot(),
                'version_folder': VersionRoot(),
                }
        super(PoolRoot, self).__init__(POOLFOLDER, *Globals.CATEGORIES, **opts)
        return
    
    def ncCategories(self, fnc):
        nc = netCDF4.Dataset(fnc, 'r')
        d  = dict(map(lambda x: (x, nc.getncattr(x)), nc.ncattrs()))
        clst = self.cnames_from_dict(d)
        clst = map(lambda x: x.upper(), clst)
        return(clst)       
        
    def addFile(self, fnc, **kw):
        clst = self.ncCategories(fnc)
        pdir = self.bottom(*clst)
        dst = pdir.addFile(fnc)
        return(dst)
    
    def mergeFile(self, fnc, merge_var, **kw):
        clst = self.ncCategories(fnc)
        pdir = self.bottom(*clst)
        dst = pdir.mergeFile(fnc, ncOperations.ncMerge.file, merge_var, **kw)
        return(dst)

    def sortFile(self, fnc, sort_var, grp):
        clst = self.ncCategories(fnc)
        pdir = self.bottom(*clst)
        dst  = pdir.sortFile(fnc, ncOperations.ncSort.file, sort_var, grp)
        return(dst)

    @classmethod
    def lock(cls, *args, **kw):
        lobj = PoolLock(*args, **kw)
        return(lobj)
        
    def newVersion(self, fsrc, lock=False):
        vdst = super(PoolRoot, self).newVersion(fsrc, lock=lock, vroot=VersionRoot())
        return(vdst)

    def sortData(self, fnc, sort_var, grp):
        clst = self.ncCategories(fnc)
        pdir = self.bottom(*clst)
        assert False, 'not implemented yet'
        
class PoolFolder(FolderManagers.PoolFolder):
    pass



        
        
    

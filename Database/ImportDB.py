
import os
import re
import hashlib

from .. import Loggers

log = Loggers.getLogger(__name__)

from . import Schema

WHITE_REG = re.compile('\s+', flags=re.UNICODE)

class ImportDB(Schema.Database):
    

    def md5(self, f):
        md5 = hashlib.md5()
        fd  = open(f, 'rb')
        for l in fd:
            l = WHITE_REG.sub('', l)
            md5.update(l)
        fd.close()
        return(md5.hexdigest())
                       
    def register_import(self, provider, platform, fsrc):
        try:
            platform_rec = self.get_insert(Schema.Platform, code=platform)
            provider_rec = self.get_insert(Schema.Provider, code=provider)
            md5          = self.md5(fsrc)
            file_rec     = self.get_insert(Schema.RawFile, 
                                       name=os.path.basename(fsrc),
                                       md5=md5, 
                                       id_platform=platform_rec.id, 
                                       id_provider=provider_rec.id)
            self.get_insert(Schema.Import, id_file=file_rec.id)
            log.info('registered new import', file=fsrc, md5=md5, platform=platform, provider=provider)
        except Exception as err:
            raise(err)
        return
    
    def is_imported(self, provider, platform, fsrc):
        try:
            platform_rec = self.first(Schema.Platform, code=platform)
            provider_rec = self.first(Schema.Provider, code=provider)
            test = (platform_rec is not None) & (provider_rec is not None)
            if test:
                md5       = self.md5(fsrc)
                file_rec  = self.first(Schema.RawFile, name=os.path.basename(fsrc), md5=md5, 
                                      id_platform=platform_rec.id, id_provider=provider_rec.id)
                test &= (file_rec is not None)
                if test:           
                    log.info('import already performed', file=fsrc, md5=md5, platform=platform, provider=provider)
        except Exception as err:
            raise(err)
        return(test)
        
    
    
    
        

        

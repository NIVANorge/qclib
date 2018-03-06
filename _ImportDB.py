"""
.. moduleauthor: Pierre Jaccard <pja@niva.no>

pyFerry._PoolDB
==============



(C) 4. feb. 2016 Pierre Jaccard
"""

import os
import re
import datetime
import hashlib

from pyTools.Database.SqlAlchemy import Interfaces

from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sqa
import sqlalchemy.orm as orm

from . import Loggers
from . import ConfigManager

log = Loggers.getLogger(__name__)

DBFILE = ConfigManager.abspath(ConfigManager.sysconf['import']['database'])

Base = declarative_base()

WHITE_REG = re.compile('\s+', flags=re.UNICODE)

#------------------------------------------------------------------------------- 
# SQLALCHEMY ORM Model
#------------------------------------------------------------------------------- 


class Platform(Base):
    __tablename__ = 'platforms'
    id    = sqa.Column(sqa.Integer, primary_key=True)
    code  = sqa.Column(sqa.String, unique=True)

class Provider(Base):
    __tablename__ = 'providers'
    id   = sqa.Column(sqa.Integer, primary_key=True)
    code = sqa.Column(sqa.String, unique=True)
        
class File(Base):
    __tablename__ = 'files'    
    id          = sqa.Column(sqa.Integer, primary_key=True)
    id_platform = sqa.Column(sqa.Integer, sqa.ForeignKey('platforms.id'))
    id_provider = sqa.Column(sqa.Integer, sqa.ForeignKey('providers.id'))
    time        = sqa.Column(sqa.DateTime, default=datetime.datetime.now)
    name        = sqa.Column(sqa.String, unique=False)
    md5         = sqa.Column(sqa.String, unique=True)
    platform    = orm.relationship("Platform" , backref=orm.backref('files', order_by=id))
    provider    = orm.relationship("Provider", backref=orm.backref('files', order_by=id))

class Import(Base):
    __tablename__ = 'imports'    
    id            = sqa.Column(sqa.Integer, primary_key=True)
    time          = sqa.Column(sqa.DateTime, default=datetime.datetime.now)
    id_file       = sqa.Column(sqa.Integer, sqa.ForeignKey('files.id'))
    file          = orm.relationship("File", backref=orm.backref('files', order_by=id))

#
# Class Utility
#

class Database(Interfaces.SQLiteInterface):
    
    def __init__(self):
        super(Database, self).__init__(DBFILE, Base)
        return

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
            platform_rec = self.get_insert(Platform, code=platform)
            provider_rec = self.get_insert(Provider, code=provider)
            md5          = self.md5(fsrc)
            file_rec     = self.get_insert(File, 
                                       name=os.path.basename(fsrc),
                                       md5=md5, 
                                       id_platform=platform_rec.id, 
                                       id_provider=provider_rec.id)
            log.info('registered new import', file=fsrc, md5=md5, platform=platform, provider=provider)
        except Exception as err:
            raise(err)
        return
    
    def is_imported(self, provider, platform, fsrc):
        try:
            platform_rec = self.first(Platform, code=platform)
            provider_rec = self.first(Provider, code=provider)
            test = (platform_rec is not None) & (provider_rec is not None)
            if test:
                md5       = self.md5(fsrc)
                file_rec  = self.first(File, name=os.path.basename(fsrc), md5=md5, 
                                      id_platform=platform_rec.id, id_provider=provider_rec.id)
                test &= (file_rec is not None)
                if test:           
                    log.info('import already performed', file=fsrc, md5=md5, platform=platform, provider=provider)
        except Exception as err:
            raise(err)
        return(test)
        
    
    
    
        

        

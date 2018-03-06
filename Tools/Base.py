"""
 .. moduleauthor: Pierre Jaccard <pja@niva.no>
 
 pyRamses.Tools._Processors
 ===========================
 
 
 
 (C) 2. feb. 2016 Pierre Jaccard
 """
 
from .. import Main
from .. import Loggers
      
log = Loggers.getLogger(__name__)
 
         
class BaseTool(object):
     
    def __init__(self):
        self.name = self.__class__.__name__.lower()
        return
         
    @classmethod
    def execute(cls, *args, **kw):
        self = cls()
        log.enter('running now tool', processor=self.name)
        try:
            m = Main.Main(lockname=self.name)
            with m.run():
                self.main(*args, **kw)
            log.success()
        except Exception as err:
            log.failed(err)
            raise err
        return
         
#         
# class PrepareMDB(ProcessorTool):
#     
#     _PROCESSOR_ = _Processors.PrepareMDB
# 
#     @classmethod
#     def process(cls, *args, **kw):
#         return(cls.execute(*args, **kw))
#     
#     cmd = Declare('processor.preparemdb', process, 'Launch prepareMDB processor')
#     cmd.register(TOOLSMGR)
# 
# class ConvertMDB(ProcessorTool):
# 
#     _PROCESSOR_ = _Processors.ConvertMDB
# 
#     @classmethod
#     def process(cls, *args, **kw):
#         return(cls.execute(*args, **kw))
# 
#     cmd = Declare('processor.convertmdb', process, 'Launch convertMDB processor')
#     cmd.register(TOOLSMGR)
# 
# class Calibrate(ProcessorTool):
# 
#     _PROCESSOR_ = _Processors.Calibrate
# 
#     @classmethod
#     def process(cls, *args, **kw):
#         return(cls.execute(*args, **kw))
# 
#     cmd = Declare('processor.calibrate', process, 'Launch calibrate processor')
#     cmd.register(TOOLSMGR)
# 
# class addNavigation(ProcessorTool):
# 
#     _PROCESSOR_ = _Processors.AddNavigation
# 
#     @classmethod
#     def process(cls, *args, **kw):
#         return(cls.execute(*args, **kw))
# 
#     cmd = Declare('processor.navigation', process, 'Launch navigation processor')
#     cmd.register(TOOLSMGR)
# 
# class addSun(ProcessorTool):
# 
#     _PROCESSOR_ = _Processors.AddSun
# 
#     @classmethod
#     def process(cls, *args, **kw):
#         return(cls.execute(*args, **kw))
# 
#     cmd = Declare('processor.sun', process, 'Launch sun angles processor')
#     cmd.register(TOOLSMGR)
# 
# 
# class trioCombine(ProcessorTool):
# 
#     _PROCESSOR_ = _Processors.TrioCombine
# 
#     @classmethod
#     def process(cls, *args, **kw):
#         return(cls.execute(*args, **kw))
# 
#     cmd = Declare('processor.trio.combine', process, 'Launch trio combine processor')
#     cmd.register(TOOLSMGR)
#    
# class trioGeoQC(ProcessorTool):
# 
#     _PROCESSOR_ = _Processors.TrioGeoQC
# 
#     @classmethod
#     def process(cls, *args, **kw):
#         return(cls.execute(*args, **kw))
# 
#     cmd = Declare('processor.trio.geoqc', process, 'Launch trio GEO QC processor')
#     cmd.register(TOOLSMGR)
# 
# class createMeris(ProcessorTool):
# 
#     _PROCESSOR_ = _Processors.MerisCreate
# 
#     @classmethod
#     def process(cls, *args, **kw):
#         return(cls.execute(*args, **kw))
# 
#     cmd = Declare('processor.meris.create', process, 'Launch MERIS creator')
#     cmd.register(TOOLSMGR)
# 
# class extractMeris(ProcessorTool):
# 
#     _PROCESSOR_ = _Processors.MerisExtract
# 
#     @classmethod
#     def process(cls, *args, **kw):
#         return(cls.execute(*args, **kw))
# 
#     cmd = Declare('processor.meris.extract', process, 'Launch MERIS extractor')
#     cmd.register(TOOLSMGR)

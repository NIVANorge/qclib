
from Error import Error

class ConfigFileError(Error)    : pass
class ConfigLoadError(Error)    : pass
class ConfigPathError(Error)    : pass
class ConfigTagError(Error)     : pass
class ConfigIncludeError(Error) : pass


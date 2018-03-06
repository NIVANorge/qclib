
import numpy as np
    
def copyDimension(dsrc, gdst):
    if dsrc.name not in gdst.dimensions:
        if dsrc.isunlimited():
            size=None
        else:
            size=dsrc.size
        ddst = gdst.createDimension(dsrc.name, size=size)
    else:
        ddst = gdst.dimensions[dsrc.name]
    return(ddst)
    
def copyVariable(vsrc, gdst, name=None):
    if name is None:
        name = vsrc.name
    if name not in gdst.variables:
        for n in vsrc.group().dimensions:
            dsrc = vsrc.group().dimensions[n]
            copyDimension(dsrc, gdst)
        vdst = gdst.createVariable(name, vsrc.dtype, vsrc.dimensions, fill_value=vsrc._FillValue)
        copyAttributes(vsrc, vdst)
    else:
        vdst = gdst.variables[name]
    return(vdst)
    
def copyAttributes(nsrc, ndst):
    adst = ndst.ncattrs()
    for a in nsrc.ncattrs():
        if a not in adst:
            v = nsrc.getncattr(a)
            ndst.setncattr(a, v)
    return
    
def copyGroup(gsrc, gdst):
    if gsrc.name not in gdst.groups:
        g = gdst.createGroup(gsrc.name)
    else:
        g = gdst.groups[gsrc.name]
    copyAttributes(gsrc, g)
    return(g)

def listVariables(gsrc):
    lst  = []
    glst = [ gsrc ]
    while len(glst) > 0:
        g = glst.pop()
        glst += g.groups.values()
        lst.append((g.path, g.variables.keys()))
    return(lst)

    
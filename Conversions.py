
import datetime
import numpy as np

DAY1950 = datetime.datetime(1950,1,1)

def timedelta_to_seconds(x):
    y = x.days*86400.0 + x.seconds + x.microseconds/1.e6
    return(y)


def datetime_to_day1950(x):
    if isinstance(x, np.ndarray):
        func = np.vectorize(datetime_to_day1950)
        dd   = func(x)
        return(dd)
    else:
        dt = x - DAY1950
        dd = dt.days + (dt.seconds+dt.microseconds/1.e6)/86400.0
    return(dd)

def day1950_to_datetime(x):
    if isinstance(x, np.ndarray):
        func = np.vectorize(day1950_to_datetime)
        dd   = func(x)
        return(dd)
    else:
        dt  = datetime.timedelta(days=x)
        day = DAY1950 + dt
    return(day)
    
def date_to_day1950(x):
    
    if isinstance(x, np.ndarray):
        func = np.vectorize(date_to_day1950)
        dd   = func(x)
        return(dd)
    else:
        dt = x - DAY1950.date()
        dd = dt.days + (dt.seconds+dt.microseconds/1.e6)/86400.0
    return(dd)

def day1950_to_date(x):
    dt  = datetime.timedelta(days=x)
    day = DAY1950.date() + dt
    return(day)
    
def days_in_month(x):
    d0 = datetime.date(x.year, x.month, 1)
    dt = datetime.timedelta(days=31)
    d1 = d0 + dt
    d1 = datetime.date(d1.year, d1.month, 1)
    dt = d1 - d0
    return(dt.days)

def first_day_of_month(x):
    return(datetime.datetime(x.year, x.month, 1))

def last_day_of_month(x):
    dt = days_in_month(x)
    d0 = first_day_of_month(x)
    d1 = d0 + datetime.timedelta(days=dt)
    d1 = d1 - datetime.timedelta(microseconds=1)
    return(d1) 
    
    
    
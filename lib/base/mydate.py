#-*- encoding:utf-8 -*-
'''
Created on 2013-3-28

@author: albertqiu
'''

import datetime


def get_datetime():
        (date,tm2,haomiao) = (None,None,0)
        try:
                dt = datetime.datetime.now()
                string = str(dt)
                (date,tm) = string.split(" ")
                tm_hm_list = tm.split(".")
                haomiao = 0
                tm2 = 0
                if len(tm_hm_list) == 2:
                        tm2 = tm_hm_list[0]
                        haomiao = int(float("0.%s" % tm_hm_list[1]) * 1000)
        except :
                pass
        return (date,tm2,haomiao)

def get_nowdate():
        (date,tm,hm) = get_datetime()
        return date

def get_nowtime():
        (date,tm,hm) = get_datetime()
        return "%s %s" % (date,tm)

def get_datetime_str():
        (date,tm2,haomiao) = get_datetime()
        date = date.replace("-", "")
        tm2 = tm2.replace(":", "")
        return str(date) + str(tm2) + str(haomiao)


if __name__== "__main__":
        dt = datetime.datetime.now()
        string = str(dt)
        (date,tm) = string.split(" ")
        (tm2,haomiao) = tm.split(".")
        haomiao = int(float("0.%s" % haomiao) * 1000)
        print (date,tm2,haomiao)
        
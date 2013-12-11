# -*- encoding=utf-8 -*-
'''
Created on 2013-3-28

@author: albertqiu
'''
import platform
import os
import types
from base import cmd
from base import mydate



def get_os_type():
        '''
        return: Windows  or  Linux
        '''
        os_vers = platform.system()
        return os_vers;


def get_local_ip():
        try:
                ip = ""
                if platform.system() == "Linux":
                        (res,error, retcode)= cmd.docmd("/sbin/ifconfig | grep -E 'eth0|em2' -A3 | grep -v eth1 | grep 'inet addr' | awk '{print $2;}' | cut -d: -f2")
                        ip = res[0]
                elif platform.system() == "Windows":
                        (res,error, retcode)  = cmd.docmd("ipconfig|grep 'IP Address'|awk -F: '{print \$2}'|sed \"s/ //g\"|grep -E '^172|^10|^192\.168'")
                        ip = res[0]
        except Exception,data:
                print data
        return ip


def get_cur_info():
        """Return the frame object for the caller's stack frame."""
        """ 获取文件名和方法名和行号"""
        try:
                raise Exception 
        except:
                import sys
                f = sys.exc_info()[2].tb_frame.f_back
                return (f.f_code.co_filename, f.f_code.co_name, f.f_lineno)
        

def fjson_out(json):
        from json import JSONDecoder
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        deconder = JSONDecoder()
        result = deconder.decode(json)
        pp.pprint(result)
        

def is_normal_env(iplist=""):
        '''
        iplist是ip列表或以分号分割的字符串，默认为空。当采用默认值时，ip为10.12.16.119或os为window
        '''
        ip_test_env = ["10.12.16.119"]
        
        if type(iplist) is types.StringType:
                res = iplist.split(";")
                ip_test_env.extend(res)
        elif type(iplist) is types.ListType:
                ip_test_env.extend(iplist)
                
        os_vers = platform.system()
        if  os_vers == "Windows":
                return False
        elif os_vers == "Linux" :
                ip = os.popen("/sbin/ifconfig eth1|grep 'inet addr'|awk -F: '{print $2}'|awk '{print $1}'").readlines()
                ip = str.strip(ip[0]);
                
                if ip in ip_test_env:
                        return False
                return True
        

def print_traceback_detail(flag=False):
        '''
        flag=True, return traceback info
        flag=False,print traceback info
        '''
        import traceback
        now = mydate.get_nowtime();
        tb = traceback.format_exc()
        if flag == False:
                print "[ %s ]:\n%s" % (now,tb)
        else:
                return "[ %s ]:\n%s" % (now,tb)
                        
        
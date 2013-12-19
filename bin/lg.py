# -*- encoding=utf8 -*-
import sys, os, signal

# 获取脚本文件的当前路径
def get_realpath():
        return os.path.split(os.path.realpath(__file__))[0]

def cur_file_dir():
        path = sys.path[0]
        if os.path.isdir(path):
                return path
        elif os.path.isfile(path):
                return os.path.dirname(path)

bin_path = get_realpath()
sys.path.append(bin_path + "/../lib")


from base import common
from base import mydate
from base import conf_helper as cfghelper
from base import output as ot
from base import cmd

import time
import getopt
import re


def get_pattern(*args):
        filters = [
                  "exit$",
                  "logout",
                  "sleep \d$",
                  "Connection",
                  "ast login",
                  "assword",
                  "spawn",
                  "authenticity of host",
                  "key fingerprint",
                  "continue connecting",
                  "ermanently added",
                  "#$",
                  "\$$",
                   #"^\[",
        ]
        for arg in args:
                filters.append(arg)
        pattern = "|".join(filters)
        return pattern

     

def signal_handler(signal, frame):
        pid = os.getpid();
        print ""
        print "kill these pids: ",pid
        os.system("kill -9 %d" % pid)
        sys.exit(0)

def usage(script):
        config = { "binpath": script}
        print "\
        usage: %(binpath)s  ip\n " % config
                                
def login(login_info, pattern="", timeout=120, debug=False, raw=True):
        """
        log_info = {ip:ip, user:user, passwd:passwd, port:port}
        return:
                 {"last_stdo":last_stdo, "stdo":stdo, "stde":stde, "retcode":retcode}
        """
        try:
                sshbin = bin_path +"/../tools/ssh2.exp"
                login_info["sshbin"] = sshbin
                cmdstr = "%(sshbin)s %(ip)s %(user)s  %(passwd)s  %(port)s" % login_info
                os.system(cmdstr)
        except Exception,data:
                common.print_traceback_detail()
                
def main():
        try:
                signal.signal(signal.SIGINT, signal_handler)
                
                try:
                        options,args = getopt.getopt(sys.argv[1:],"h:m", ["host=","man"])
                except getopt.GetoptError:
                        print "parse parameters error!"
                        common.print_traceback_detail()
                        sys.exit()
                
                default_hosts_path = bin_path+"/../etc/hosts"
                (hosts,man ) = (default_hosts_path, False)
        
                
                for name,value in options:
                        if name in ("-h","--hosts"):
                                hosts = value
                        if name in ("-m","--man"):
                                man = True
                                
                if man == True:
                        usage(sys.argv[0])
                        exit()
                        
                if not os.path.exists(hosts):
                        ot.error("hosts file:%s not exist!" % (hosts))
                        exit()

        
                cfghelper.parse_host(hosts)
                hosts = cfghelper.get_hosts("","")

                if len(hosts) > 1:
                        print "match more than one host!"
                        exit()
                        
                for srv_host in hosts:
                        ip = srv_host.get("ip", "")
                        if ip == sys.argv[1]:
                                srv_host = dict(srv_host)
                                gp_name = srv_host.get("group", "")
                                lid = srv_host.get("id", "")
                                user = srv_host.get("user", "")
                                passwd = srv_host.get("passwd", "")
                                port = srv_host.get("port", "")
                                ot.emphasize("==== group:%(group)s id:%(id)s  ip:%(ip)s  user:%(user)s  port:%(port)s ===="  % srv_host)
                                login(srv_host, timeout=120, debug=False, raw=True)
                                break;
        except Exception,data:
                common.print_traceback_detail()

        

main()




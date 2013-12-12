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
        usage: %(binpath)s  [options]\n\
        \n\
        options:\n\
                [[-h|--host] $hostfile]  host file path, if not assign, use default: ../etc/hosts \n\
                [[-g|--group] $group] which group\n\
                [[-i|--id] $id] which id\n\
                [[-t|--timeout] $timeout] cmd execute timeout, use 120s as default\n\
                [[-d|--debug]] if open debug flag, false as default\n\
                [[-m|--man]] show this page\n\
        note:\n\
                please assign group and id at the same! if you are confidence, \n\
                you can assign group or id at once time, even neither of them!\n\
        " % config
                                
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
                        options,args = getopt.getopt(sys.argv[1:],"h:g:i:t:dm", ["host=", "group=", "id=", "timeout=", "debug", "man"])
                except getopt.GetoptError:
                        print "parse parameters error!"
                        common.print_traceback_detail()
                        sys.exit()
                
                default_hosts_path = bin_path+"/../etc/hosts"
                (hosts, group, id, timeout, debug, man ) = (default_hosts_path, False, False, 120, False, False)
        
                
                for name,value in options:
                        if name in ("-h","--hosts"):
                                hosts = value
                        if name in ("-g","--group"):
                                group = value
                        if name in ("-i","--id"):
                                id = value
                        if name in ("-t","--timeout"):
                                timeout = int(value)
                        if name in ("-d","--debug"):
                                debug = True
                        if name in ("-m","--man"):
                                man = True
                                
                if man == True:
                        usage(sys.argv[0])
                        exit()
                        
                if not os.path.exists(hosts):
                        ot.error("hosts file:%s not exist!" % (hosts))
                        exit()
        
                if group == False and id ==False:
                        if not yesflag:
                                ot.warn("not assign group or id, this tool will affect all host!")
                                answer = raw_input("Are you sure?[yes|no]:")
                                answer = str.lower(answer)
                                if answer not in ("yes", "y"):
                                        exit()
        
                cfghelper.parse_host(hosts)
                hosts = cfghelper.get_hosts(group,id)

                if len(hosts) > 1:
                        print "match more than one host!"
                        exit()
                        
                for srv_host in hosts:
                        srv_host = dict(srv_host)
                        gp_name = srv_host.get("group", "")
                        lid = srv_host.get("id", "")
                        ip = srv_host.get("ip", "")
                        user = srv_host.get("user", "")
                        passwd = srv_host.get("passwd", "")
                        port = srv_host.get("port", "")
                        ot.emphasize("==== group:%(group)s id:%(id)s  ip:%(ip)s  user:%(user)s  port:%(port)s ===="  % srv_host)
                        login(srv_host, timeout=120, debug=False, raw=True)
        except Exception,data:
                common.print_traceback_detail()

        

main()




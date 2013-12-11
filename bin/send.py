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
                [[-c|--cmd] $cmdstr] cmd string\n\
                [[-g|--group] $group] which group\n\
                [[-i|--id] $id] which id\n\
                [[-s|--src] $srcfile] source files or directory\n\
                [[-z|--dest] $destpath] destination path\n\
                [[-t|--timeout] $timeout] cmd execute timeout, use 120s as default\n\
                [[-d|--debug]] if open debug flag, false as default\n\
                [[-m|--man]] show this page\n\
        note:\n\
                please assign group and id at the same! if you are confidence, \n\
                you can assign group or id at once time, even neither of them!\n\
        " % config
                                
def execute(sshbin, login_info, cmdstr="", pattern="", timeout=120, debug=False, raw=True):
        """
        log_info = {ip:ip, user:user, passwd:passwd, port:port}
        return:
                 {"last_stdo":last_stdo, "stdo":stdo, "stde":stde, "retcode":retcode}
        """
        try:
                sshbin = bin_path +"/../tools/ssh.exp"
                login_info["sshbin"] = sshbin
                login_info["cmd"] = cmdstr
                cmdstr = "%(sshbin)s %(ip)s %(user)s  %(passwd)s  %(port)s  '%(cmd)s' " % login_info
                (stdo, stde, retcode) = cmd.docmd(cmdstr, timeout=timeout, debug=debug, raw=raw)
                
                last_stdo = []
                for so in stdo:
                        if not re.search(pattern, str.strip(so)):
                                last_stdo.append(so)
                return {"last_stdo":last_stdo, "stdo":stdo, "stde":stde, "retcode":retcode}
        except Exception,data:
                common.print_traceback_detail()
        

def send(scpbin, login_info, src, dest, direction="push", pattern="", timeout=120, debug=False, raw=True):
        """
        log_info = {ip:ip, user:user, passwd:passwd, port:port}
        return:
                 {"last_stdo":last_stdo, "stdo":stdo, "stde":stde, "retcode":retcode}
        """
        try:
                login_info["scpbin"] = scpbin
                login_info["src"] = src
                login_info["dest"] = dest
                login_info["direction"] = direction
                cmdstr = "%(scpbin)s %(ip)s %(user)s  %(passwd)s  %(port)s   %(src)s  %(dest)s  %(direction)s"  % login_info
                (stdo, stde, retcode) = cmd.docmd(cmdstr, timeout=timeout, debug=debug, raw=raw)
                
                last_stdo = []
                for so in stdo:
                        if not re.search(pattern, str.strip(so)):
                                last_stdo.append(so)
                return {"last_stdo":last_stdo, "stdo":stdo, "stde":stde, "retcode":retcode}
        except Exception,data:
                common.print_traceback_detail()
                                
def deploy(login_info, src, dest, direction="push", pattern="", timeout=120, debug=False, raw=True, show=False):
        """
        log_info = {ip:ip, user:user, passwd:passwd, port:port}
        return:
                 none
        """
        try:
                if not os.path.exists(src):
                        ot.error("src: %s not found!" % (src))
                        return;
                scpbin = bin_path+"/../tools/scp.exp"
                res = send(scpbin, login_info, src, dest, direction=direction, pattern=pattern, timeout=timeout, debug=debug, raw=raw)
                retcode = res["retcode"]
                last_stdo = res["last_stdo"]
                stdo = res["stdo"]
                stde = res["stde"]
                if retcode == 0:
                        ot.info("deploy src:%s to dest:%s success!\n"  % (src, dest))
                        if show == True:
                                for so in stdo:
                                        if not re.search(pattern, str.strip(so)):
                                                print so
                else:
                        ot.info("deploy src:%s to dest:%s failure!\n"  % (src, dest))
                        if show == True:
                                for so in stdo:
                                        ot.error(so)
                                for eo in stde:
                                        ot.error(eo)
        except Exception,data:
                common.print_traceback_detail()


def main():
        try:
                signal.signal(signal.SIGINT, signal_handler)
                
                try:
                        options,args = getopt.getopt(sys.argv[1:],"h:c:g:i:s:z:t:dm", ["host=", "config=", "group=", "id=", "src=", "dest=", "timeout=", "debug", "man"])
                except getopt.GetoptError:
                        sys.exit()
                
                default_hosts_path = bin_path+"/../etc/hosts"
                (hosts, cmdstr, group, id, timeout, debug, man ) = (default_hosts_path, False, False, False, 120, False, False)
                (srcfiles, destdir) = ("", "")
        
                
                for name,value in options:
                        if name in ("-h","--hosts"):
                                hosts = value
                        if name in ("-c","--cmd"):
                                cmdstr = value
                        if name in ("-g","--group"):
                                group = value
                        if name in ("-i","--id"):
                                id = value
                        if name in ("-a","--action"):
                                action = value
                        if name in ("-s","--src"):
                                srcfiles = value
                        if name in ("-z","--dest"):
                                destdir = value
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
                        ot.warn("not assign group or id, this tool will affect all host!")
                        answer = raw_input("Are you sure?[yes|no]:")
                        answer = str.lower(answer)
                        if answer not in ("yes", "y"):
                                exit()
        
                cfghelper.parse_host(hosts)
                hosts = cfghelper.get_hosts(group,id)

                for srv_host in hosts:
                        srv_host = dict(srv_host)
                        gp_name = srv_host.get("group", "")
                        lid = srv_host.get("id", "")
                        ip = srv_host.get("ip", "")
                        user = srv_host.get("user", "")
                        passwd = srv_host.get("passwd", "")
                        port = srv_host.get("port", "")
                        
                        ot.emphasize("==== group:%(group)s id:%(id)s  ip:%(ip)s  user:%(user)s  port:%(port)s ===="  % srv_host)
                        pattern = get_pattern("%s$" % (cmdstr))
                        deploy(srv_host, srcfiles, destdir, direction="push", pattern="", timeout=120, debug=debug, raw=True, show=True)
        except Exception,data:
                common.print_traceback_detail()

        

main()




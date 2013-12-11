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
from base import log
from base import mydate
from base import conf_helper as cfghelper
from base import output as ot
from base import cmd

import time
import getopt
import re

def dolog(logstr, logdir=bin_path+"/../var/log", file_prefix="deploy"):
        try:
                nowdate = mydate.get_nowdate()
                nowdtstr = mydate.get_nowtime()
                logp = "%s/%s_%s.txt" % (logdir,file_prefix,nowdate)
                if file_prefix == "" :
                        logp = "%s/%s.txt" % (logdir,nowdate)
                logstr = "[%s]:\n%s\n\n" % (nowdtstr,logstr)
                fh = open(logp, "a+")
                fh.write(logstr)
                fh.close()
        except Exception,data:
                common.print_traceback_detail()


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
                [[-c|--conf] $conffile] config file path, if not assign, use default: ../etc/deploy.cfg\n\
                [[-g|--group] $group] which group\n\
                [[-i|--id] $id] which id\n\
                [[-a|--action] $action] value in ('start', 'stop' , ''restart, 'status', 'deploy')\n\
                [[-t|--timeout] $timeout] cmd execute timeout, use 120s as default\n\
                [[-d|--debug]] if open debug flag, false as default\n\
                [[-m|--man]] show this page\n\
                [[-y|--yes]] when not assign group and id, but set yes flag open,\n\
                                will execute directly but do not need to confirm!\n\
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
                
                dolog((stdo, stde, retcode))
                last_stdo = []
                for so in stdo:
                        if not re.search(pattern, str.strip(so)):
                                last_stdo.append(so)
                return {"last_stdo":last_stdo, "stdo":stdo, "stde":stde, "retcode":retcode}
        except Exception,data:
                dolog(data)
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
                dolog((stdo, stde, retcode))
                last_stdo = []
                for so in stdo:
                        if not re.search(pattern, str.strip(so)):
                                last_stdo.append(so)
                return {"last_stdo":last_stdo, "stdo":stdo, "stde":stde, "retcode":retcode}
        except Exception,data:
                dolog(data)
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

def do_action(login_info, cmdstr="", pattern="", timeout=120, debug=False, raw=True):
        try:
                sshbin = bin_path+"/../tools/ssh.exp"
                res = execute(sshbin, login_info, cmdstr=cmdstr, pattern=pattern, timeout=timeout, debug=debug, raw=raw)
                retcode = res["retcode"]
                last_stdo = res["last_stdo"]
                stdo = res["stdo"]
                stde = res["stde"]
                if retcode == 0:
                        for so in stdo:
                                if not re.search(pattern, str.strip(so)):
                                        print so
                else:
                        for so in stdo:
                                ot.error(so)
                        for eo in stde:
                                ot.error(eo)
                print ""
        except Exception,data:
                common.print_traceback_detail()
                
def main():
        try:
                signal.signal(signal.SIGINT, signal_handler)
                
                try:
                        options,args = getopt.getopt(sys.argv[1:],"h:c:g:i:a:t:dmy", ["host=", "config=", "group=", "id=", "action=", "timeout=", "debug", "man", "yes"])
                except getopt.GetoptError:
                        sys.exit()
                
                #命令行参数数据存储
                default_deploy_path = bin_path+"/../etc/deploy.cfg"
                default_hosts_path = bin_path+"/../etc/hosts"
                (hosts, config, group, id, action, timeout, debug, man, yesflag ) = (default_hosts_path, default_deploy_path, False, False, False, 120, False, False, False)
        
                
                for name,value in options:
                        if name in ("-h","--hosts"):
                                hosts = value
                        if name in ("-c","--config"):
                                config = value
                        if name in ("-g","--group"):
                                group = value
                        if name in ("-i","--id"):
                                id = value
                        if name in ("-a","--action"):
                                action = value
                        if name in ("-t","--timeout"):
                                timeout = int(value)
                        if name in ("-d","--debug"):
                                debug = True
                        if name in ("-m","--man"):
                                man = True
                        if name in ("-y","--yes"):
                                yesflag = True
                                
                if man == True:
                        usage(sys.argv[0])
                        exit()
                        
                if not os.path.exists(hosts):
                        ot.error("hosts file:%s not exist" % (hosts))
                        exit()
                        
                if not os.path.exists(config):
                        ot.error("config file:%s not exist" % (config))
                        exit()
        
                if action not in ("start", "stop", "status", "restart", "deploy", "undeploy"):
                        ot.error("wrong action:%s" % (action))
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
                
                deploy_conf = cfghelper.parse_deploy_cfg(config)
                default_src = deploy_conf.get("src", "")
                default_dest = deploy_conf.get("dest", "")
                
                if not hosts:
                        ot.info("no any host match!")
        
                for srv_host in hosts:
                        srv_host = dict(srv_host)
                        gp_name = srv_host.get("group", "")
                        lid = srv_host.get("id", "")
                        ip = srv_host.get("ip", "")
                        user = srv_host.get("user", "")
                        passwd = srv_host.get("passwd", "")
                        port = srv_host.get("port", "")
                        src = srv_host.get("src", default_src)
                        dest = srv_host.get("dest", default_dest)
                        
                        if action in ("deploy"):
                                pattern = get_pattern();
                                ot.emphasize("==== group:%(group)s id:%(id)s  ip:%(ip)s  user:%(user)s  port:%(port)s ===="  % srv_host)
                                deploy(srv_host, src, dest, direction="push", pattern=pattern, timeout=120, debug=False, raw=True, show=False)
                        if action in("start", "stop", "status", "restart", "undeploy"):
                                cmdstr = "cd %s  && chmod a+x ./* &&  ./run.sh %s"  % (dest, action)
                                if action == "undeploy":
                                        if not dest:
                                                continue
                                        cmdstr = "rm  %s -fr"  % (dest)
                                ot.emphasize("==== group:%(group)s id:%(id)s  ip:%(ip)s  user:%(user)s  port:%(port)s ===="  % srv_host)
                                ot.info("execute: %s"  % cmdstr )
                                pattern = get_pattern("%s$" % (cmdstr))
                                do_action(srv_host, cmdstr=cmdstr, pattern=pattern, timeout=120, debug=debug, raw=True)
        except Exception,data:
                common.print_traceback_detail()

        

main()




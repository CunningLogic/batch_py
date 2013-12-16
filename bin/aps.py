#!/usr/bin/python
# -*- encoding=utf8 -*-
import sys, os
# 获取脚本文件的当前路径
def get_realpath():
        return os.path.split(os.path.realpath(__file__))[0]

bin_path = get_realpath()
sys.path.append(bin_path + "/../lib/")

from base import common
from base import mydate
from base import output as ot
from base import conf_helper as cfghelper
from base import cmd

import re
import signal
import getopt

"""
远程执行脚本，批处理: 
iplist: 配置IP以及用户名、密码、端口文件
conf: 配置需要远程传输的文件及路径、需要远程执行的命令
"""

def signal_handler(signal, frame):
        pid = os.getpid();
        print ""
        print "kill these pids: ",pid
        os.system("kill -9 %d" % pid)
        sys.exit(0)

def usage(script):
        config = { "binpath": script}
        print "\
        usage: %s  -i|--iplist $iplist [options]\n\
        \n\
        options:\n\
                [-h|--help] print this page and exit \n \
                [-D|--debug] debug flag, when set console will print more infomation when do remote call \n \
                [-l|local]  when set this flag, no need to assign (user,ip), if not must assign (user, ip) at the same time \n \
                [-c|--cmd $cmd] command \n \
        Example:\n \
                %(binpath)s -d -c 'ifconfig' -i $iplist     #default model, use user=root, port=22, password=goome-tech as default \n \
                %(binpath)s -d -c 'ifconfig' -i $iplist    #same as befault, also print out debug info \n \
                %(binpath)s  -l $port -c 'rpm -qa' -i 183.60.142.137 \n \
        note:  when not set defalut flag, each line of iplist  must contain 4 fields, that (ip user password port)\n \
                192.168.1.74   root  passwdxxxx  22\n \
        " % config

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

def handle_stdo_list(stdo):
        idx=0
        result = []
        for so in stdo:
                #if re.search(cmdstr,str.strip(so)):
                if so.strip().endswith(cmdstr):
                        #print "find cmdstr here!index=",idx
                        break
                idx = idx + 1
        tmp_res = stdo[(idx-1):]
        for so in tmp_res:
                if not re.search(pattern, str.strip(so)):
                        result.append(so)
        return result
        
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
                                print "\n".join(handle_stdo_list(stdo))
                else:
                        ot.info("deploy src:%s to dest:%s failure!\n"  % (src, dest))
                        if show == True:
                                for so in stdo:
                                        ot.error(so)
                                for eo in stde:
                                        ot.error(eo)
                return res
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
                        print "\n".join(handle_stdo_list(stdo))
                                
                else:
                        for so in stdo:
                                ot.error(so)
                        for eo in stde:
                                ot.error(eo)
                print ""
                return res
        except Exception,data:
                common.print_traceback_detail()
        
def main():
        """
        远程执行
        """
        try:
                import signal
        	import getopt
                signal.signal(signal.SIGINT, signal_handler)
                try:
                        options,args = getopt.getopt(sys.argv[1:],"h:c:g:i:t:dmy", ["host=", "config=", "group=", "id=", "timeout=", "debug", "man", "yes"])
                except getopt.GetoptError:
                        common.print_traceback_detail()
                        sys.exit()
                
                #命令行参数数据存储
                default_deploy_path = bin_path+"/../etc/deploy.cfg"
                default_hosts_path = bin_path+"/../etc/hosts"
                (hosts, config, group, id, timeout, debug, man, yesflag ) = (default_hosts_path, default_deploy_path, False, False, 120, False, False, False)
        
                
                for name,value in options:
                        if name in ("-h","--hosts"):
                                hosts = value
                        if name in ("-c","--config"):
                                config = value
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
        
                if group == False and id ==False:
                        if not yesflag:
                                ot.warn("not assign group or id, this tool will affect all host!")
                                answer = raw_input("Are you sure?[yes|no]:")
                                answer = str.lower(answer)
                                if answer not in ("yes", "y"):
                                        exit()
        
                cfghelper.parse_host(hosts)
                hosts = cfghelper.get_hosts(group,id)
                
                
                if not hosts:
                        ot.info("no any host match!")

                fd = open(config, "r")
                config_contents = fd.readlines()
                fd.close()
        
                ip = None
                rgt_ip_count = 0  #总有效IP数
                ip_total = 0  #总IP数，排除空行、注释行
                
                wrong_ip_conf = []   #错误的IP配置
                wrong_config_conf = []  #错误的文件传输、命令执行配置

                cmd_result = dict()
                         
                for srv_host in hosts:
                        infostr = "".join(["="] * 30)
			ip = srv_host["ip"]
			port = srv_host["port"]
                        setting = { "padding": infostr, "ip": ip, "port": port }
                        ot.info("%(padding)s %(ip)s PORT:%(port)s %(padding)s"  % setting)
                                                        
                        for config_line in config_contents:
                                config_line = str.strip(config_line)
                                if  re.search("^$|^#", config_line):
                                        continue
                                
                                config_arg = re.split(":::", config_line)
                                if not config_arg:
                                        wrong_config_conf.append(config_line)
                                        continue
                                
                                type_flag = config_arg[0]
                                if type_flag not in ("file", "cmd") or len(config_arg) < 1 :
                                        wrong_config_conf.append(config_line)
                                        continue

                                #如果是命令
                                if type_flag == "cmd" and len(config_arg) > 1:
                                        cmdstr = config_arg[1]
                                	pattern = get_pattern("%s$" % (cmdstr))
                                        do_action(srv_host, cmdstr=cmdstr, pattern=pattern, timeout=timeout, debug=debug, raw=True)
                                #如果是文件传输
                                if type_flag == "file":
                                        less_config_str = str.strip(config_arg[1])
                                        less_config_ary = re.split("[ |\t]+", less_config_str)
                                        
                                        if len(less_config_ary) < 3:
                                                wrong_config_conf.append(config_line)
                                                continue
                                        
                                        src_file = less_config_ary[0]
                                        dest_dir = less_config_ary[1]
                                        direction = less_config_ary[2]
                                        
                                        if direction not in ("push", "pull"):
                                                wrong_config_conf.append(config_line)
                                                continue
                                	pattern = get_pattern("")
                                        deploy(srv_host, src_file, dest_dir, direction=direction, pattern=pattern, timeout=timeout, debug=debug, raw=True, show=False)
    
                                        print "\n"
                
                #print aps execute logs
#                 now = mydate.get_datetime_str()
#                 filename = "remote_exe_" + now
#                 fd = open(filename, "w")
#                 for ip_port in cmd_result:
#                         data = cmd_result[ip_port]
#                         fd.write("--------- %s ---------- "  % (ip_port) + "\n")
#                         for element in data:
#                                 cmdstr = element["cmd"]
#                                 result = element["result"]
#                                 errors =  element["error"]
#                                 retcode = element["retcode"]
#                                 if result:
#                                         fd.write("[ std out ] " + "\n")
#                                         fd.write("command : " + cmdstr +  "\n")
#                                         for line in result:
#                                                 fd.write(line.strip() + "\n")
#                                         fd.write("\n")
#                                 if errors:
#                                         fd.write("[ std error ] " + "\n")
#                                         fd.write("command : " + cmdstr +  "\n")
#                                         for line in errors:
#                                                 fd.write(line.strip() + "\n")
#                         fd.write("\n\n")
#                 fd.close()
                
#                 print "all command result save in %s" % (filename)
#                 print "maybe you want to do as follow:"
                
#                 print "vi %s" % (filename)
#                 print "cat %s" % (filename)
#                 ot.info("vi %s" % (filename))
#                 ot.info("cat %s" % (filename))
                if  wrong_ip_conf:
                        print "====== wrong ip config:"
                        print wrong_ip_conf
                if wrong_config_conf:
                        print "====== wrong config line:"
                        print wrong_config_conf
        except Exception,data:
                common.print_traceback_detail()
                print data
                
                        

main()
# test_business()





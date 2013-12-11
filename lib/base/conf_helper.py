#-*- encoding:utf-8 -*-
'''
Created on 2013-11-23
@author: albert
'''
import re

hosts_cfg_dict = {}

def parse_host(conf_path):
        """
        [GROUP_1]
        id=first  ip=113.105.152.146   user=goocar  passwd=IfOvPq9PulH4vhP9   port=10683
        id=second  ip=113.12.82.249   user=goocar  passwd=cnLJPkED0qmoqJzz   port=10683
        
        [GROUP_2]
        id=first  ip=113.105.152.146   user=goocar  passwd=IfOvPq9PulH4vhP9   port=10683
        id=second  ip=113.12.82.249   user=goocar  passwd=cnLJPkED0qmoqJzz   port=10683
        """
        if not hosts_cfg_dict:
                fh = open(conf_path, "r")
                contents = fh.readlines()
                fh.close()
                section_start = 0
                section_end = 0
                section_id = ""
                for line in contents:
                        line = line.strip()
                        
                        if re.match("^$" , line ) or re.match("^#", line):
                                continue
                        
                        if line.startswith("[" ) and line.endswith("]"):
                                section_start = 1
                                section_end = 1
                                section_id = line.replace("[", "")
                                section_id = section_id.replace("]", "")
                                hosts_cfg_dict[section_id] = list()
                        else:
                                section_end = 0
                                
                        if section_start == 1 and section_end == 0:
#                                 tmp_list = re.split("=", line)
#                                 key = str.strip(tmp_list[0])
#                                 val = str.strip(tmp_list[1])
#                                 conf[section_id][key] = val
                                splitter = "[ |\t]+"
                                conf_item= re.split(splitter , line)
                                obj = {}
                                for conf in conf_item:
                                        conf_ary= re.split("[=|:]" , conf)
                                        if len(conf_ary) == 2:
                                                key = str.strip(conf_ary[0])
                                                val = str.strip(conf_ary[1])
                                                obj[key]=val
                                hosts_cfg_dict[section_id].append(obj)
        return hosts_cfg_dict

def get_group_list():
        return hosts_cfg_dict.keys()

def get_host_list():
        host_list = []
        for (gp,hostlist) in hosts_cfg_dict.items():
                for host in hostlist:
                        host["group"]=gp
                        host_list.append(host)
        return host_list

def get_hosts(gp_pattern="", id_pattern=""):
        hosts = list()
        if not gp_pattern and not id_pattern:  #all
                hosts = get_host_list()
        
        if gp_pattern and id_pattern: #group and id
                all_host = get_host_list()
                for host in all_host:
                        group = host["group"]
                        id = host["id"]
                        if  re.search(gp_pattern, group) and re.search(id_pattern, id)  :
                                hosts.append(host)
                                
        if gp_pattern and not id_pattern: #group
                all_host = get_host_list()
                for host in all_host:
                        group = host["group"]
                        if  re.search(gp_pattern, group):
                                hosts.append(host)
                                
        if not gp_pattern and id_pattern: #id
                all_host = get_host_list()
                for host in all_host:
                        id = host["id"]
                        if  re.search(id_pattern, id)  :
                                hosts.append(host)
                                
        return hosts
        
        


# ============= parse deploy.cfg ===================

deploy_cfg_dict = {}
def parse_deploy_cfg(conf_path):
        """
                src=../scripts/business1
                dest=/tmp/deploy
        """
        if not deploy_cfg_dict:
                fh = open(conf_path, "r")
                contents = fh.readlines()
                fh.close()

                for line in contents:
                        line = line.strip()
                        if re.match("^$" , line ) or re.match("^#", line):
                                continue
                        conf_ary= re.split("[=|:]" , line)
                        if len(conf_ary) >= 2:
                                deploy_cfg_dict[conf_ary[0]] = conf_ary[1]
                        
        return deploy_cfg_dict

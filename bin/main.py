# -*- encoding=utf8 -*-
import sys, os, signal
# 获取脚本文件的当前路径

def get_realpath():
        return os.path.split(os.path.realpath(__file__))[0]

def cur_file_dir():
        # 获取脚本路径
        path = sys.path[0]
        # 判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
        if os.path.isdir(path):
                return path
        elif os.path.isfile(path):
                return os.path.dirname(path)

bin_path = get_realpath()
sys.path.append(bin_path + "/../")


from base import common
from base import log
from base import mydate
from parsematrix import apply_vmres
from parsematrix import opt_vmres
 

import time

     
def get_nowtime():
        return mydate().get_nowtime()

def utcreate_vmascii(utf8_str):
        res = utf8_str.encode("ascii")
        return res

def obj2dict(obj):
        pr = {}
        for (k, v) in obj.items():
                pr[k] = v
        return pr


def submit_apply():
        cwd = get_realpath()
        lgpath = "%s/%s" % (cwd,'../logs/matrix')
        lg = log(lgpath)
        aly_res = apply_vmres(lg)
        while True:
                aly_res.do_instance_create()
                time.sleep(1)
                
def create_vm():
        cwd = get_realpath()
        lgpath = "%s/%s" % (cwd,'../logs/matrix')
        lg = log(lgpath)
        aly_res = apply_vmres(lg)
        while True:
                aly_res.do_query_create_status()   #这个动作比较耗时
                time.sleep(2)
                
def exe_apply():
        cwd = get_realpath()
        lgpath = "%s/%s" % (cwd,'../logs/matrix')
        lg = log(lgpath)
        aly_res = apply_vmres(lg)
        while True:
                aly_res.do_apply()
                time.sleep(1)

def vm_opt():
        cwd = get_realpath()
        lgpath = "%s/%s" % (cwd,'../logs/matrix')
        lg = log(lgpath)
        opt_vm = opt_vmres(lg)
        while True:
                opt_vm.do_vm_instance_opt()
                time.sleep(1)

def vm_opt_query():
        cwd = get_realpath()
        lgpath = "%s/%s" % (cwd,'../logs/matrix')
        lg = log(lgpath)
        opt_vm = opt_vmres(lg)
        while True:
                opt_vm.do_vm_instance_opt_status_query()
                time.sleep(1)


def vm_opt_total():
        '''
        提交vm操作请求以及vm操作结果查询
        '''
        cwd = get_realpath()
        lgpath = "%s/%s" % (cwd,'../logs/matrix')
        lg = log(lgpath)
        opt_vm = opt_vmres(lg)
        while True:
                opt_vm.do_vm_instance_opt()
                opt_vm.do_vm_instance_opt_status_query()
                time.sleep(1)

def main2():
        cwd = get_realpath()
        lgpath = "%s/%s" % (cwd,'../logs/matrix')
        lg = log(lgpath)
        aly_res = apply_vmres(lg)
        while True:
                aly_res.do_instance_create()
#                 time.sleep(1)
                aly_res.do_query_create_status()
#                 time.sleep(1)
                aly_res.do_apply()
                time.sleep(1)

def signal_handler(signal, frame):
        pid = os.getpid();
        print ""
        print "kill these pids: ",pid
        os.system("kill -9 %d" % pid)
        sys.exit(0)
        
#method 1  为每个任务创建一个进程，单独执行
def main():
        
        signal.signal(signal.SIGINT, signal_handler)
        
        choice = 1
        try:
                print "1. run all"
                print "2. run submit_apply"
                print "3. create_vm"
                print "4. exe_apply"
                print "5. vm_opt_total"
                #choice = int(raw_input("please input your choice[1-5]:"))
                choice = 1
        except Exception,dt:
                print dt
                return
        
        if choice == 2:
                submit_apply()
        elif choice == 3:
                create_vm()
        elif choice == 4:
                exe_apply()
        elif choice == 5:
                vm_opt_total()
        else:
                from multiprocessing import Process
                
                p1 = Process(target=submit_apply,args=())
                p2 = Process(target=create_vm,args=())
                p3 = Process(target=exe_apply,args=())
                p4 = Process(target=vm_opt_total,args=())
                p5 = Process(target=vm_opt_query,args=())
                
                pro_list = [p1,p2,p3,p4]
                
                for pro in pro_list:
                        pro.start();
                
                for pro in pro_list:
                        pro.join();

        
#method3   这种方法貌似可以，但是在插入数据的时候会出错，原因可能是高并发
#OK的，但不建议采用此方法，相当于串行了
def main3():
        from multiprocessing import Process
        p1 = Process(target=main,args=())
        p1.start()
        p1.join()
        print "Sub-process(es) done."
        
#method 4  使用线程池，阻塞版本        
def main4():
        import multiprocessing
        pool = multiprocessing.Pool(processes=4)
        pool.apply(submit_apply, ( ))
        pool.apply(create_vm, ( ))
        pool.apply(exe_apply, ( ))
        pool.close()
        pool.join()
        
#method 5 使用线程池，非阻塞版本，OK的
def main5():
        import multiprocessing
        result = []
        pool = multiprocessing.Pool(processes=4)
        result.append(pool.apply_async(submit_apply, ( )))
        result.append(pool.apply_async(create_vm, ( )))
        result.append(pool.apply_async(exe_apply, ( )))
        result.append(pool.apply_async(vm_opt, ( )))
        result.append(pool.apply_async(vm_opt_query, ( )))
        pool.close()
        pool.join()
        for res in result:
                print res.get()

        print "Sub-process(es) done."
        
def get_db_data():
        from parsematrix import dbhelper
        db = dbhelper();
        ds1 = db.get_instance_opt_request_order(0, 10)
        print ds1

##
##经过大量测试发现，之所以数据不能同步更新到DB中，是因为采用了DB线程池的方式
##在Connection2的reconnetc函数中设定
##取消后测试通过
##
# main2()
main()
# submit_apply()
# main3()
# main4()
# main5()

# vm_opt()
# vm_opt_query()
# get_db_data()




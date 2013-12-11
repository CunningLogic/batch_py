#-*- encoding:utf-8 -*-
'''
Created on 2013-3-28

@author: albertqiu
'''

'''
格式：\033[显示方式;前景色;背景色m
 
说明：
前景色            背景色           颜色
---------------------------------------
30                40              黑色
31                41              红色
32                42              绿色
33                43              黃色
34                44              蓝色
35                45              紫红色
36                46              青蓝色
37                47              白色
显示方式           意义
-------------------------
0                终端默认设置
1                高亮显示
4                使用下划线
5                闪烁
7                反白显示
8                不可见
 
例子：
\033[1;31;40m    <!--1-高亮显示 31-前景色红色  40-背景色黑色-->
\033[0m          <!--采用终端默认设置，即取消颜色设置-->
'''

def error(error_str):
        '''
        前景色：红色 背景色：黑色
        '''
        print "\033[1;31;40m%s\033[0m" % (error_str)
        
def info(info_str):
        '''
        前景色：绿色 背景色：黑色
        '''
        print "\033[1;32;40m%s\033[0m" % (info_str)
        
def emphasize(emphasize_str):
        """
        same as error
        """
        error(emphasize_str)
        
def warn(info_str):
        '''
        前景色：绿色 背景色：黑色
        '''
        print "\033[1;36;40m%s\033[0m" % (info_str)

if __name__ == "__main__":
        error("what")
        info("what")
        
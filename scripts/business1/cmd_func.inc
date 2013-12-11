####################
# author: albert
# date: 2013-11-22
# version: 1.0
####################

pidfile="./pids"
spt_name="target.sh"
chk_spt_name="daemon.sh"


function info () 
{
	echo -e "\033[032m$*\033[m"
}

function ok () 
{
	echo -e "\033[032m$*\033[m"
}

function warn () 
{
	echo -e "\033[033m$*\033[m"
}

function error () 
{
	echo -e "\033[031m$*\033[m"
}


function run_script () 
{
	local script_path=$1
	$script_path > /dev/null 2>&1 &
	if [ $? -eq 0 ];then
		info "run $script_path ok"
	else
		error "run $script_path failure!"
	fi
}

function stop_script()
{
	local spt_name=$1
	local pattern="$spt_name$"
	if [ "x$pattern" != "x$" ];then
		pids=$(ps -ef | grep -E "$pattern" | grep -v grep | awk '{print $2}')
		for pid in $pids;do
			$(kill -9 $pid >/dev/null 2>&1)
			if [ $? -eq 0 ]; then
				info "stop $spt_name ok"
			else
				error "stop $spt_name failure"
			fi
		done
		#$(ps -ef|grep "$pattern" | grep -v grep | awk '{print $2}'|xargs kill -9)
	fi
}

function check_status()
{
	local spt_name=$1
	local pattern="$spt_name$"
	lines=`ps -ef | grep -E "$pattern" | grep -v grep`
    info $lines
}

function check_ps
{
	local spt_name=$1
	local pattern="$spt_name$"
	local res=$(ps -ef | grep -E "$pattern" | grep -v grep | wc -l)
	if [ $res -gt 0 ];then
		#echo 'no more than one instance,exit'
		#exit
		return 0
	fi
	return 1  #not exist
}

function check_exit
{
	local spt_name=$1
	local pattern="$spt_name$"
	local res=$(ps -ef | grep -E "$pattern" | grep -v grep | wc -l)
	if [ $res -gt 2 ];then
		#echo 'no more than one instance,exit'
		exit
	fi
}

function check_pid
{
	local dt="[`date +'%F %T'`]"
	local pid=$1
	local script_name=$2
	$(ps -p $pid -fww  >/dev/null 2>&1)
	if [ $? -eq 0 ];then
	        ok $dt check pid:$pid script:$script_name process ok
	else 
	        error $dt check pid:$pid script:$script_name not found, auto run script:$script_name !
	        run_script ./$script_name > /dev/null 2>&1 &
	fi
}

function check_pid_script
{
	local pid=$1
	local script_name=$2
	local dt="[`date +'%F %T'`]"
	local psinfo=$(ps -p $pid -fww  2>/dev/null)
	local is_pid_ok=$?
	local ct=$(echo $psinfo | grep "$script_name$" | wc -l)
	if [ $is_pid_ok -eq 0 ] && [ $ct -gt 0 ]; then
			ok is_pid_ok: $is_pid_ok ct: $ct
	        ok $dt check pid:$pid script:$script_name process ok
	else 
			error is_pid_ok: $is_pid_ok ct: $ct
	        error $dt check pid:$pid script:$script_name not found, auto run script:$script_name !
	        run_script ./$script_name
	fi
}

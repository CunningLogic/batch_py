#! /bin/sh

inc_script="./cmd_func.inc"
source $inc_script


function start
{
	local spt_name=$1
	local chk_spt_name=$2

	$(check_ps $spt_name)
	
	if [ $? -ne 0 ];then
		run_script ./$spt_name
	else
		info $spt_name exist!
	fi

	$(check_ps $chk_spt_name)
	if [ $? -ne 0 ];then
		run_script ./$chk_spt_name
	else
		info $chk_spt_name exist!
	fi
}

function stop
{
	local spt_name=$1
	local chk_spt_name=$2

	$(check_ps $spt_name)
	if [ $? -eq 0 ];then
		stop_script $spt_name
	else
		info $spt_name not exist, do nothing!
	fi
	
	$(check_ps $chk_spt_name)
	if [ $? -eq 0 ];then
		stop_script $chk_spt_name
	else
		info $chk_spt_name not exist, do nothing!
	fi
}

function restart
{
	local spt_name=$1
	local chk_spt_name=$2

	stop $spt_name $chk_spt_name
	start $spt_name $chk_spt_name
}

function status
{
	local spt_name=$1
	local chk_spt_name=$2
	check_status $spt_name
	check_status $chk_spt_name
}

function help
{
	help_tmp_file="/tmp/helpinfo"
	self=$1
	cat > $help_tmp_file  <<EOF
$self [options]
options like as follow:
	start		start target&daemon
	stop		stop target&daemon
	restart		restart target&daemon
	status		output target&daemon status
EOF
	cat $help_tmp_file
}

ARGV="$@"


if [ "x$ARGV" = "x" ] ; then 
    ARGV="-h"
fi

ARGV=`echo $ARGV | tr 'A-Z' 'a-z'`

case $ARGV in
	start)
		start $spt_name $chk_spt_name
	    ;;
	stop)
		stop $spt_name $chk_spt_name
	    ;;
	restart)
		restart $spt_name $chk_spt_name
	    ;;
	status)
		status $spt_name $chk_spt_name
	    ;;
	-h|h)
		help $0
		;;
	*)
		help $0
esac


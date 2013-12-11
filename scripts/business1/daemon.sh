#! /bin/sh

inc_script="./cmd_func.inc"
source $inc_script



function main
{
	check_exit $chk_spt_name

	while true;do
			cd `dirname $0`
			while read pid script_name;
			do
				#check_pid $pid $script_name
				check_pid_script $pid $script_name
			done < $pidfile
		sleep 1
	done
}

main



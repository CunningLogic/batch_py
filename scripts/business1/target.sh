#! /bin/sh

inc_script="./cmd_func.inc"
source $inc_script


function main
{
	pid=$$
	
	check_exit $spt_name

	echo "$pid  $spt_name" > $pidfile
	
	COUNTER=1
	while true; do
		  echo $COUNTER
		  COUNTER=$(($COUNTER+1))
		  sleep 1
	done
}

main






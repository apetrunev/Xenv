#!/bin/sh

#
# Start script for Xvfb
#

case $1 in
stop)
	pid=$(ps axo pid,user,cmd | grep -E "[X]vfb" | awk '{ print $1 }')
	kill $pid 2>/dev/null
	exit 0
	;;
start)
	pid=$(ps axo pid,user,cmd | grep -E "[X]vfb" | awk '{ print $1 }')
	if [ x"$pid" != x"" ]; then 
		echo "Xvfb already running..."
		exit 1
	fi	
	# create screen
	( exec 2>&1 >/dev/null Xvfb -screen 0 1280x720x24+32 -ac & ) 2>&1 1>/dev/null
	# wait for sceen is available
	while :; do
		( exec 2>&1 >/dev/null xdpyinfo -display :0 ) 2>&1 1>/dev/null
		if [ $? -eq 0 ]; then
			break
		fi
	done
	# screen is available now
	exit 0
	;;
*)
	echo "usage: ./xvfb.sh start|stop"
	exit 1
	;;
esac	

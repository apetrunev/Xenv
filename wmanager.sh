#!/bin/sh

wmanager=$(which jwm)

case $1 in
start)
	pid=$(ps axo pid,user,cmd | grep -v grep | grep $wmanager)
	if [ x"$pid" != x"" ]; then 
		echo "$wmanager already running..."
		exit 1
	fi
	($wmanager) 2>&1 1>/dev/null &
	exit 0
	;;
stop)
	pid=$(ps axo pid,user,cmd | grep -v grep | grep $wmanager)
	kill $pid  2>/dev/null
	exit 0
	;;
*)
	echo "usage: $wmanager start|stop ..."
	exit 1
	;;
esac

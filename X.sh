#!/bin/sh 

PATH="$PATH:$(pwd)"

xvfb=$(which xvfb.sh)
wmanager=$(which wmanager.sh)

case $1 in
start)
	$xvfb start
	$wmanager start 
	exit 0
	;;
stop)
	$xvfb stop
	$wmanager stop
	exit 0
	;;
*)
	exit 1
	;;
esac

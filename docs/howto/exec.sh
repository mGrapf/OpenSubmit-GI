#!/bin/bash
PATH_RESULT="__Fertig"

#set -x

if [ ! "$1" ]; then
	echo "Bitte Ordnernamen als Parameter mitgeben:"
	for D in *; do
		if [ -d "$D" ] && [ "$D" != "$PATH_RESULT" ]; then
			echo -e "\t$D"
		fi
	done	
	exit 0
fi

if [ ! -d "$1" ]; then
	echo "Diese Aufgabe existiert nicht"
	exit -1
fi

if [ ! -e "$1/validator_example.cpp" ]; then
	echo "$1/validator_example.cpp fehlt"
	exit -1
fi
	


logfile="./opensubmit-exec.log"
opensubmit-exec test "$1" |& tee $logfile
if grep -q "('ErrorCode', [^0]*)" $logfile ; then
	exit 1
fi
exit 0

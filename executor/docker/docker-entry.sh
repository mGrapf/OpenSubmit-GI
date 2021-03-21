#!/bin/bash
set -e
CONFIG_FILE=/etc/opensubmit/executor.ini

if [ ! -f $CONFIG_FILE ]; then
	OPTIONS=""

	# pip3 install --upgrade <url>
	if [ $OPENSUBMIT_UPGRADE ]; then
		printf "pip3 install --upgrade $OPENSUBMIT_UPGRADE\n"
		pip3 install --no-cache-dir --upgrade $OPENSUBMIT_UPGRADE || exit
	fi
	HELP_TEXT=$(opensubmit-exec help)
	
	# OPENSUBMIT_SERVER_URL
	if [ ! $OPENSUBMIT_SERVER_URL ]; then
		OPENSUBMIT_SERVER_URL="http://localhost:8000"
	fi
	printf "Try to reach web server ... "
	until $(curl --output /dev/null --silent --head --fail $OPENSUBMIT_SERVER_URL); do
		echo '... still try ...'
		sleep 5
	done
	echo "OK"
	
	# -u user
	if [[ $HELP_TEXT == *"-u <user>"* ]];then
		OPTIONS="$OPTIONS -u opensubmit"
	fi
	# ID
	if [ $OPENSUBMIT_ID ] && [[ $HELP_TEXT == *"-i <id>"* ]]; then
		OPTIONS="$OPTIONS -i $OPENSUBMIT_ID"
	fi
	# SECRET
	if [ $OPENSUBMIT_SECRET ] && [[ $HELP_TEXT == *"-s <secret>"* ]]; then
		OPTIONS="$OPTIONS -s $OPENSUBMIT_SECRET"
	fi
	
	# Create Config
	echo "opensubmit-exec configcreate $OPENSUBMIT_SERVER_URL $OPTIONS"
	opensubmit-exec configcreate $OPENSUBMIT_SERVER_URL $OPTIONS
	
	# Test Config
	while ! opensubmit-exec configtest; do
		echo "The configuration appears to be incorrect."
		echo "Please adjust the configuration with:  \"docker exec -ti [CONTAINERNAME] nano $CONFIG_FILE\""
		TIME_A=$(stat -c %Y $CONFIG_FILE)
		TIME_B=$TIME_A
		until [ $TIME_A -ne $TIME_B ]; do
			TIME_B=$(stat -c %Y $CONFIG_FILE)
			sleep 1
		done
	done
fi
if [[ $HELP_TEXT == *"run_forever"* ]];then
	crontab -r
	echo "opensubmit-exec run_forever"
	opensubmit-exec run_forever
else
	echo "opensubmit-exec run"
	cron -f
fi



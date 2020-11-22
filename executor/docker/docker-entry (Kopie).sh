#!/bin/bash
set -e
CONFIG_FILE=/etc/opensubmit/executor.ini

if [ ! -f $CONFIG_FILE ]; then
	# create config
	if [ ! $OPENSUBMIT_SERVER_URL ]; then
		OPENSUBMIT_SERVER_URL=http://localhost
	fi
	opensubmit-exec configcreate $OPENSUBMIT_SERVER_URL
	ln -s $CONFIG_FILE /config
	
	# test config
	while ! opensubmit-exec configtest; do
		echo "The configuration appears to be incorrect."
		echo "Please adjust the configuration with:  \"docker exec -ti [CONTAINERNAME] nano config\""
		TIME_A=$(stat -c %Y $CONFIG_FILE)
		TIME_B=$TIME_A
		until [ $TIME_A -ne $TIME_B ]; do
			TIME_B=$(stat -c %Y $CONFIG_FILE)
			sleep 1
		done
	done
fi

opensubmit-exec run

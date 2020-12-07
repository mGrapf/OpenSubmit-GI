#!/bin/bash
set -e
CONFIG_FILE=/config.ini

# ENV OPENSUBMIT_SERVER_URL
# ENV OPENSUBMIT_SERVER_UUID
# ENV OPENSUBMIT_SERVER_SECRET

if [ ! -f $CONFIG_FILE ]; then
	# update opensubmit-exec
	pip3 install --upgrade git+https://github.com/mGrapf/opensubmit-gi#egg=opensubmit-exec\&subdirectory=executor
	# create config
	if [ ! $OPENSUBMIT_SERVER_URL ]; then
		OPENSUBMIT_SERVER_URL="http://localhost -u opensubmit"
	fi
	OPTIONS="-c $CONFIG_FILE"
	if [ $OPENSUBMIT_SERVER_UUID ]; then
		OPTIONS="$OPTIONS -i $OPENSUBMIT_SERVER_UUID"
		OPENSUBMIT_SERVER_SECRET=""
	fi
	if [ $OPENSUBMIT_SERVER_SECRET ]; then
		OPTION="$OPTIONS -s $OPENSUBMIT_SERVER_SECRET"
		OPENSUBMIT_SERVER_SECRET=""
	fi
	
	opensubmit-exec configcreate $OPENSUBMIT_SERVER_URL $OPENSUBMIT_SERVER_URL $OPTIONS
		
	#ln -s $CONFIG_FILE /config
	
	# test config
	while ! opensubmit-exec configtest -c $CONFIG_FILE; do
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

opensubmit-exec run_forever -c $CONFIG_FILE

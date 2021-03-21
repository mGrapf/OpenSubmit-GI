#!/bin/bash

SERVER_URL=http://localhost
ID=1
SECRET="49846zut93purfh977TTTiuhgalkjfnk89"
UPGRADE=git+https://github.com/mGrapf/opensubmit-gi#egg=opensubmit-exec\&subdirectory=executor


docker run -d \
	--name opensubmit-exec \
	--restart=unless-stopped \
    -e OPENSUBMIT_SERVER_URL=$SERVER_URL \
    -e OPENSUBMIT_ID=$ID \
    -e OPENSUBMIT_SECRET=$SECRET \
    -e OPENSUBMIT_UPGRADE=$UPGRADE \
    mgrapf/opensubmit-exec:latest

echo "Please check: \"docker logs opensubmit-exec|'"

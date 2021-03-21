#!/bin/bash

SERVER_URL=http://pi4/
ID=1
SECRET="49846zut93purfh977TTTiuhgalkjfnk89"
UPGRADE=git+https://github.com/troeger/opensubmit#egg=opensubmit-exec\&subdirectory=executor


docker run -d \
	--name opensubmit-exec \
	--rm \
    -e OPENSUBMIT_SERVER_URL=$SERVER_URL \
    -e OPENSUBMIT_ID=$ID \
    -e OPENSUBMIT_SECRET=$SECRET \
    -e OPENSUBMIT_UPGRADE=$UPGRADE \
    mgrapf/opensubmit-exec:latest

docker logs --follow opensubmit-exec

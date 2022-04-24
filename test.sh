#!/bin/bash

API_HOSTNAME=https://2utbomhdmi.execute-api.us-east-1.amazonaws.com/dev

TODOS_ENDPOINT=todos
USER_ENDPOINT=user

CREATE_USER_REQUEST='{"username": "shawn"}'
CREATE_TODO_REQUEST='{"body": "foo"}'

curl -i -X POST ${API_HOSTNAME}/${USER_ENDPOINT} -d "${CREATE_USER_REQUEST}"

resp=`curl -X POST ${API_HOSTNAME}/${USER_ENDPOINT}/shawn/${TODOS_ENDPOINT} -d "${CREATE_TODO_REQUEST}"`
echo $resp
todoId=`echo "$resp" | jq '.todoId' | sed -e 's/"//g'`

curl -i ${API_HOSTNAME}/${USER_ENDPOINT}/shawn/${TODOS_ENDPOINT}

curl -i ${API_HOSTNAME}/${USER_ENDPOINT}/shawn/${TODOS_ENDPOINT}/${todoId}

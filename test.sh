#!/bin/bash

API_HOSTNAME=https://2utbomhdmi.execute-api.us-east-1.amazonaws.com/dev

TODOS_ENDPOINT=todos
USER_ENDPOINT=user

CREATE_USER_REQUEST='{"username": "shawn"}'
CREATE_TODO_REQUEST='{"body": "foo"}'
UPDATE_TODO_REQUEST='{"body": "foobar", "completed": true}'

set -x
# test user create
curl -i -X POST ${API_HOSTNAME}/${USER_ENDPOINT} -d "${CREATE_USER_REQUEST}"

# test todo create
resp=`curl -X POST ${API_HOSTNAME}/${USER_ENDPOINT}/shawn/${TODOS_ENDPOINT} -d "${CREATE_TODO_REQUEST}"`
echo $resp
todoId=`echo "$resp" | jq '.todoId' | sed -e 's/"//g'`

# test todo get-all
curl -i ${API_HOSTNAME}/${USER_ENDPOINT}/shawn/${TODOS_ENDPOINT}

# test todo get-one
curl -i ${API_HOSTNAME}/${USER_ENDPOINT}/shawn/${TODOS_ENDPOINT}/${todoId}

# # test todo delete-one
# curl -i -X DELETE ${API_HOSTNAME}/${USER_ENDPOINT}/shawn/${TODOS_ENDPOINT}/${todoId}
# curl -i ${API_HOSTNAME}/${USER_ENDPOINT}/shawn/${TODOS_ENDPOINT}/${todoId}

# test todo update-one
curl -i -X PUT ${API_HOSTNAME}/${USER_ENDPOINT}/shawn/${TODOS_ENDPOINT}/${todoId} -d "${UPDATE_TODO_REQUEST}"
curl -i ${API_HOSTNAME}/${USER_ENDPOINT}/shawn/${TODOS_ENDPOINT}/${todoId}
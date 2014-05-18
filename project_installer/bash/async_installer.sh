#!/bin/bash

VHOST=$1
USER=$2
PW=$3

echo "Creating rabbitmq vhost ${VHOST} for ${USER} and ${PW}"

rabbitmqctl add_vhost ${VHOST} \
   && rabbitmqctl add_user ${USER} ${PW} \
   && rabbitmqctl set_permissions -p ${VHOST} ${USER} ".*" ".*" ".*"


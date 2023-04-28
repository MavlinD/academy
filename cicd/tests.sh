#!/bin/bash
set -euo pipefail

# docker network ls
# docker network inspect bridge
# docker network inspect host
# docker network inspect none
# docker network inspect localnet

{

    echo FIRST_USER_EMAIL=root@loc.loc
    echo FIRST_USER_USERNAME=root
    echo FIRST_USER_PASSWORD=Pass!123

    # указанный ниже пользователь исп-ся в тестах
    echo TEST_USER_EMAIL=test@loc.loc
    echo TEST_USER_USERNAME=test_username
    echo TEST_USER_PASSWORD='Pass&123'
    echo TEST_USER_FIRST_NAME=Семён
    echo SALT='a*w0z%9p&!b=9(!y(u&hf1uuf_blkx%)400!k%mekc&asi@v&'
    echo TOKEN_ISS=auth
    echo TOKEN_AUDIENCE=auth
    echo MAIL_CONSOLE=1
    # не отправлять письма на подтверждение почты и именение пароля
    echo SUPPRESS_SEND=1

    echo POSTGRES_HOSTNAME=$POSTGRES_PORT_5432_TCP_ADDR
    echo PG_PORT=5432
    echo DB_NAME=$POSTGRES_DB
    echo DB_TPL=${POSTGRES_DB}_test
    echo POSTGRES_USER=$POSTGRES_USER
    echo POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"

    echo API_PORT_INTERNAL=8000
    echo PRIVATE_KEY=priv-key.pem
    echo PUBLIC_KEY=pub-key.pem

    echo TESTING=1
    echo DBS_ENGINE=postgres
    echo DB_NAME=auth
    echo DB_TPL=auth

} > .env
# cat .env
# env

docker login -u gitlab-ci-token -p $CI_JOB_TOKEN $CI_REGISTRY

docker run --rm -i --env-file .env --network bridge $CI_REGISTRY_IMAGE/api bash cicd-run-tests.sh

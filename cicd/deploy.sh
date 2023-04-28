#!/bin/bash

set -euo pipefail
# ls -al
# echo $CI_ENVIRONMENT_NAME
# exit
if [[ $CI_ENVIRONMENT_NAME == 'production' ]]
then
	DEPLOY_DIR_LOCAL=${DEPLOY_DIR}/auth-v2

fi

{
    echo NET_NAME=mb-v2
    echo SUFFIX=-v2
    echo API_PORT_INTERNAL=8000
    echo LOG_LEVEL=20
    echo WEB_CONCURRENCY=8
    echo SENTRY_DSN=https://b82f8f1a9da94c2d9f2b3633c7f7e6d0@sentry.macrodom.ru/3
    echo SALT=$SALT

    echo TOKEN_ISS=auth
    echo TOKEN_AUDIENCE=auth
    echo PRIVATE_KEY=./../../../dbs/priv-key.pem
    echo PUBLIC_KEY=./../../../dbs/pub-key.pem

    # FastMail
    echo ROOT_URL=https://auth-v2.macrobank.pro/
    # адрес для верификации созданных УЗ
    echo VERIFICATION_URL="api/v2/user/accept-verify-token"
    # адрес для переустановки пароля
    echo PASSWORD_RESET_URL="docs#/User/reset_password_api_v2_user_reset_password_patch"
    # выводить токены в stdout, требуется для выполнения тестов
    echo MAIL_CONSOLE=1
    # не отправлять письма на подтверждение почты и именение пароля
    echo SUPPRESS_SEND=0

    echo MAIL_USERNAME=$MAIL_USERNAME
    echo MAIL_PASSWORD=$MAIL_PASSWORD
    echo MAIL_SERVER=$MAIL_SERVER
    echo MAIL_PORT=587
    echo MAIL_SENDER=$MAIL_SENDER

# ------------------- end api --------------------

    echo DBS_ENGINE=postgres
    # имя основной, главной БД, Postgres
    echo DB_NAME=$DB_NAME
    # имя сервера внутри докер сети
    echo POSTGRES_HOSTNAME=auth-db-v2
    echo POSTGRES_USER=$POSTGRES_USER
    echo POSTGRES_PASSWORD=$POSTGRES_PASSWORD
    echo PG_PORT=5432
    # закрываем сервис снаружи
    echo PG_PORT_EXTERNAL_DOCKER=127.0.0.1:5432

    # папка для всех БД
    echo DBS=dbs
    echo DB_TPL=""
    # папка для БД Postgres
    echo POSTGRES_DB_FOLDER=pg

    echo LC_ALL=C.UTF-8
    echo TERM=xterm-256color
#     echo IMAGE_DB=$CI_REGISTRY_IMAGE/db
#     echo IMAGE_API=$CI_REGISTRY_IMAGE/api
    echo IMAGE_DB=$CI_REGISTRY_IMAGE/db:$IMAGE_NUM
    echo IMAGE_API=$CI_REGISTRY_IMAGE/api:$IMAGE_NUM

} > .env

# список сервисов, должен быть актуален!
declare -a services=(api db)

for i in "${services[@]}"
do
	rsync $i/docker-compose.yml \
  	$USER_TO_DEPLOY@$HOST_TO_DEPLOY:$DEPLOY_DIR_LOCAL/$i/
done

rsync \
.env \
docker-compose.yml \
$USER_TO_DEPLOY@$HOST_TO_DEPLOY:$DEPLOY_DIR_LOCAL/

# echo $DEPLOY_DIR_LOCAL

source cicd/send-notice.sh

ssh $USER_TO_DEPLOY@$HOST_TO_DEPLOY "bash -s" < cicd/reload.sh $DEPLOY_DIR_LOCAL

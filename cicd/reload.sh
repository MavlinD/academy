#!/bin/bash
# перезапускает сервисы
set -eEu

cd $1
# echo $1
# env
# exit
docker compose pull --include-deps -q

# rm -rf node_modules && mkdir node_modules
echo $PWD

echo 'up!!!'
docker compose up --remove-orphans -d

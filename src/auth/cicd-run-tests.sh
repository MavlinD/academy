#!/bin/bash
set -euo pipefail

# этот сценарий нужен для ci/cd, он заменяет собой точку входа в образ api

ls -al

key_folder=src/auth/app/core

echo $PWD

openssl ecparam -name secp256k1 -genkey -noout -out $key_folder/priv-key.pem
openssl ec -in $key_folder/priv-key.pem -pubout > $key_folder/pub-key.pem

ls -al $key_folder

python src/auth/staff.py alembic upgrade head

# pytest -x
# только те тесты, что не помечены 'local'
pytest -x -m "not local"

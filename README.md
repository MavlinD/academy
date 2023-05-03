[![version-badge][version-badge]][main-branch-link] [![tests-status-badge][tests-status-badge]][main-branch-link]

[version-badge]: https://img.shields.io/badge/version-1.0.0-%230071C5?style=for-the-badge&logo=semver&logoColor=orange
[tests-status-badge]: https://img.shields.io/badge/test-passed-green?style=for-the-badge&logo=pytest&logoColor=orange
[main-branch-link]: https://gitlab.macrodom.ru/macrobank-3/auth-v2/-/commits/master

### Развертывание

```shell
# Клонируем репо
git clone 
cd academy
cp template.env .env
# Заполняем файл с переменными окружения
```
#### Настройка БД
```shell
# создаём папку для файлов БД имя папки указанной ниже
# формируется как $DBS/${POSTGRES_DB_FOLDER}${SUFFIX} 
mkdir dbs/pg-v2
# Запускаем сервер БД
docker compose up db

# собираем сервис
docker compose build api
# создаём БД и выполняем миграции
docker compose run api bash -c 'python3 staff.py alembic upgrade head'

# генерируем ключевую пару
docker compose run api sh generate-keys.sh

# запускаем АПИ
docker compose up api
# проверяем статус сервиса, например в браузере http://localhost:8000/docs
```
#### если [SQLite]: 
с версии 1.0.0 поддержка [SQLite] не гарантируется 
```shell
# собираем сервис
docker compose build api

# генерируем ключевую пару
docker compose run api sh generate-keys.sh

# создаём БД и выполняем миграции
docker compose run api bash -c 'python3 staff.py alembic upgrade head'

# запускаем АПИ
docker compose up api
# проверяем статус сервиса, например в браузере http://localhost:8000/docs
```



[смотри документацию](src/auth/wiki/docs/index.md)

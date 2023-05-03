[![version-badge][version-badge]][main-branch-link] [![tests-status-badge][tests-status-badge]][main-branch-link]

[version-badge]: https://img.shields.io/badge/version-1.0.0-%230071C5?style=for-the-badge&logo=semver&logoColor=orange
[tests-status-badge]: https://img.shields.io/badge/test-passed-green?style=for-the-badge&logo=pytest&logoColor=orange
[main-branch-link]: https://github.com/MavlinD/academy

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
```
#### Настройка АПИ
```shell
# генерируем ключевую пару, в докере
docker compose run api sh generate-keys.sh ./../../$DBS

# создаём первого суперпользователя, в докере:
docker compose run api bash -c 'python3 src/django_space/manage.py createsuperuser'

# генерируем ключевую пару, локально
sh generate-keys.sh dbs

# создаём первого суперпользователя, локально:
python3 src/django_space/manage.py createsuperuser

# собираем сервис
docker compose up api
# создаём БД и выполняем миграции
docker compose run api bash -c 'python3 src/django_space/manage.py makemigrations'
docker compose run api bash -c 'python3 src/django_space/manage.py migrate'

# запускаем АПИ
docker compose up api

# или локально, устанавливаем виртуальное окружение
poetry shell
# устанавливаем зависимости
poetry install
# запуск апи
python3 src/main.py
```
#### [проверяем статус сервиса, например в браузере](http://localhost:8000/api/docs)  
#### [вход в админку](http://localhost:8000/django/admin)

### Тестирование
```shell
pytest -x
# должно выполнится 25 тестов
```

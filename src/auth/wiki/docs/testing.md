### Тестирование
```shell
# установить TESTING=true
# Подготовить шаблон тестовой БД (в полученный шаблон автоматически добавляется суперюзер)
python3 src/auth/staff.py alembic upgrade head
# or
docker compose run api bash -c 'python3 src/auth/staff.py alembic upgrade head'
# можно запускать тесты
pytest -x
```
тестируются конечные точки и миграции БД
```shell
# мониторинг тестов, будет следить за изменениями в коде и перезапускать изменившиеся тесты
ptw -- 5 mon
```
где 5 - [уровень логирования](https://docs.python.org/3/library/logging.html#logging-levels) 

{% 
include 'links.md'
rewrite-relative-urls=false
%}

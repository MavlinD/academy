### Резервное копирование и восстановление БД

```bash
# выполняется команда внутри контейнера db
pg_restore -h localhost -p 5432 -U postgres -d old_db -v
pg_restore -h localhost -p 5432 -U auth-root -d auth -c /backups/auth-dev/dump_macrobank-auth-dev_2022-03-24@13_35_29.tar
# -c очистить бд перед восстановлением
psql -U $POSTGRES_USER -d $POSTGRES_DB 
psql -U auth-root -d auth 
# подключение к БД
```

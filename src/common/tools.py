from sqlalchemy_utils import create_database, database_exists


def create_dbs(db_uri: str | None) -> None:
    """создать БД если отсутствует"""
    # для SQLite БД создавать не нужно
    if db_uri is None:
        return
    sync_url = db_uri.replace("+asyncpg", "")
    if not database_exists(sync_url):
        create_database(sync_url)

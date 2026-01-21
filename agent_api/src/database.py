from contextlib import contextmanager

from src.db.factory import make_database

_database = None

def get_database():
    """Get the database instance, creating it if it doesn't exist."""
    global _database
    if _database is None:
        _database = make_database()
    return _database

@contextmanager
def get_db_session():
    """Context manager to get a database session."""
    database = get_database()
    with database.get_session() as session:
        yield session
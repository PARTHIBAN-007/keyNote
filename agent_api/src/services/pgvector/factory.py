from src.services.pgvector.pgvector import PostgresVectorClient
from src.database import get_db_session
def get_pgvector_client():
    session = get_db_session()
    return PostgresVectorClient(session=session)

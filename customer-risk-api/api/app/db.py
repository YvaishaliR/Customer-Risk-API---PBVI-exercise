import os

from psycopg2.pool import SimpleConnectionPool

_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=5,
    host=os.environ['POSTGRES_HOST'],
    port=int(os.environ.get('POSTGRES_PORT', 5432)),
    dbname=os.environ['POSTGRES_DB'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD'],
)


def get_conn():
    return _pool.getconn()


def release_conn(conn):
    _pool.putconn(conn)

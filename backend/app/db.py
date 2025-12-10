# app/db.py

import mysql.connector
from mysql.connector import pooling
from .config import DB_CONFIG

# Create a connection pool so we can reuse DB connections efficiently
connection_pool = pooling.MySQLConnectionPool(
    pool_name="air_nova_pool",
    pool_size=5,               # Max number of active connections
    **DB_CONFIG                # Unpack DB_CONFIG (host, user, password, database)
)

def get_connection():
    """
    Get a connection object from the pool.
    Every time we want to talk to MySQL,
    we will call this function instead of creating new connections manually.
    """
    return connection_pool.get_connection()

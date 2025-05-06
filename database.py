
import psycopg2 as db

def connect_db():
    conn = db.connect(
        dbname="sistema_serralheria",
        user="postgres",
        password="12341",
        host="localhost",
        port="5432"
    )
    return conn

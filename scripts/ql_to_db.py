import os
import dotenv
import psycopg2
import json
import uuid
from psycopg2.extensions import AsIs

dotenv.load_dotenv()

pg_string = psycopg2.extensions.make_dsn(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    dbname=os.getenv('DB_DATABASE'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

with psycopg2.connect(pg_string) as conn:
    with conn.cursor() as cur:
        table_sql = """
           create extension if not exists vector;

           drop table if exists qualifiers;

           create table qualifiers (
              id char(36) primary key,
              y char(8),
              n char(5),
              q varchar(2048),
              t varchar(255),
              e vector(1536),
              unique(y, n)
            )
            """
        cur.execute(table_sql)
        conn.commit()
        docs = json.loads(open('output/qualifiers_embedded.json', 'r').read())
        question_sql = "INSERT INTO qualifiers (id, y, n, q, t, e) VALUES (%s, %s, %s, %s, %s, %s);"

        for doc in docs:
            try:
                cur.execute(question_sql, (
                     str(uuid.uuid4()),
                     doc["y"],
                     doc["n"],
                     doc["q"],
                     doc["t"],
                     doc["e"],
                ))
                conn.commit()
            except Exception as e:
                print(f"{doc['y']}-{doc['n']}. {doc['q']}")
                print(e)
                exit(0)

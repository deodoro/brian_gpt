# Create database
import os
import dotenv
import psycopg
import json
from psycopg.conninfo import make_conninfo

dotenv.load_dotenv()

pg_string = make_conninfo(
  host=os.getenv('DB_HOST'),
  port=os.getenv('DB_PORT'),
  dbname=os.getenv('DB_DATABASE'),
  user=os.getenv('DB_USER'),
  password=os.getenv('DB_PASSWORD')
)

with psycopg.connect(pg_string) as conn:
    docs = json.loads(open('output/questions_embedded.json', 'r').read())
    sql = "INSERT INTO questions (enunciate, answer, explanation, combined, embedding_enunciate, embedding_answer, embedding_explanation, embedding_combined) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (enunciate) DO NOTHING;"

    for doc in docs:
        conn.execute(sql, (doc["enunciate"], doc["answer"], doc["explanation"], doc["combined"], doc["embedding_enunciate"], doc["embedding_answer"], doc["embedding_explanation"], doc["embedding_combined"]))
        conn.commit()

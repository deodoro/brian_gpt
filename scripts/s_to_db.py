# Create database
import os
import dotenv
import psycopg
import json
from glob import glob
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
  sql = "DELETE from pages; DELETE from sources;"
  conn.execute(sql)
  conn.commit()
  for file in glob('output/*.json'):
    if file != 'output/questions_embedded.json':
      print("Loading file: " + file)
      data = json.load(open(file, 'r'))
      sql = "INSERT INTO sources (title, author, type, ref) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING RETURNING id;"

      for item in data:
        title = item["title"] if "title" in item else ""
        author = item["author"] if "author" in item else ""
        _type = item["type"] if "type" in item else ""
        ref = item["ref"] if "ref" in item else ""
        cur = conn.execute(sql, (title, author, _type, ref))
        _id = cur.fetchone()[0]
        for page in item["pages"]:
          sql = "INSERT INTO pages (text, page_number, embedding, source_id) VALUES (%s, %s, %s, %s);"
          try:
            conn.execute(sql, (page["content"], page["number"], page["embedding"], _id))
          except:
            print(page.keys())
        conn.commit()
      print("Done loading file: " + file)

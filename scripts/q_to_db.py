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

            drop table if exists question_tags;
            drop table if exists tags;
            drop table if exists questions;

            create table questions (
                id char(36) primary key,
                enunciate text not null,
                answer text,
                explanation text,
                combined text not null,
                year char(4) not null,
                exam char(7) not null,
                addr char(11) not null,
                part char(1) not null,
                number char(3) not null,
                embedding_enunciate vector(1536),
                embedding_answer vector(1536),
                embedding_explanation vector(1536),
                embedding_combined vector(1536)
            );

            create table tags (
                id serial primary key,
                tag text unique not null
            );

            create table question_tags (
                question_id char(36) references questions(id),
                tag_id integer references tags(id),
                primary key(question_id, tag_id)
            );
            """
        cur.execute(table_sql)
        conn.commit()
        docs = json.loads(open('output/questions_tagged.json', 'r').read())
        question_sql = "INSERT INTO questions (id, enunciate, answer, explanation, combined, embedding_enunciate, embedding_answer, embedding_explanation, embedding_combined, year, exam, part, number, addr) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"
        tag_sql = "INSERT INTO tags (tag) VALUES (%s) ON CONFLICT (tag) DO UPDATE SET tag=EXCLUDED.tag RETURNING id;"
        question_tag_sql = "INSERT INTO question_tags (question_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;"

        for doc in docs:
            (y, p, q) = doc["addr"].split(".")
            cur.execute(question_sql, (
                 str(uuid.uuid4()),
                 doc["enunciate"],
                 doc["answer"],
                 doc["explanation"],
                 doc["combined"],
                 doc["embedding_enunciate"],
                 doc["embedding_answer"],
                 doc["embedding_explanation"],
                 doc["embedding_combined"],
                 y[:4],
                 "Final" if y.endswith('f') else "Midterm",
                 p,
                 q,
                 doc["addr"]
            ))
            question_id = cur.fetchone()[0]

            for tag in doc["tags"]:
                cur.execute(tag_sql, (tag,))
                tag_id = cur.fetchone()[0]

                cur.execute(question_tag_sql, (question_id, tag_id))
            conn.commit()

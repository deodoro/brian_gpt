import os
import dotenv
import psycopg
from psycopg.conninfo import make_conninfo

dotenv.load_dotenv()

pg_string = make_conninfo(
  host=os.getenv('DB_HOST'),
  port=os.getenv('DB_PORT'),
  dbname=os.getenv('DB_DATABASE'),
  user=os.getenv('DB_USER'),
  password=os.getenv('DB_PASSWORD')
)

table_sql = """
create extension if not exists vector;

drop table if exists pages;
drop table if exists sources;
drop table if exists questions;

create table questions (
  id serial primary key,
  enunciate text not null,
  answer text,
  explanation text,
  combined text not null,
  embedding_enunciate vector(1536),
  embedding_answer vector(1536),
  embedding_explanation vector(1536),
  embedding_combined vector(1536)
);

alter table questions add constraint unique_enunciate unique (enunciate);

create table sources (
    id serial primary key,
    title varchar(255) not null,
    author varchar(255),
    type varchar(255),
    ref varchar(255)
);

create table pages (
    id serial primary key,
    text text not null,
    page_number integer not null,
    embedding vector(1536) not null,
    source_id integer not null,
    foreign key (source_id) references sources(id)
);
"""

with psycopg.connect(pg_string) as conn:
    conn.execute(table_sql)

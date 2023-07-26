# Create database
import os
import dotenv
import psycopg2
import json
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg.conninfo import make_conninfo
from langchain.vectorstores.pgvector import PGVector, DistanceStrategy
from langchain.embeddings.openai import OpenAIEmbeddings

if __name__ == '__main__':
    dotenv.load_dotenv()
    connection_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"

    # Connect to your postgres DB
    conn = psycopg2.connect(connection_string)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # execute your SQL statement
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    print("Extension 'vector' created (if not existed)")

    # close the cursor and connection
    cur.close()
    conn.close()

    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

    with open('output/chunked_350.1.json', 'rt') as f:
       raw = json.load(f)
       for _type in ['paper', 'book', 'blog', 'lecture', 'notes']:
           pairs = [(doc['page_content'], doc['embedding']) for doc in raw if doc['metadata']['type'] == _type]
           metadata = [doc['metadata'] for doc in raw if doc['metadata']['type'] == _type]
           PGVector.from_embeddings(
               embedding=embeddings,
               text_embeddings=pairs,
               metadatas=metadata,
               distance_strategy=DistanceStrategy.COSINE,
               collection_name=_type + '_350',
               connection_string=connection_string,
           )

    # with open('output/chunked_3000.1.json', 'rt') as f:
    #    raw = json.load(f)
    #    for _type in ['paper', 'book', 'blog', 'lecture', 'notes']:
    #        pairs = [(doc['page_content'], doc['embedding']) for doc in raw if doc['metadata']['type'] == _type]
    #        metadata = [doc['metadata'] for doc in raw if doc['metadata']['type'] == _type]
    #        PGVector.from_embeddings(
    #            embedding=embeddings,
    #            text_embeddings=pairs,
    #            metadatas=metadata,
    #            distance_strategy=DistanceStrategy.COSINE,
    #            collection_name=_type + '_3000',
    #            connection_string=connection_string,
    #        )

    # with open('output/chunked_1500.1.json', 'rt') as f:
    #     raw = json.load(f)
    #     for _type in ['paper', 'book', 'blog', 'lecture', 'notes']:
    #         pairs = [(doc['page_content'], doc['embedding']) for doc in raw if doc['metadata']['type'] == _type]
    #         metadata = [doc['metadata'] for doc in raw if doc['metadata']['type'] == _type]
    #         PGVector.from_embeddings(
    #             embedding=embeddings,
    #             text_embeddings=pairs,
    #             metadatas=metadata,
    #             distance_strategy=DistanceStrategy.COSINE,
    #             collection_name=_type + '_1500',
    #             connection_string=connection_string,
    #         )

    # with open('output/chunked_750.1.json', 'rt') as f:
    #    raw = json.load(f)
    #    for _type in ['paper', 'book', 'blog', 'lecture', 'notes']:
    #        pairs = [(doc['page_content'], doc['embedding']) for doc in raw if doc['metadata']['type'] == _type]
    #        metadata = [doc['metadata'] for doc in raw if doc['metadata']['type'] == _type]
    #        PGVector.from_embeddings(
    #            embedding=embeddings,
    #            text_embeddings=pairs,
    #            metadatas=metadata,
    #            distance_strategy=DistanceStrategy.COSINE,
    #            collection_name=_type + '_750',
    #            connection_string=connection_string,
    #        )

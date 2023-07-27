# Create database
import os
import dotenv
import json
from langchain.vectorstores.redis import Redis
from langchain.embeddings.openai import OpenAIEmbeddings

if __name__ == '__main__':
    dotenv.load_dotenv()

    embedding_f = OpenAIEmbeddings(model="text-embedding-ada-002")

    with open('output/chunked_350.1.json', 'rt') as f:
       raw = json.load(f)
       for _type in ['paper', 'book', 'blog', 'lecture', 'notes']:
           texts = [doc['page_content'] for doc in raw if doc['metadata']['type'] == _type]
           if len(texts) > 0:
            embeddings = [doc['embedding'] for doc in raw if doc['metadata']['type'] == _type]
            metadata = [doc['metadata'] for doc in raw if doc['metadata']['type'] == _type]
            Redis.from_texts(
                texts=texts,
                embedding=embedding_f,
                metadatas=metadata,
                embeddings=embeddings,
                index_name=_type + '_350',
                redis_url="redis://localhost:6379",
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

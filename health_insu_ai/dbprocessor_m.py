import os.path
#from langchain_community.vectorstores.pgvector import PGVector
#from langchain_postgres import PGVector
from vectorstores import PGVector
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
# Create a PGVector instance to house the documents and embeddings
from langchain_community.vectorstores.pgvector import DistanceStrategy
from dotenv import load_dotenv, find_dotenv

from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

_ = load_dotenv(find_dotenv())

embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key= os.environ['HUGGINGFACEHUB_API_TOKEN'], model_name="BAAI/bge-base-en-v1.5"
)

  # Initialize Embeddings
# embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")
    

def get_pgvector_connection():
   # Build the PGVector Connection String from params
# Found in the credential cheat-sheet or "Connection Info" in the Timescale console
# In terminal, run: export VAR_NAME=value for each of the values below
   host= os.environ['LOCAL_HOST']
   port= os.environ['LOCAL_PORT']
   user= os.environ['LOCAL_USER']
   password= os.environ['LOCAL_PASSWORD']
   dbname= os.environ['LOCAL_DBNAME']
   dbschema=os.environ['LOCAL_DB_SCHEMA']
   # We use postgresql rather than postgres in the conn string since LangChain uses sqlalchemy under the hood
   # You can remove the ?sslmode=require if you have a local PostgreSQL instance running without SSL
   CONNECTION_STRING = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}"

   return CONNECTION_STRING

def upsert_pgvector_db(docs,collection_name):
    db = PGVector.from_documents(
    documents= docs,
    embedding = embeddings,
    collection_name= collection_name,
    distance_strategy = DistanceStrategy.COSINE,
    connection=get_pgvector_connection(),
    pre_delete_collection=False,
    use_jsonb=True
    )
    return db

def pgvector_db_retriever(collection_name):
    store = PGVector(
    collection_name=collection_name,
    connection=get_pgvector_connection(),
    embeddings=embeddings,
    distance_strategy = DistanceStrategy.COSINE
    
    )

    return store

def apgvector_db_retriever(collection_name):
    store = PGVector(
    collection_name=collection_name,
    connection=get_pgvector_connection(),
    embeddings=embeddings,
    distance_strategy = DistanceStrategy.COSINE,
    use_jsonb=True,
    async_mode=True
    
    )

    return store


def get_pgv_db():
    vectorstore= PGVector.from_existing_index(
    embedding = embeddings,
    collection_name= "benefitsummary",
    distance_strategy = DistanceStrategy.COSINE,
    connection_string=get_pgvector_connection(),
    pre_delete_collection=False,)
    
    return vectorstore

def pgv_metadatas_search(texts,metadatas):
    docsearch = PGVector.from_texts(
    texts=texts,
    collection_name="benefitsummary_md",
    embedding=embeddings,
    metadatas=metadatas,
    distance_strategy = DistanceStrategy.COSINE,
    connection_string=get_pgvector_connection(),
    pre_delete_collection=True,
)
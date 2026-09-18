from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_transformers.openai_functions import (
    create_metadata_tagger,
)
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_voyageai import VoyageAIEmbeddings
from pymongo import MongoClient

import key_param

# Set the MongoDB URI, DB, Collection Names

client = MongoClient(key_param.MONGODB_URI)
dbName = "book_mongodb_chunks"
collectionName = "chunked_data"
collection = client[dbName][collectionName]

pdf_path = (
    Path(__file__).resolve().parent
    / "fichiers_exemples"
    / "documentation_stack_project.pdf"
)
loader = PyPDFLoader(str(pdf_path))
pages = loader.load()
cleaned_pages = []

for page in pages:
    if len(page.page_content.split(" ")) > 20:
        cleaned_pages.append(page)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=150)

schema = {
    "properties": {
        "title": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string"}},
        "hasCode": {"type": "boolean"},
    },
    "required": ["title", "keywords", "hasCode"],
}

llm = ChatGroq(
    groq_api_key=key_param.GROQ_API_KEY,
    temperature=0,
    model="openai/gpt-oss-20b",
)

document_transformer = create_metadata_tagger(metadata_schema=schema, llm=llm)

docs = document_transformer.transform_documents(cleaned_pages)

split_docs = text_splitter.split_documents(docs)

embeddings = VoyageAIEmbeddings(
    voyage_api_key=key_param.VOYAGE_API_KEY,
    model="voyage-3-large",
    batch_size=128,
)


vectorStore = MongoDBAtlasVectorSearch.from_documents(
    split_docs, embeddings, collection=collection
)
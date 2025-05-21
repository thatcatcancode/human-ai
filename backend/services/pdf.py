from fastapi import HTTPException, UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
import tempfile


def process_file(file: UploadFile):
    # Save uploaded file to temp directory
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        content = file.file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # load
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()

        # simple chunking
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = splitter.split_documents(docs)

        # embed
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

        # persist in vector store
        db = Chroma.from_documents(chunks, embeddings, persist_directory="chroma_db")
        db.persist()
    finally:
        # Clean up temp file
        os.unlink(tmp_path)
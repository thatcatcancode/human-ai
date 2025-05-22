from fastapi import HTTPException, UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
import tempfile


async def process_file(file: UploadFile):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Save uploaded file to temp directory
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    try:
        # load
        try:
            loader = PyPDFLoader(tmp_path)
            docs = loader.load()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to load PDF: {str(e)}")

        # simple chunking
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
            chunks = splitter.split_documents(docs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process document chunks: {str(e)}")

        # embed
        try:
            embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize embeddings: {str(e)}")

        # persist in vector store
        try:
            db = Chroma.from_documents(chunks, embeddings, persist_directory="chroma_db")
            db.persist()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to store embeddings: {str(e)}")

    finally:
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except Exception:
            pass  # Ignore cleanup errors
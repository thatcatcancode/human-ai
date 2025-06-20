from fastapi import HTTPException, UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec
import os
import tempfile
import uuid
import hashlib
from datetime import datetime

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

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
            splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "."], chunk_size=300, chunk_overlap=35)
            split_docs = splitter.split_documents(docs)
            chunks = [doc.page_content for doc in split_docs]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process document chunks: {str(e)}")

        # embed
        try:
            embeddings = HuggingFaceEmbeddings(model="sentence-transformers/all-mpnet-base-v2")
            vectors = embeddings.embed_documents(chunks)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize embeddings: {str(e)}")

        # persist in vector store
        try:
            
            # 1. Instantiate a client ──────────────────────────────────────────
            pc = Pinecone(api_key=PINECONE_API_KEY)

            # 2. Create or connect to an index
            # Get existing indexes
            if not pc.has_index(PINECONE_INDEX_NAME):
                pc.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=768,
                    vector_type="dense",
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region='us-east-1')
                )

            index = pc.Index(PINECONE_INDEX_NAME)
            
            # 3. Upsert your embeddings
            vectors_to_upsert = []
            file_hash = hashlib.md5(file.filename.encode()).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            for i, (vector, chunk) in enumerate(zip(vectors, chunks)):
                # Create unique ID with file info and timestamp
                unique_id = f"{file_hash}_{timestamp}_chunk_{i}"
                
                vectors_to_upsert.append({
                    "id": unique_id,
                    "values": vector,
                    "metadata": {
                        "text": chunk,
                        "filename": file.filename,
                        "upload_time": timestamp,
                        "chunk_index": i
                    }
                })
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i+batch_size]   
                print(f"Upserting batch {i//batch_size + 1} of {len(vectors_to_upsert)//batch_size}")
                index.upsert(vectors=batch)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to store embeddings: {str(e)}")

    finally:
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except Exception:
            pass  # Ignore cleanup errors
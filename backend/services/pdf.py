from fastapi import HTTPException, UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from pinecone import Pinecone
#from langchain.vectorstores import Pinecone
import os
import tempfile

OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV     = os.getenv("PINECONE_ENVIRONMENT")  # e.g. "us-west1-gcp"
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
            splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
            split_docs = splitter.split_documents(docs)
            chunks = [doc.page_content for doc in split_docs]
            assert all(isinstance(c, str) for c in chunks), "All chunks must be plain strings"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process document chunks: {str(e)}")

        # embed
        try:
            embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
            print('chunks', chunks)
            vectors = embeddings.embed_documents(chunks)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize embeddings: {str(e)}")

        # persist in vector store
        try:
            
            # 1. Instantiate a client ──────────────────────────────────────────
            client = Pinecone(api_key=PINECONE_API_KEY)

            # 2. Create or connect to an index
            # Get existing indexes
            existing_indexes = [index.name for index in client.list_indexes()]
            if PINECONE_INDEX_NAME not in existing_indexes:
                client.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=1536,  # your embedding dimension
                    metric="cosine",
                    spec=dict(
                        serverless=dict(
                            cloud="aws",
                            region=PINECONE_ENV
                        )
                    )# or "euclidean", etc.
                )

            index = client.Index(PINECONE_INDEX_NAME)
            
            # 3. Upsert your embeddings
            vectors_to_upsert = []
            for i, (vector, chunk) in enumerate(zip(vectors, chunks)):
                vectors_to_upsert.append(
                    {
                        "id": f"doc_{i}",
                        "values": vector,
                        "metadata": {
                            "text": chunk
                        }
                    }   
                )
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
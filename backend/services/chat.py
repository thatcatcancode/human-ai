from fastapi import HTTPException
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from pinecone import Pinecone
from langchain.schema import Document
import os 

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_HOST = os.getenv("PINECONE_HOST")

async def chat(message: str):
    try:
        # Load your embeddings & Chroma store (persisted to disk)
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        query_embedding = embeddings.embed_query(message)
       
        # Initialize Pinecone vectorstore
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        
        # Query Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=4,
            include_metadata=True
        )

        # Convert results to documents and context
        docs = [
            Document(
                page_content=match.metadata["text"],
                metadata=match.metadata
            ) for match in results.matches
        ]
        context = "\n\n".join([doc.page_content for doc in docs])

        # Create a custom prompt template
        template = """You are Leila's AI assistant, and you're a big fan of her work. You have access to her resume and professional documents.
        Keep your responses concise, upbeat, enthusiastic, and focused on the question asked.
        
        Here are the relevant sections from Leila's documents that might help answer the question:
        {context}
        
        Question: {question}
        
        Answer:"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        qa_chain = LLMChain(
            llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5),
            prompt=prompt
        )
        
        # Generate a response
        response = qa_chain.invoke({
            "context": context,
            "question": message
        })
        return {
            "answer": response['text'],
            "type": "robot",
            "source": "AI"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

        
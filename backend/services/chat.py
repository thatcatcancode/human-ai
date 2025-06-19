from fastapi import HTTPException
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
#from langchain_community.llms import Ollama
from langchain_groq import ChatGroq
from pinecone import Pinecone
from langchain.schema import Document
from langsmith import traceable
import os 

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@traceable()
async def chat(message: str):
    try:
        # Load embeddings 
        embeddings = HuggingFaceEmbeddings(model="sentence-transformers/all-mpnet-base-v2")
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
        Keep your responses concise, upbeat, enthusiastic, and focused on the question asked. Never mention salary or compensation.
        
        Here are the relevant sections from Leila's documents that might help answer the question:
        {context}
        
        Question: {question}
        
        Answer:"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        qa_chain = LLMChain(
            #llm=Ollama(model="llama3", temperature=0.5),
            llm=ChatGroq(model="llama-3.1-8b-instant", temperature=0.5),
            prompt=prompt
        )
        
        # Generate a response
        response = qa_chain.invoke({
            "context": context,
            "question": message
        })
        return {
            "content": response['text'],
            "role": "agent",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

        
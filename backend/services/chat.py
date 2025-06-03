from fastapi import HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
#from langchain.vectorstores import Pinecone
from pinecone import Pinecone
import os 

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

async def chat(message: str):
    try:
        # Load your embeddings & Chroma store (persisted to disk)
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        query_embedding = embeddings.embed_query(message)
       
       # Initialize Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        
        # Query Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=4,
            include_metadata=True
        )
        
        # Extract context from results
        context = "\n\n".join([match.metadata["text"] for match in results.matches])

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
        
        # Build a Retriever + QA chain with custom prompt
        # retriever = vectordb.as_retriever(
        #     search_kwargs={
        #         "k": 4  # Number of most relevant chunks to retrieve
        #     }
        # )
        
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

        
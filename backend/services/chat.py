from fastapi import HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

async def chat(message: str):
    try:
        # Load your embeddings & Chroma store (persisted to disk)
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        vectordb = Chroma(
            embedding_function=embeddings,
            persist_directory="chroma_db"
        )
        
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
        retriever = vectordb.as_retriever(
            search_kwargs={
                "k": 4  # Number of most relevant chunks to retrieve
            }
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5),
            chain_type="stuff",  # This combines all retrieved documents into a single context
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True  # This will help us see what documents were used
        )
        
        # Generate a response
        response = qa_chain.invoke({"query": message})
        return {
            "answer": response['result'],
            "type": "robot",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

        
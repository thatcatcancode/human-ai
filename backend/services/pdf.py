from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


def process_file(file_path: str):
    # load
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    # simple chunking
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    # embed
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

    # persist in vector store
    db = Chroma.from_documents(chunks, embeddings, persist_directory="chroma_nestle_hr")
    db.persist()
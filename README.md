# human-ai
RAG project that ingests resume and other docs about myself and answers recruiter questions about my professional expereince.

## Get Started

### First time set up
```
cd backend

# create virtual env
/Users/ladams/.pyenv/versions/3.12.10/bin/python3.12 -m venv venv

# activate venv
source venv/bin/activate

# verify in virtual env:
echo $VIRTUAL_ENV
# will return a file path to your venv

copy .env file and set your own values
mv .env-template .env

# install deps
pip install -r requirements.txt

pip install "fastapi[standard]"

# start the server
fastapi dev main.py

```

### Run the project 

```
cd backend

source venv/bin/activate

# install any new deps 
pip install -r requirements.txt

# start the server
fastapi dev main.py

```

## Workflow 

- Upload pdf (requires auth)
- Chunking
- Embeddings
- Persist in vector db
- Ask a question via /chat endpoint
- Query vectorstore for relevant chunks and format answer by LLM 
- Integrate with my-portfolio web site

## Technical Approach

- LangChain for simple, clean code. ex: PyPDFLoader
- Pinecone for vectorstore
- Meta's free llama3 model for human formatted responses
- Hugging Face transformer for embeddings (768 dimensions)
- Groq Cloud for hosting LLM
- Python's FastAPI for RESTful endpoints (/load and /chat)
- LangSmith - logging & monitoring
- Render for web service hosting (too expensive)

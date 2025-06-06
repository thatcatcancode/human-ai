# human-ai
RAG project that ingests resume and other docs about myself and answers recruiter questions about my professional expereince.

## Get Started

### First time set up
```
cd /backend

# create virtual env
py -m venv venv

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
cd /backend

source venv/bin/activate

# install any new deps 
pip install -r requirements.txt

# start the server
fastapi dev main.py

```

## Workflow 

- Upload pdf (private endpoint)
- Chunking
- Embed
- Persist in vector db
- Ask a question via /chat endpoint
- Query vectorstore for relevant chunks and retreive answer from LLM 
- Integrate with my-portfolio web site

## Technical Approach

- LangChain for simple, clean code. ex: PyPDFLoader
- Pinecone for vectorstore
- Llama model for human responses
- Hugging Face hosting for IP protection
- Python's FastAPI for RESTful endpoints 
- LangSmith - logging, monitoring, deployment, etc. 

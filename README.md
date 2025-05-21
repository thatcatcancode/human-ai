# human-ai
AI Powered Human Resources Assistant

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

source env/bin/activate

# install any new deps 
pip install -r requirements.txt

# start the server
fastapi dev main.py

```

## Workflow 

- Upload pdf 
- Chunking
- Embed
- Persist in vector db

## Technical Approach

- LangChain for simple, clean code. ex: PyPDFLoader 
- LangServe with RESTful API 
- LangSmith - logging, monitoring, deployment, etc. 

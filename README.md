# human-ai
RAG project that ingests resume and other docs about myself and answers recruiter questions about my professional expereince.

Swagger
https://human-ai-latest.onrender.com/docs

See it in action 👇
https://thatcatcancode.github.io/my-portfolio/

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

## Lessons Learned


🔄 LangChain packages change constantly, and managing package dependencies is a big part of developing a RAG-based app.


🔍 LangSmith was super easy to set up for monitoring chains — a must-have for tracking all the weird stuff your users will ask 💬 and the odd things LLMs will say 🤖.


🧩 There’s definitely an art to splitting, chunking, and embedding into dimension space — but my main issue was overwriting vector IDs with collisions. DOH! 😅


🤝 OpenAI was by far the easiest to set up for both embeddings and LLMs, but I wasn’t 100% confident they wouldn’t use my RAG context to train their next model 🧠⚠️.


🚀 I switched to Meta’s free LLaMA 3 model, served by blazing-fast Groq — it was responsive, creative in word choice, and followed prompts very well 🎯✨.


🧠 I used Hugging Face Sentence Transformers for embeddings, but it required ~2GB RAM and kept crashing my Render service 🧨 until I upgraded to a paid tier 💸. I should migrate to AWS EC2 or choose a leaner transformer. There’s definitely an art to picking the right one 🎨.


📄 Honestly, a static FAQ with fixed Q&A in a local JSON file would've worked better here — no vector store, no model, no headaches 🙃.


🏢 For companies, a chatbot that surfaces knowledge base content is useful — but RAG doesn't automatically mean it won't hallucinate. While RAG does not involve training or fine-tuning a model, you do need to update docs and re-embed them in your vector db. You don't play around with hyper params but you might need to experiment with text splitting separators. In other words, you still need to pull the levers. 


🏆 Overall I saw quick wins, but do have to monitor the logs and upload corrective documents when the LLM says weird stuff about me.  

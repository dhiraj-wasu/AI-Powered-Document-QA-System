 AI-Powered Document QA System (RAG-based)

An end-to-end Retrieval-Augmented Generation (RAG) system that lets you upload documents, store them as vector embeddings in a PostgreSQL database (with pgvector), and ask natural-language questions about their content — getting accurate answers powered by OpenAI GPT models.

Features
1.Document Uploading & Parsing — PDFs parsed with PyMuPDF (fitz)

2.Chunking & Embedding — Documents split into small chunks and embedded with OpenAI text-embedding-3-small

3.Vector Search — Uses pgvector extension in PostgreSQL for fast semantic similarity search

5.Chat Interface — Clean conversational UI built with Streamlit

6.RAG Pipeline — Retrieval-Augmented Generation: retrieved chunks are fed into GPT to answer user questions

7.Containerized — Fully dockerized with docker-compose for one-click setup


System Architecture
User → Streamlit UI → Query
                  ↓
        Retrieve Top-K Similar Chunks
        from PostgreSQL (pgvector)
                  ↓
     Inject chunks into GPT prompt
                  ↓
           GPT generates answer
                  ↓
         Response shown in chat

📁 Project Structure
.
├── main.py                      # Initializes database schema
├── db.py                        # Database models & pgvector setup
├── chat_with_doc.py             # Streamlit RAG chat interface
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image for app
├── docker-compose.yml            # App + pgvector DB services
└── .env                         # Environment variables

⚙Tech Stack

Language: Python 3.10

Frontend: Streamlit

Database: PostgreSQL + pgvector extension

ORM: Peewee

Embeddings: OpenAI text-embedding-3-small

LLM: OpenAI gpt-4o-mini-2024-07-18

Containerization: Docker & Docker Compose

Setup Instructions
1. Clone the repository
git clone https://github.com/your-username/ai-powered-document-qa.git
cd ai-powered-document-qa

2. Add environment variables

Create a .env file:

POSTGRES_DB_NAME=ragdb
POSTGRES_DB_USER=postgres
POSTGRES_DB_PASSWORD=yourpassword
POSTGRES_DB_HOST=pgvector-db
POSTGRES_DB_PORT=5432
OPENAI_API_KEY=sk-xxxxxx

3. Build and run with Docker Compose
docker-compose up --build


Then open: http://localhost:8501

Usage

Start the app

Upload your documents (PDFs)

Ask any question related to them

The system retrieves relevant chunks and generates answers using GPT

Key Python Packages
streamlit
python-dotenv
peewee
pgvector
psycopg2-binary
PyMuPDF
openai

Concepts Demonstrated

Retrieval-Augmented Generation (RAG)

Vector Databases & Semantic Search

Chunking strategies for document embeddings

Prompt engineering & system prompts

Database schema design for document QA

Async handling & retry logic

Clean, modular Python codebase

Full-stack containerized deployment

⭐️ If you like this project

Give it a ⭐ on GitHub to show support!

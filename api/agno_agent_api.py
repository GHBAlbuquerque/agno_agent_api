from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.chunking.recursive import RecursiveChunking

from agno.tools.yfinance import YFinanceTools

from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.chroma import ChromaDb

from fastapi import FastAPI
import uvicorn

import asyncio

import os
from dotenv import load_dotenv

load_dotenv()

# ======================
# In-memory SQL DB
# ======================
db = SqliteDb(session_table="agent_session", db_file="tmp/agent.db")

# ======================
# Vector DB (RAG)
# ======================
vector_db = ChromaDb(
    collection="company_reports",
    path="tmp/Chromadb",
    embedder=OpenAIEmbedder(
        id="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY")
    ),
    persistent_client=True
)

# ======================
# Knowledge class - Manages knowledge for AI agents
# ======================

knowledge = Knowledge(
    vector_db=vector_db
)

# ======================
# Reader - Converts files, URLs, and text into searchable documents.
# ======================

pdf_reader = PDFReader(
    chunking_strategy=RecursiveChunking(
        chunk_size=2000,
        overlap=200,
    ),
)

# ======================
# Agent
# ======================
agent = Agent(
    name="api_agent",
    model=OpenAIChat(
        id="gpt-5-nano",
        api_key=os.getenv("OPENAI_API_KEY"),
    ),
    tools=[YFinanceTools()],
    instructions=("Call user `Client`"),
    db=db,
    num_history_runs=3,

    # RAG 
    knowledge=knowledge,
    search_knowledge=True
)

# ======================
# Tests
# ======================

# agent.print_response(
#     "What were Ubisoft's IRFS 15 Sales in Q1 of 2025-26 and 2025-24?",
#     session_id="ubisoft_session_1", 
# )

# agent.print_response(
#     "What was said of the strategic Vantage studios investments?",
#     session_id="ubisoft_session_2", 
# )

# ======================
# API
# ======================

app = FastAPI(
    title="FastAPI Asimov",
    description="Asimov API"
)

@app.post("/agent_pdf")
def balance(question: str):
    response = agent.run(question);
    return {"message": response.content}

# ======================
# Server
# ======================
if __name__ == "__main__":

    # must be ran async
    asyncio.run(knowledge.add_content_async(
    path="files/UBISOFT/",
    reader=pdf_reader,
    skip_if_exists=True
    ))

    uvicorn.run("agno_agent_api:app", host="0.0.0.0", port=8000, reload=True)

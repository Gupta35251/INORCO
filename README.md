# INORCO Website Chatbot — Agentic RAG System

An AI-powered chatbot that answers questions about **[INORCO](https://www.inorco.in)** — an industrial paints, solvents, and coatings company — using only information scraped from its official website. Built with an agentic Retrieval-Augmented Generation (RAG) architecture, deployed as a public API, and embeddable as a chat widget on the live website.

---

## Overview

The chatbot answers user questions about INORCO's products (paints, primers, solvents, coatings), applications, specifications, and contact details — strictly using content retrieved from the company's own website, not general LLM knowledge. If information isn't found in the knowledge base, the assistant says so instead of guessing.

**Live backend:** Deployed on Hugging Face Spaces (Docker)
**Frontend:** A lightweight, embeddable chat widget (HTML/CSS/JS)

---

## Architecture

```
┌─────────────────────┐
│  INORCO Website      │
│  (inorco.in)          │
└──────────┬───────────┘
           │ scraped via Firecrawl
           ▼
┌─────────────────────┐
│  scraping_web_page.py │  →  web_data/*.md
└──────────┬───────────┘
           │ cleaned, chunked, embedded
           ▼
┌─────────────────────┐
│   ingest_docs.py      │  →  vector_db/ (Chroma)
└──────────┬───────────┘
           │
           ▼
┌─────────────────────┐
│      tools.py          │  RAG retrieval tool (similarity search + Groq LLM)
└──────────┬───────────┘
           │
           ▼
┌─────────────────────┐
│  agent.py + tasks.py   │  CrewAI agent orchestration
│  + crew.py             │
└──────────┬───────────┘
           │
           ▼
┌─────────────────────┐
│      main.py           │  FastAPI backend (/chat endpoint)
│  (deployed on HF Spaces)│
└──────────┬───────────┘
           │ HTTPS request/response
           ▼
┌─────────────────────┐
│    widget.html         │  Embeddable chat widget
│  (pasted into website)  │
└─────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web scraping | [Firecrawl](https://firecrawl.dev) |
| Text splitting & document loading | LangChain (`CharacterTextSplitter`, `UnstructuredFileLoader`) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace) |
| Vector database | [Chroma](https://www.trychroma.com/) |
| Retrieval | LangChain similarity search |
| LLM | Groq (`llama-3.3-70b-versatile`) |
| Agent orchestration | [CrewAI](https://www.crewai.com/) |
| Backend API | FastAPI + Uvicorn |
| Deployment | Hugging Face Spaces (Docker) |
| Frontend widget | Vanilla HTML/CSS/JavaScript (no framework, no build step) |

> **Note:** This project uses a straightforward vector similarity retriever. It does **not** use BM25 or hybrid keyword+vector search.

---

## Project Structure

```
INORCO/
├── agents/
│   ├── agent.py            # CrewAI agent definition (role, goal, backstory, LLM)
│   ├── tasks.py             # Task definition describing what the agent must do
│   └── tools.py             # RAG retrieval tool (Chroma + Groq)
├── vector_db/                # Persisted Chroma vector database
├── web_data/                  # Scraped website pages (markdown)
├── crew.py                    # Assembles agent + task into a runnable Crew
├── ingest_docs.py              # Loads, cleans, chunks, embeds, and stores website data
├── scraping_web_page.py         # Scrapes inorco.in into markdown files using Firecrawl
├── main.py                      # FastAPI backend exposing the chatbot as an API
├── widget.html                   # Embeddable chat widget for the website
├── Dockerfile                     # Container definition for deployment
├── requirements.txt                # Python dependencies
└── .env                              # Local environment variables (not committed)
```

---

## How It Works

1. **Scraping** — `scraping_web_page.py` crawls up to 100 pages of `inorco.in` using Firecrawl and saves each page as a markdown file in `web_data/`.

2. **Ingestion** — `ingest_docs.py`:
   - Loads all markdown files
   - Cleans repeated boilerplate (phone numbers, emails, SEO keyword blocks that repeat on every page)
   - Splits documents into chunks
   - Removes near-duplicate chunks (the same product blurb often appears on multiple pages)
   - Embeds each chunk using `all-MiniLM-L6-v2`
   - Persists everything into a local Chroma vector database (`vector_db/`)

3. **Retrieval Tool** — `tools.py` defines a CrewAI tool that:
   - Takes a user's question
   - Retrieves the most relevant chunks from Chroma using similarity search
   - Passes those chunks + the question to a Groq LLM
   - Returns an answer strictly grounded in the retrieved content

4. **Agent** — `agent.py` defines an agent whose backstory instructs it to **always** consult the RAG tool before answering, and to say "not found on the website" rather than fabricate an answer.

5. **Task & Crew** — `tasks.py` and `crew.py` wire the agent and task together into a single callable pipeline (`crew.kickoff({...})`).

6. **API** — `main.py` wraps `crew.kickoff(...)` in a FastAPI `/chat` POST endpoint, so any HTTP client (including a browser) can query the chatbot.

7. **Widget** — `widget.html` is a self-contained floating chat bubble that calls the deployed `/chat` endpoint and displays responses — this is the only file that needs to be added to the live website.

---

## Local Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd INORCO
pip install -r requirements.txt
```

### 2. Set environment variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

### 3. Scrape the website (one-time, or whenever content changes)

```bash
python scraping_web_page.py
```

### 4. Build the vector database

```bash
python ingest_docs.py
```

### 5. Test the RAG tool directly

```bash
python -m agents.tools
```

### 6. Run the backend API locally

```bash
uvicorn main:app --reload --port 8000
```

Visit `http://127.0.0.1:8000/docs` to test the `/chat` endpoint interactively.

### 7. Test the widget locally

Open `widget.html` directly in a browser (double-click the file), or serve it via any static file server. Update `API_URL` inside the file to point to your running backend.

---

## Deployment

The backend is deployed on **Hugging Face Spaces** using Docker (chosen over other free hosting options due to its higher free-tier RAM allocation, which this project's ML dependencies — PyTorch, sentence-transformers, ChromaDB — require).

### Deployment steps

1. Create a Space on Hugging Face with SDK type **Docker**.
2. Add a `Dockerfile` (included in this repo) that installs dependencies and runs Uvicorn on port `7860`.
3. Push the project (excluding `.env`) to the Space's git repository.
4. Add `GROQ_API_KEY` as a **secret** in the Space's settings (not committed to code).
5. Once running, the API is publicly available at:
   ```
   https://<your-username>-<space-name>.hf.space
   ```

### CORS configuration

`main.py` restricts which domains may call the API:

```python
allow_origins=[
    "https://www.inorco.in",
    "https://inorco.in",
]
```

This must match the exact domain the widget is hosted on, or browsers will block requests.

---

## Embedding the Chatbot on the Website

Only **`widget.html`** needs to be shared with whoever manages the website. No other project files, credentials, or setup are required on their end.

**Instructions for the website admin:**
1. Open the site's shared footer/template file (or each page, if no shared template exists).
2. Paste the entire contents of `widget.html` just before the closing `</body>` tag.
3. Save/publish.

A blue chat bubble will appear in the bottom-right corner of the site, connected live to the deployed backend.

---

## Known Limitations

- **Groq free-tier rate limits** — heavy or rapid testing can occasionally trigger rate-limit errors, causing the tool to fail silently and the agent to fall back to a generic error message.
- **Free-tier cold starts** — if the Hugging Face Space goes idle, the first request after inactivity can take 30–60 seconds while the container wakes up.
- **Website content freshness** — the knowledge base only reflects the site as of the last scrape. Re-run `scraping_web_page.py` and `ingest_docs.py` whenever the website content changes.

---

## Future Improvements

- Add hybrid retrieval (vector + keyword search) to improve recall on short, label-style content (e.g. contact details).
- Add caching to reduce repeated Groq API calls for identical/similar questions.
- Add automated re-scraping on a schedule to keep the knowledge base current.
- Add authentication/rate-limiting on the `/chat` endpoint to prevent abuse.

---

## License

Internal project for INORCO. Not licensed for redistribution.

# CoursePath

**Project members**

- Timothy Chan (TimothyChan2912)
- Saket Gajavada

CoursePath is a web-based course recommendation system designed to simplify and optimize the college course planning and enrollment process. Students can upload their academic transcripts, which are processed to extract completed coursework. The system then analyzes prerequisites and degree requirements to generate personalized course recommendations and suggested semester plans.

The platform also integrates course catalog data scraping and a natural language processing-based assistant to help students make informed academic decisions more efficiently.

---

## Prerequisites

| Requirement | Notes |
|--------------|--------|
| **Python** | **3.10+** recommended (tested with **3.12**). |
| **pip / venv** | Standard library `venv` is enough. |
| **Ollama** | Required only for the **AI Advisor** tab. Catalog, transcript upload, scheduling, and reviews work without it. |

No separate Node build step — the UI is Flask templates plus static JS/CSS.

---

## Quick start

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd CoursePath
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Verify data files

The app expects:

- **`data/catalog.json`** — course list loaded by `backend/catalog.py` (committed in this repo).
- **`data/reviews.json`** — created automatically when someone submits a review (if missing, reviews still initialize safely).

Uploaded transcripts are stored under **`uploads/`** (created on first upload).

### 4. Run the server

```bash
python app.py
```

Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

The server listens on **port 5000** by default (`app.run(debug=False, port=5000)` in `app.py`).

---

## AI Advisor (Ollama)

Chat uses **`POST /chat`**, which calls Ollama’s HTTP API (no paid cloud API keys).

### Install and start Ollama

1. Install Ollama from [ollama.com](https://ollama.com).
2. Pull the default model (or choose another and set `OLLAMA_MODEL`):

   ```bash
   ollama pull llama3.1:8b
   ```

3. Ensure Ollama is running (the desktop app keeps the daemon alive). Default API URL is **`http://localhost:11434`**.

### Check readiness

With Flask running:

```bash
curl -s http://127.0.0.1:5000/health/ai | python3 -m json.tool
```

The AI Advisor tab shows the same status. If Ollama is off or the model is missing, chat explains what to fix.

# Setup Guide for Windows

## Step 1 — Install Dependencies

Open PowerShell in the project folder and run:

```powershell
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
pip install --upgrade pip
pip install --only-binary=:all: fastapi uvicorn sqlalchemy aiosqlite httpx beautifulsoup4 google-generativeai streamlit plotly pandas requests python-dotenv pydantic reportlab python-multipart lxml
```

## Step 2 — Add Your Gemini API Key

```powershell
copy .env.example .env
notepad .env
```

Replace `paste_your_gemini_key_here` with your actual key.
Get free key at: https://aistudio.google.com/app/apikey

## Step 3 — Start Backend (Terminal 1)

```powershell
venv\Scripts\activate
uvicorn backend.main:app --reload --port 8000
```

Wait for: `✅ Database tables initialized`

## Step 4 — Start Frontend (Terminal 2, new window)

```powershell
cd path\to\dark-pattern-detector
venv\Scripts\activate
streamlit run frontend\app.py
```

## Step 5 — Open Browser

- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs

## Step 6 — Load Sample Data (Optional, Terminal 3)

```powershell
venv\Scripts\activate
python database\seed.py
```

## Troubleshooting

**uvicorn not found:** Run `pip install uvicorn` then try again

**sqlalchemy error:** Run `pip install --upgrade sqlalchemy`

**Port in use:** Change `--port 8000` to `--port 8001`
Then update API_BASE in frontend/app.py line 8 to `http://localhost:8001/api`

**Sites return 403:** Use the Paste Content tab instead — paste text from any website

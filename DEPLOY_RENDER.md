# 🚀 Deploy on Render — Step by Step

## Total Time: ~10 minutes

---

## Step 1 — Push to GitHub

```bash
# In your project folder
git init
git add .
git commit -m "Dark Pattern Detector v1.0"

# Create repo at github.com → New Repository → name: dark-pattern-detector
git remote add origin https://github.com/YOUR_USERNAME/dark-pattern-detector.git
git push -u origin main
```

---

## Step 2 — Create PostgreSQL Database on Render

1. Go to **render.com** → Sign up (free)
2. Click **New +** → **PostgreSQL**
3. Name: `dark-pattern-db`
4. Plan: **Free**
5. Click **Create Database**
6. Copy the **Internal Database URL** — you'll need this soon

---

## Step 3 — Deploy FastAPI Backend

1. Click **New +** → **Web Service**
2. Connect GitHub → Select `dark-pattern-detector` repo
3. Fill in settings:
   ```
   Name:           dark-pattern-backend
   Runtime:        Python 3
   Build Command:  pip install -r requirements.txt
   Start Command:  uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   Plan:           Free
   ```
4. Click **Add Environment Variable**:
   ```
   Key:   GEMINI_API_KEY
   Value: your_gemini_api_key_here
   ```
5. Click **Add Environment Variable** again:
   ```
   Key:   DATABASE_URL
   Value: (paste the Internal Database URL from Step 2)
   ```
6. Click **Create Web Service**
7. Wait ~3 minutes for deployment
8. Copy your backend URL: `https://dark-pattern-backend.onrender.com`

---

## Step 4 — Deploy Streamlit Frontend

1. Click **New +** → **Web Service**
2. Connect same GitHub repo
3. Fill in settings:
   ```
   Name:           dark-pattern-frontend
   Runtime:        Python 3
   Build Command:  pip install -r requirements.txt
   Start Command:  streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
   Plan:           Free
   ```
4. Add Environment Variable:
   ```
   Key:   API_BASE
   Value: https://dark-pattern-backend.onrender.com/api
   ```
   (Use YOUR actual backend URL from Step 3)
5. Click **Create Web Service**
6. Wait ~3 minutes
7. Your live URL: `https://dark-pattern-frontend.onrender.com`

---

## Step 5 — Load Sample Data (Optional)

In the Render backend service dashboard:
1. Click **Shell** tab
2. Run:
   ```bash
   python database/seed.py
   ```

---

## Step 6 — Verify Everything Works

Open your frontend URL and test:
- Paste Content tab → paste sample text → should analyze
- Analytics page → should show charts
- Pattern Database → should show leaderboard

---

## Add to Your Resume

```
Dark Pattern Detector
Live: https://dark-pattern-frontend.onrender.com
GitHub: https://github.com/YOUR_USERNAME/dark-pattern-detector
```

---

## Troubleshooting

**Backend shows "Application failed to start"**
→ Check logs in Render dashboard → likely missing env variable

**Frontend shows "Cannot connect to API"**
→ Make sure API_BASE points to your actual backend URL (not localhost)

**Database errors**
→ Make sure DATABASE_URL is the Internal Database URL, not External

**Free tier sleeps after 15 mins inactivity**
→ First request after sleep takes ~30 seconds to wake up
→ This is normal for Render free tier

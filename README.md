# ⚡ FITAI - AI Personal Trainer
### Powered by Zaya Group of Company

A full-stack AI Personal Trainer web application 
using Computer Vision, Deep Learning, and 
Generative AI to provide real-time workout coaching.

## ✨ Features
- Real-time pose detection using MediaPipe
- Rep counting with UP/DOWN state machine  
- Form scoring 0-100 with voice feedback
- JWT authentication and user sessions
- Cyberpunk dark navy + neon blue UI
- Session history dashboard with Chart.js
- FastAPI WebSocket streaming at 30fps
- 5 exercises: Bicep Curl, Squat, Push Up,
  Shoulder Press, Lunge

## 🧠 Tech Stack
- Frontend: HTML5, CSS3, JavaScript
- Backend: FastAPI, Python 3.11
- AI/CV: MediaPipe, OpenCV, NumPy
- Auth: JWT, Passlib, bcrypt
- Database: SQLite, SQLAlchemy
- Streaming: WebSocket, Uvicorn

## 🚀 Run Locally

### Backend
cd ai-personal-trainer-backend
python -m venv .venv311
.venv311\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

### Frontend
cd C:\aipersonaltrainer
python serve.py
Open: http://localhost:3000

## 👥 Team - Zaya Group of Company
- Rohith — Founder & CTO
- Rahul Kumar Yadav — Co-Founder & CEO
- Sujan Khatri — Co-Founder & Network Manager
- Samagya Baral — Co-Founder & Graphic Designer

## 🚀 Deploy (Vercel frontend + Render backend)

The frontend is static and talks to a **separate backend**. Auth fails with
"Connection error" if the frontend still points at `localhost`. There are NO
hardcoded backend URLs — the base URL is injected at build time.

### 1. Deploy the backend to Render
- New → Web Service → connect this repo.
- Set **Root Directory**: `ai-personal-trainer-backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- (Or just commit `render.yaml` — Render auto-detects it.)
- Add env vars (Render can auto-generate `JWT_SECRET`):
  `JWT_SECRET`, `JWT_ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=60`,
  `DATABASE_URL=sqlite:///./app.db`, `CORS_ORIGINS=*`, `HOST=0.0.0.0`.
- Copy the deployed URL, e.g. `https://ai-personal-trainer-backend.onrender.com`.

### 2. Point the Vercel frontend at the backend
- In Vercel project settings set **Build Command**: `node build.js`
  (Output Directory: `.`). `build.js` writes `config.generated.js` from the
  `FITAI_API_URL` env var.
- Add Vercel env var: `FITAI_API_URL` = your Render backend URL
  (e.g. `https://ai-personal-trainer-backend.onrender.com`).
- Redeploy. The frontend now calls the deployed backend — no code edits needed.

### 3. Local development
- Backend: `cd ai-personal-trainer-backend && uvicorn app.main:app --port 8000`
- Frontend: `python serve.py` → http://localhost:3000
- Locally `config.generated.js` falls back to `http://127.0.0.1:8000`.

## 📄 License
MIT License - Zaya Group of Company 2026

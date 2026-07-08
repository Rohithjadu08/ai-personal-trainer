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

## 📄 License
MIT License - Zaya Group of Company 2026

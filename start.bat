@echo off
echo Starting AI Personal Trainer...
start "Backend" cmd /k "cd ai-personal-trainer-backend && .venv311\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3
start "Frontend" cmd /k "cd C:\aipersonaltrainer && python serve.py"
timeout /t 2
start chrome http://localhost:3000

echo Done! Both servers started.
